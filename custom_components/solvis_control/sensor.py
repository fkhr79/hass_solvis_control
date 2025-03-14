"""
Solvis Sensors.

Version: 1.2.0-alpha11
"""

import logging
import re
from decimal import Decimal

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_HOST, CONF_NAME, DATA_COORDINATOR, DOMAIN, DEVICE_VERSION, REGISTERS

from .coordinator import SolvisModbusCoordinator
from .utils.helpers import generate_device_info, conf_options_map

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis sensor entities."""

    coordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    if not host:
        _LOGGER.error("Device has no valid address")
        return  # Exit if no host is configured

    # Generate device info
    device_info = generate_device_info(entry, host, name)

    # Add sensor entities
    sensors = []
    active_entity_ids = set()
    for register in REGISTERS:
        if register.input_type == 0:  # Check if the register represents a sensor
            # Check if the sensor is enabled based on configuration options
            if isinstance(register.conf_option, tuple):
                if not all(entry.data.get(conf_options_map[option]) for option in register.conf_option):
                    continue
            else:
                if register.conf_option == 0:
                    pass
                elif not entry.data.get(conf_options_map.get(register.conf_option)):
                    continue

            _LOGGER.debug(f"Supported version: {entry.data.get(DEVICE_VERSION)} / Register version: {register.supported_version}")
            if int(entry.data.get(DEVICE_VERSION)) == 1 and int(register.supported_version) == 2:
                _LOGGER.debug(f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}")
                continue
            if int(entry.data.get(DEVICE_VERSION)) == 2 and int(register.supported_version) == 1:
                _LOGGER.debug(f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}")
                continue

            entity = SolvisSensor(
                coordinator,
                device_info,
                host,
                register.name,
                register.unit,
                register.device_class,
                register.state_class,
                register.entity_category,
                register.enabled_by_default,
                register.data_processing,
                register.poll_rate,
                register.supported_version,
                register.address,
                register.suggested_precision,
            )
            sensors.append(entity)
            active_entity_ids.add(entity.unique_id)
            _LOGGER.debug(f"Erstellte unique_id: {entity.unique_id}")

    try:
        entity_registry = er.async_get(hass)
        existing_entity_ids = {entity_entry.unique_id for entity_entry in entity_registry.entities.values() if entity_entry.config_entry_id == entry.entry_id}
        entities_to_remove = existing_entity_ids - active_entity_ids  # Set difference
        _LOGGER.debug(f"Vorhandene unique_ids: {existing_entity_ids}")
        _LOGGER.debug(f"Aktive unique_ids: {active_entity_ids}")
        _LOGGER.debug(f"Zu entfernende unique_ids: {entities_to_remove}")
        for entity_id in entities_to_remove:
            entity_entry = entity_registry.entities.get(entity_id)  # get the entity_entry by id
            if entity_entry:  # check if the entity_entry exists
                entity_registry.async_remove(entity_entry.entity_id)  # remove by entity_id
                _LOGGER.debug(f"Removed old entity: {entity_entry.entity_id}")

    except Exception as e:
        _LOGGER.error("Fehler beim Entfernen alter Entities", exc_info=True)  # include stacktrace in log

    async_add_entities(sensors)


class SolvisSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address: int,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
        modbus_address: int | None = None,
        suggested_precision: int | None = 1,
    ):
        """Initialize the Solvis sensor."""
        super().__init__(coordinator)

        self._address = address
        self.modbus_address = modbus_address
        self._response_key = name
        self._attr_native_value = None
        self.entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
        self.entity_registry_enabled_default = enabled_by_default
        self.device_class = device_class
        self.state_class = state_class
        self.native_unit_of_measurement = unit_of_measurement
        self._attr_available = False
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        cleaned_name = re.sub(r"[^A-Za-z0-9_-]+", "_", name or "unknown")
        self.unique_id = f"{modbus_address}_{supported_version}_{cleaned_name}"
        self.translation_key = name
        self.data_processing = data_processing
        self.poll_rate = poll_rate
        self.suggested_display_precision = suggested_precision

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        register = next((r for r in REGISTERS if r.name == self._response_key), None)

        # skip slow poll registers not being updated
        if register and (register.poll_rate == 1 and register.poll_time != self.coordinator.poll_rate_slow):
            _LOGGER.debug(f"Skipping update for {self._response_key} (slow polling active, remaining wait time: {register.poll_time}s)")
            return
        elif register and (register.poll_rate == 0 and register.poll_time != self.coordinator.poll_rate_default):
            _LOGGER.debug(f"Skipping update for {self._response_key} (standard polling active, remaining wait time: {register.poll_time}s)")
            return

        if self.coordinator.data is None:
            _LOGGER.warning(f"Data from coordinator for {self._response_key} is None. Skipping update")
            return

        if not self.coordinator.data or not isinstance(self.coordinator.data, dict):
            _LOGGER.error(f"Invalid data from coordinator: {type(self.coordinator.data)} expected")
            self._attr_available = False
            self.async_write_ha_state()
            return

        response_data = self.coordinator.data.get(self._response_key)

        if response_data is None:
            _LOGGER.warning(f"No data available for {self._response_key}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        # Validate the data type received from the coordinator
        if not isinstance(response_data, (int, float, complex, Decimal)):
            _LOGGER.error(f"Invalid response data type for {self._response_key} from coordinator. {response_data} has type {type(response_data)}")
            self._attr_available = False
            self.async_write_ha_state()
            return

        if response_data == -300:
            _LOGGER.warning(f"The coordinator failed to fetch data for entity: {self._response_key}")
            self._attr_available = False
            self.async_write_ha_state()
            return
        self._attr_available = True
        self._attr_extra_state_attributes = {"unprocessed_value": response_data}
        match self.data_processing:
            case 1:  # Version
                if len(str(response_data)) == 5:
                    response_data = str(response_data)
                    self._attr_native_value = f"{response_data[0]}.{response_data[1:3]}.{response_data[3:5]}"
                    if self._address in (32770, 32771):
                        # Hole den Device-Registry
                        device_registry = dr.async_get(self.hass)

                        # Aktualisiere Geräteinformationen
                        device = device_registry.async_get_device(self.device_info.identifiers)
                        if device is not None:
                            if self._address == 32770:
                                device_registry.async_update_device(
                                    device.id,
                                    sw_version=self._attr_native_value,
                                )
                                if self._attr_native_value != "3.20.06":
                                    ir.async_create_issue(
                                        self.hass,
                                        DOMAIN,
                                        "software_update",
                                        is_fixable=False,
                                        severity=ir.IssueSeverity.WARNING,
                                        translation_key="software_update",
                                    )
                            elif self._address == 32771:
                                device_registry.async_update_device(
                                    device.id,
                                    hw_version=self._attr_native_value,
                                )
                else:
                    _LOGGER.warning("Couldn't process version string to Version.")
                    self._attr_native_value = response_data
            case 2:  # https://github.com/LarsK1/hass_solvis_control/issues/58#issuecomment-2496245943
                if response_data != 0:
                    self._attr_native_value = (1 / (response_data / 60)) * 1000 / 2 / 42
                else:
                    _LOGGER.warning(f"Division by zero for {self._response_key} with value {response_data}")
                    self._attr_native_value = 0
            case 3:
                if response_data != 0:
                    self._attr_native_value = (1 / (response_data / 60)) * 1000 / 42
                else:
                    _LOGGER.warning(f"Division by zero for {self._response_key} with value {response_data}")
                    self._attr_native_value = 0
            case _:
                self._attr_native_value = response_data  # Update the sensor value
        self.async_write_ha_state()
