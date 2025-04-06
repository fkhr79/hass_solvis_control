"""
Helper file for various config modules

Version: v2.0.0-beta.1
"""

import logging
import re

from decimal import Decimal
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.entity_registry import async_resolve_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from scapy.all import ARP, Ether, srp
from pymodbus.exceptions import ConnectionException, ModbusException
import pymodbus.client as ModbusClient

from custom_components.solvis_control.const import (
    CONF_NAME,
    PORT,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    MANUFACTURER,
    DATA_COORDINATOR,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    REGISTERS,
)

_LOGGER = logging.getLogger(__name__)


def generate_device_info(entry: ConfigEntry, host: str, name: str) -> DeviceInfo:
    """Generate device info."""
    _LOGGER.debug(f"Generating device info for {host}")
    _LOGGER.debug(f"Entry data: {entry.data}")

    device_version_str = entry.data.get(DEVICE_VERSION, "")
    try:
        device_version = int(device_version_str)
    except (ValueError, TypeError):
        device_version = None

    model = {
        1: "Solvis Control 3",
        2: "Solvis Control 2",
    }.get(device_version, "Solvis Control (unbekannt)")

    info = {
        "identifiers": {(DOMAIN, host)},
        "name": name,
        "manufacturer": MANUFACTURER,
        "model": model,
    }

    if "VERSIONSC" in entry.data:
        info["sw_version"] = entry.data["VERSIONSC"]
    if "VERSIONNBG" in entry.data:
        info["hw_version"] = entry.data["VERSIONNBG"]

    return DeviceInfo(**info)


async def fetch_modbus_value(register: int, register_type: int, host: str, port: int, datatype="INT16", order="big") -> int | None:
    """Fetch a value from the Modbus device."""
    modbussocket = None
    try:
        _LOGGER.debug(f"[fetch_modbus_value] Creating Modbus client for {host}:{port}")

        modbussocket = ModbusClient.AsyncModbusTcpClient(host=host, port=port)

        if modbussocket is None:
            raise ConnectionException(f"[fetch_modbus_value] Failed to initialize Modbus client for {host}:{port}")

        _LOGGER.debug(f"[fetch_modbus_value] Modbus client created: {modbussocket}")
        connected = await modbussocket.connect()

        if not connected:
            raise ConnectionException(f"[fetch_modbus_value] Failed to connect to Modbus device at {host}:{port}")

        _LOGGER.debug("[fetch_modbus_value] Connected to Modbus for Solvis")

        if register_type == 1:
            data = await modbussocket.read_input_registers(address=register, count=1)
        else:
            data = await modbussocket.read_holding_registers(address=register, count=1)

        if not data or not hasattr(data, "registers") or not data.registers:
            raise ModbusException(f"[fetch_modbus_value] Invalid response from Modbus for register {register} at {host}:{port}")

        result = modbussocket.convert_from_registers(
            data.registers,
            data_type=modbussocket.DATATYPE.INT16,
            word_order=order,
        )

        return result

    finally:
        if modbussocket:
            try:
                _LOGGER.debug(f"[fetch_modbus_value] Closing Modbus connection: {modbussocket}")
                modbussocket.close()
                _LOGGER.debug("[fetch_modbus_value] Modbus connection closed")
            except Exception as e:
                _LOGGER.warning(f"[fetch_modbus_value] Error while closing Modbus connection: {e}")
        else:
            _LOGGER.warning("[fetch_modbus_value] Modbus client was None before closing!")


conf_options_map = {
    1: CONF_OPTION_1,
    2: CONF_OPTION_2,
    3: CONF_OPTION_3,
    4: CONF_OPTION_4,
    5: CONF_OPTION_5,
    6: CONF_OPTION_6,
    7: CONF_OPTION_7,
    8: CONF_OPTION_8,
}
conf_options_map_coordinator = {
    1: "option_hkr2",
    2: "option_hkr3",
    3: "option_solar",
    4: "option_heatpump",
    5: "option_heatmeter",
    6: "option_room_temperature_sensor",
    7: "option_write_temperature_sensor",
    8: "option_pv2heat",
}


def get_mac(ip):
    arp_request = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")  # Broadcast-Adresse
    packet = ether / arp_request

    responses = srp(packet, timeout=3, verbose=0)
    if not responses or len(responses) == 0:
        return None

    result = responses[0]

    if not result or len(result) == 0 or len(result[0]) < 2 or result[0][1] is None:
        return None

    return result[0][1].hwsrc


async def remove_old_entities(hass: HomeAssistant, config_entry_id: str, active_entity_ids: set) -> None:
    """Remove entities from the registry that are not in active_entity_ids."""

    entity_registry = er.async_get(hass)

    existing_entity_ids = {entity_entry.unique_id for entity_entry in entity_registry.entities.values() if entity_entry.config_entry_id == config_entry_id}

    entities_to_remove = existing_entity_ids - active_entity_ids

    _LOGGER.debug(f"Existing unique_ids: {existing_entity_ids}")
    _LOGGER.debug(f"Active unique_ids: {active_entity_ids}")
    _LOGGER.debug(f"Existing but not active unique_ids to remove: {entities_to_remove}")

    for unique_id in entities_to_remove:
        # entities_to_remove contains unique_id's and not entity_id's,
        # but we need entity-id's here to get the entity_entries
        entity_id = async_resolve_entity_id(entity_registry, unique_id)  # resolve unique_id to entity_id
        entity_entry = entity_registry.entities.get(entity_id)  # get the entity_entry by entity_id
        if entity_entry:  # check if the entity_entry exists
            entity_registry.async_remove(entity_entry.entity_id)  # remove by entity_id
            _LOGGER.debug(f"Removed old entity: {unique_id} (entity_id: {entity_entry.entity_id})")


def generate_unique_id(modbus_address: int, supported_version: int, name: str) -> str:
    """Generate a unique ID by cleaning the given name."""
    cleaned_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")
    if cleaned_name:
        return f"{modbus_address}_{supported_version}_{cleaned_name}"
    return f"{modbus_address}_{supported_version}"  # if name consists of special chars only


async def write_modbus_value(modbus, address: int, value: int, response_key: str = None) -> bool:
    """Write a value to a Modbus register."""
    try:
        _LOGGER.debug(f"[write_modbus_value] Using Modbus client: {modbus}")
        connected = await modbus.connect()
        if not connected:
            _LOGGER.error(f"[write_modbus_value] Failed to connect to Modbus device")
            return False

        _LOGGER.debug("[write_modbus_value] Connected to Modbus device")
        response = await modbus.write_register(address, value, slave=1)
        if response.isError():
            _LOGGER.error(f"[write_modbus_value] Modbus error response for register {address}: {response}")
            return False

        _LOGGER.debug(f"[write_modbus_value] Successfully wrote value {value} to register {address}")
        return True

    except ConnectionException as e:
        _LOGGER.error(f"[write_modbus_value] Modbus connection error: {e}")
        return False
    except ModbusException as e:
        _LOGGER.error(f"[write_modbus_value] Modbus error: {e}")
        return False
    except Exception as e:
        _LOGGER.error(f"[write_modbus_value] Unexpected error: {e}")
        return False
    finally:
        try:
            _LOGGER.debug("[write_modbus_value] Closing Modbus connection")
            modbus.close()
            _LOGGER.debug("[write_modbus_value] Modbus connection closed")
        except Exception as e:
            _LOGGER.warning(f"[write_modbus_value] Error while closing Modbus connection: {e}")


def process_coordinator_data(coordinator_data: dict, response_key: str):
    """
    Process data from the coordinator for a given response key.

    Returns a tuple (available, value, extra_state_attributes):
    - available: Boolean indicating if data is valid.
    - value: The raw value from the coordinator.
    - extra_state_attributes: Additional attributes (e.g. raw_value).

    If the data is not valid, available is False.
    If response_key is not present, None is returned.
    """
    if coordinator_data is None:
        _LOGGER.warning("Data from coordinator is None. Skipping update")
        return False, None, {}

    if not isinstance(coordinator_data, dict):
        _LOGGER.warning("Invalid data from coordinator")
        return False, None, {}

    if response_key not in coordinator_data:
        _LOGGER.debug(f"[{response_key}] Skipping update: no data available in coordinator. Skipped update!?")
        return None, None, {}

    response_data = coordinator_data.get(response_key)

    if response_data is None:
        _LOGGER.warning(f"[{response_key}] No data available: response data is None.")
        return False, None, {}

    if not isinstance(response_data, (int, float, Decimal)) or isinstance(response_data, complex):  # complex numbers are not valid
        _LOGGER.warning(f"[{response_key}] Invalid response data type from coordinator: {response_data} has type {type(response_data)}")
        return False, None, {}

    if response_data == -300:
        _LOGGER.warning(f"[{response_key}] The coordinator failed to fetch data.")
        return False, None, {}

    extra_state_attributes = {"raw_value": response_data}

    return True, response_data, extra_state_attributes


def should_skip_register(entry_data: dict, register) -> bool:
    """
    Determine whether a register should be skipped based on the config-options and the supported version.
    Returns True, if the register should be skipped, else False.
    """
    # check config-options
    if isinstance(register.conf_option, tuple):  # tuple
        if not all(entry_data.get(conf_options_map[option]) for option in register.conf_option):
            _LOGGER.debug(f"[{register.name} | {register.address}] Skipping register because not all conf_options are enabled: {register.conf_option}")
            return True

    else:  # single value
        if register.conf_option == 0:
            _LOGGER.debug(f"[{register.name} | {register.address}] conf_option {register.conf_option} allows processing. Continuing...")
            pass
        elif not entry_data.get(conf_options_map.get(register.conf_option)):
            _LOGGER.debug(f"[{register.name} | {register.address}] Skipping register because conf_option {register.conf_option} is not enabled.")
            return True

    # check supported version
    device_version_str = entry_data.get(DEVICE_VERSION, "")
    _LOGGER.debug(f"[{register.name} | {register.address}] Register version: {register.supported_version} / Device version: {device_version_str}")
    try:
        device_version = int(device_version_str)
    except (ValueError, TypeError):
        device_version = None

    if device_version == 1 and int(register.supported_version) == 2:
        _LOGGER.debug(f"[{register.name} | {register.address}] Skipping SC2 entity for SC3 device.")
        return True

    if device_version == 2 and int(register.supported_version) == 1:
        _LOGGER.debug(f"[{register.name} | {register.address}] Skipping SC3 entity for SC2 device.")
        return True

    return False


async def async_setup_solvis_entities(
    hass,
    entry,
    async_add_entities: AddEntitiesCallback,
    entity_cls,
    input_type: int,
):
    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if host is None:
        _LOGGER.error("Device has no address")
        return

    device_info = generate_device_info(entry, host, name)
    entities = []
    active_entity_ids = set()

    for register in REGISTERS:
        if register.input_type != input_type:
            continue

        if should_skip_register(entry.data, register):
            continue

        kwargs = {
            "coordinator": coordinator,
            "device_info": device_info,
            "host": host,
            "name": register.name,
            "enabled_by_default": register.enabled_by_default,
            "modbus_address": register.address,
            "data_processing": register.data_processing,
            "poll_rate": register.poll_rate,
            "supported_version": register.supported_version,
        }

        if entity_cls.__name__ == "SolvisSelect":
            kwargs["options"] = register.options

        if entity_cls.__name__ == "SolvisSensor":
            kwargs["unit_of_measurement"] = register.unit
            kwargs["device_class"] = register.device_class
            kwargs["state_class"] = register.state_class
            kwargs["entity_category"] = register.entity_category
            kwargs["suggested_precision"] = register.suggested_precision

        if entity_cls.__name__ == "SolvisNumber":
            kwargs["unit_of_measurement"] = register.unit
            kwargs["device_class"] = register.device_class
            kwargs["state_class"] = register.state_class
            kwargs["range_data"] = register.range_data
            kwargs["step_size"] = register.step_size
            kwargs["multiplier"] = register.multiplier

        if entity_cls.__name__ == "SolvisBinarySensor":
            kwargs["device_class"] = register.device_class
            kwargs["state_class"] = register.state_class
            kwargs["entity_category"] = register.entity_category

        entity = entity_cls(**kwargs)
        entities.append(entity)
        active_entity_ids.add(entity.unique_id)
        _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        await remove_old_entities(hass, entry.entry_id, active_entity_ids)
    except Exception as e:
        _LOGGER.error(f"Error removing old entities: {e}", exc_info=True)

    async_add_entities(entities)
    _LOGGER.info(f"Successfully added {len(entities)} entities")
