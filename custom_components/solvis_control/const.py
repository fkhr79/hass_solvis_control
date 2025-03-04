"""
Definition of constants for the Solvis Control integration.

Version: 1.2.0-alpha11
"""

from dataclasses import dataclass
from enum import IntEnum

DOMAIN = "solvis_control"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"

DEVICE_VERSION = "device_version"
POLL_RATE_DEFAULT = "poll_rate_default"
POLL_RATE_SLOW = "poll_rate_slow"
POLL_RATE_HIGH = "poll_rate_high"

# Option attributes to make certain values configurable
CONF_OPTION_1 = "HKR2"  # HKR 2
CONF_OPTION_2 = "HKR3"  # HKR 3
CONF_OPTION_3 = "solar collector"  # Solar collector
CONF_OPTION_4 = "heat pump"  # heat pump
CONF_OPTION_5 = "heat_meter"  # heat meter
CONF_OPTION_6 = "room_temperature_sensor"  # room temperature sensor
CONF_OPTION_7 = "write_room_temperature_sensor"  # write room temperature sensor
CONF_OPTION_8 = "pv2heat"  # pv2heat


DATA_COORDINATOR = "coordinator"
MANUFACTURER = "Solvis"
PORT = 502


class SolvisDeviceVersion(IntEnum):
    """Enum for device versions."""

    SC2 = 2
    SC3 = 1


@dataclass
class ModbusFieldConfig:
    name: str
    address: int
    unit: str | None
    device_class: str | None
    state_class: str | None
    multiplier: float = 0.1
    absolute_value: bool = False

    register: int = 1
    # 1 = INPUT, 2 = HOLDING

    entity_category: str = None

    enabled_by_default: bool = True
    # Option to disable entitiy by default

    edit: bool = False
    # Allows entities to be set to editable

    range_data: tuple = None
    # Assigns a range for number entities input_type = 2

    step_size: float = None

    options: tuple = None
    # Assigns possible potions for select entities input_type = 1

    conf_option: int | tuple = 0
    # Assign CONF_OPTION to entities

    input_type: int = 0
    # Configuration for which state class a register belongs to
    # Possibilities:
    # sensor (0), select (1), number (2), switch (3), binary_sensor (4)

    data_processing: int = 0
    # Option to further process data
    # 0: no processing
    # 1: version string split for version sc & version nbg, registers 32770 & 32771
    # 2: special conversion for S18 on SC2, register 33041
    # 3: special conversion for S17 on SC2, register 33040
    # 4: special conversion for digin_error, register 33045

    supported_version: int = 0
    # Supported Version
    # 0: SC2 & SC3, 1: SC3, 2: SC2

    poll_rate: int = 0
    # 0: default, 1: slow, 2: high

    poll_time: int = 0
    # Internal variable to store the value of the last poll
    # Don't change

    byte_swap: int = 0
    # endianness (byte_order)
    # 0: big endian (default), 1: little endian

    suggested_precision: int | None = 1


# Naming Scheme
# [heating_circuit]_[parameter]_[solvis_name]
# [heating_circuit] = hkr1 / hkr2 / hkr3 / empty, if applicable
# [parameter] = description & name of sensor, each word seperated with an underscore [hot_water_temp]
# [solvis_name] = if applicable add Solvis own Name of entity, letters in lowercase (due to hass), numbers without a leading zero. [s12, o1]
# Example: hkr1_flow_water_temp_s12

REGISTERS = [
    ModbusFieldConfig(  # Number of HKR
        name="hkr_number",
        address=2,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        multiplier=1,
        suggested_precision=0,
        poll_rate=1,
    ),
    ModbusFieldConfig(  # Analog Out 1 Status (the status of Analog Out O1 = burner_modulation_O1)
        name="burner_modulation_o1_status",
        address=3840,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        multiplier=1,  # <-- even if the comma is not correct it prevents lint-errors: otherwise black wants to reformat and remove the linebreaks
    ),
    ModbusFieldConfig(  # Analog Out 2 Status
        name="solar_pump_primary_o2_status",
        address=3845,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        conf_option=3,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Analog Out 3 Status
        name="solar_pump_secondary_o3_status",
        address=3850,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        conf_option=3,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Analog Out 4 Status
        name="heatpump_charging_pump_o4_status",
        address=3855,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        conf_option=4,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Analog Out 5 Status
        name="warm_water_pump_o5_status",
        address=3860,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Analog Out 6 Status
        name="analog_out_o6_status",
        address=3865,
        enabled_by_default=False,
        device_class=None,
        unit=None,
        state_class=None,
        entity_category="diagnostic",
        poll_time=0,
        multiplier=1,
    ),
    ModbusFieldConfig(  # To be verified: Wärmemenge PV2Heat - see #54, #173
        name="pv2heat_energy",
        address=33539,
        unit="kWh",
        device_class="energy",
        state_class="total_increasing",
        poll_time=0,
        multiplier=10,  # Solvis doc states "1"
        suggested_precision=0,
        conf_option=8,
    ),
    ModbusFieldConfig(  # Wärmemenge Solaranlage - see #173
        name="solar_energy",
        address=33536,
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
        absolute_value=True,
        poll_time=0,
        multiplier=10,
        suggested_precision=0,
        poll_rate=1,
        conf_option=3,
    ),
    ModbusFieldConfig(  # Wärmemenge Wärmeerzeuger 1 / Wärmepumpe - see #115, #173
        name="heatpump_energy_thermal",
        address=33537,
        unit="kWh",
        device_class="energy",
        state_class="total_increasing",
        multiplier=10,
        absolute_value=True,
        poll_rate=1,
        poll_time=0,
        suggested_precision=0,
        conf_option=0,  # can possibly be changed to 4
    ),
    ModbusFieldConfig(  # Wärmemenge Wärmeerzeuger 2 / Brenner - see #116, #173
        name="burner_energy_thermal",
        address=33538,
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
        absolute_value=True,
        poll_time=0,
        multiplier=10,
        suggested_precision=0,
        poll_rate=1,
    ),
    ModbusFieldConfig(  # Wärmemenge Warmwasser - see #173
        name="warm_water_energy",
        address=33540,
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
        absolute_value=True,
        poll_time=0,
        multiplier=10,  # Solvis doc states "1"
        suggested_precision=0,
        poll_rate=1,
    ),
    ModbusFieldConfig(  # Wärmemenge Heizkreise - see #173
        name="heating_circuits_energy",
        address=33541,
        device_class="energy",
        unit="kWh",
        state_class="total_increasing",
        absolute_value=True,
        poll_time=0,
        multiplier=10,
        suggested_precision=0,
        poll_rate=1,
    ),
    ModbusFieldConfig(  # aktuelle Leistung Wärmeerzeuger 2 (thermisch)
        name="heat_generator_2_power_thermal",
        address=33546,
        unit="kW",
        device_class="power",
        state_class="measurement",
        conf_option=0,  # might be changed later
        poll_time=0,
        poll_rate=2,
    ),
    ModbusFieldConfig(  # aktuelle Leistung Wärmeerzeuger 2 (elektrisch)
        name="heat_generator_2_power_electric",
        address=33547,
        unit="kW",
        device_class="power",
        state_class="measurement",
        conf_option=0,
        poll_time=0,
        poll_rate=2,
    ),
    ModbusFieldConfig(  # aktuelle Leistung Warmwasser (thermisch)
        name="warm_water_power",
        address=33549,
        unit="kW",
        device_class="power",
        state_class="measurement",
        multiplier=1,
        conf_option=0,
        poll_time=0,
        poll_rate=2,
    ),
    ModbusFieldConfig(  # Laufzeit Solarpumpe 1
        name="solar_pump_primary_runtime",
        address=33552,
        unit="h",
        multiplier=1,
        device_class=None,
        state_class="measurement",
        absolute_value=True,
        conf_option=3,
        poll_time=0,
        poll_rate=1,
        suggested_precision=0,
    ),
    ModbusFieldConfig(  # Laufzeit Solarpumpe 2
        name="solar_pump_secondary_runtime",
        address=33553,
        unit="h",
        multiplier=1,
        device_class=None,
        state_class="measurement",
        absolute_value=True,
        conf_option=3,
        poll_time=0,
        poll_rate=1,
        suggested_precision=0,
    ),
    ModbusFieldConfig(  # Meldungen Anzahl
        name="messages_number",
        address=33792,
        unit=None,
        device_class=None,
        state_class=None,
        entity_category="diagnostic",
        multiplier=1,
        conf_option=0,
        poll_time=0,
        poll_rate=1,
    ),
    ModbusFieldConfig(  # Außentemperatur
        name="outdoor_air_temp_s10",
        address=33033,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(
        name="solar_collector_temp_s8",
        address=33031,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Zirkulationstemperatur
        name="circulation_temp_s11",
        address=33034,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        multiplier=0.1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Vorlauftemperatur HKR1
        name="hkr1_flow_water_temp_s12",
        address=33035,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(  # Vorlauftemperatur HKR2
        name="hkr2_flow_water_temp_s13",
        address=33036,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Vorlauftemperatur HKR3
        name="hkr3_flow_water_temp_s14",
        address=33039,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=False,
        conf_option=2,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Warmwassertemperatur
        name="warm_water_temp_s2",
        address=33025,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(  # Warmwasser Nachheizung
        name="warm_water_reheat",
        address=2322,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        input_type=3,
        register=2,
        poll_time=0,
    ),
    ModbusFieldConfig(
        name="solar_flow_primary_temp_s7",
        address=33030,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
        poll_time=0,
    ),
    ModbusFieldConfig(
        name="solar_return_secondary_temp_s6",
        address=33029,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
        poll_time=0,
    ),
    ModbusFieldConfig(
        name="solar_flow_secondary_temp_s5",
        address=33028,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Speicherreferenztemperatur
        name="storage_reference_temp_s3",
        address=33026,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur unten
        name="heating_buffer_lower_temp_s9",
        address=33032,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        absolute_value=True,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur oben
        name="heating_buffer_upper_temp_s4",
        address=33027,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        absolute_value=True,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Warmwasserpuffer
        name="warm_water_buffer_temp_s1",
        address=33024,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(  # Kaltwassertemperatur
        name="cold_water_temp_s15",
        address=33038,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        poll_time=0,
    ),
    ModbusFieldConfig(  # A01 Pumpe Zirkulation
        name="circulation_pump_a1",
        address=33280,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A02 Wärmepumpe Ladepumpe
        name="heatpump_charging_pump_a2",
        address=33281,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        poll_time=0,
        input_type=4,
        conf_option=4,
    ),
    ModbusFieldConfig(  # WP hybrid Warmwasser Bivalenztemperatur
        name="heatpump_hybrid_warm_water_bivalence_temp",
        address=838,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(-20, 40),
        poll_time=0,
        poll_rate=1,
        conf_option=4,
    ),
    ModbusFieldConfig(  # WP hybrid Heizung Bivalenztemperatur
        name="heatpump_hybrid_heating_bivalence_temp",
        address=839,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(-20, 20),
        poll_time=0,
        poll_rate=1,
        conf_option=4,
    ),
    ModbusFieldConfig(  # Warmwasser Solltemperatur
        name="warm_water_target_temp",
        address=2305,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(10, 65),
        poll_time=0,
    ),
    ModbusFieldConfig(  # A03 Pumpe HKR 1
        name="hkr1_pump_a3",
        address=33282,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A04 Pumpe HKR 2
        name="hkr2_pump_a4",
        address=33283,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=1,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A05 Pumpe HKR 3
        name="hkr3_pump_a5",
        address=33284,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=2,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A06 HKR3 Mischer auf
        name="hkr3_mixer_heating_circuit_open_a6",
        address=33285,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=2,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A07  HKR3 Mischer zu
        name="hkr3_mixer_heating_circuit_close_a7",
        address=33286,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=2,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A10 HKR2 Mischer auf
        name="hkr2_mixer_heating_circuit_open_a10",
        address=33289,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=1,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A11 HKR2 Mischer zu
        name="hkr2_mixer_heating_circuit_close_a11",
        address=33290,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=1,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A13 Heizstab Stufe 2 & 3
        name="heatpump_heating_rod_level_2_3_a13",
        address=33292,
        unit=None,
        device_class=None,
        state_class="measurement",
        multiplier=1,
        byte_swap=1,
        conf_option=4,
        poll_time=0,
        input_type=4,
    ),
    ModbusFieldConfig(  # A12 Brennerstatus
        name="burner_status_a12",  # maybe also valve for remote heat, depending on config
        address=33291,
        unit=None,
        multiplier=1,
        byte_swap=1,
        device_class=None,
        state_class="measurement",
        poll_time=0,
        input_type=4,
        supported_version=1,
    ),
    ModbusFieldConfig(  # A12 Brennerstatus
        name="burner_status_a12",  # maybe also valve for remote heat, depending on config
        address=33291,
        unit=None,
        multiplier=1,
        device_class=None,
        state_class="measurement",
        poll_time=0,
        input_type=4,
        supported_version=2,
    ),
    ModbusFieldConfig(  # S17
        name="solar_volume_flow_s17",
        address=33040,
        unit="l/h",
        device_class=None,
        state_class="measurement",
        multiplier=1,
        conf_option=3,
        poll_time=0,
        suggested_precision=0,
        supported_version=1,  # SC3
    ),
    ModbusFieldConfig(  # S17
        name="solar_volume_flow_s17",
        address=33040,
        unit="l/min",
        device_class=None,
        state_class="measurement",
        multiplier=1,
        conf_option=3,
        poll_time=0,
        data_processing=3,
        supported_version=2,  # SC2
    ),
    ModbusFieldConfig(  # Solarleistung
        name="solar_power",
        address=33543,
        unit="kW",
        device_class="power",
        state_class="measurement",
        register=2,
        edit=False,
        conf_option=3,
        poll_time=0,
        supported_version=1,
    ),
    ModbusFieldConfig(  # Volumenstrom Warmwasser S18
        name="warm_water_volume_flow_s18",
        address=33041,
        unit="l/min",
        device_class=None,
        state_class="measurement",
        supported_version=1,  # SC3
        poll_time=0,
    ),
    ModbusFieldConfig(  # Volumenstrom Warmwasser S18
        name="warm_water_volume_flow_s18",
        address=33041,
        unit="l/min",
        device_class=None,
        state_class="measurement",
        supported_version=2,  # SC2
        data_processing=2,
        multiplier=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Betriebsart
        name="hkr1_operating_mode",
        address=2818,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        input_type=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Warmwasser Vorrang
        name="hkr1_warm_water_priority",
        address=2817,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=3,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Vorlaufart
        name="hkr1_flow_type",
        address=2819,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        poll_rate=1,
        poll_time=0,
        input_type=1,
        options=("0", "1"),
    ),
    ModbusFieldConfig(  # HKR1 Fix Temperatur Tag
        name="hkr1_fix_day_temp",
        address=2820,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        input_type=2,
        range_data=(5, 75),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Fix Vorlauf Nacht
        name="hkr1_fix_reduction_temp",
        address=2821,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 75),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 1
        name="hkr1_heating_curve_day_temp_1",
        address=2822,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 50),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 2
        name="hkr1_heating_curve_day_temp_2",
        address=2823,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 3
        name="hkr1_heating_curve_day_temp_3",
        address=2824,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Absenkung
        name="hkr1_heating_curve_reduction_temp",
        address=2825,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Steilheit
        name="hkr1_heating_curve_slope",
        address=2826,
        unit=None,
        device_class=None,
        state_class="measurement",
        register=2,
        multiplier=0.01,
        edit=True,
        input_type=2,
        range_data=(0.2, 2.5),
        step_size=0.05,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR1 type sensor > READ
        name="hkr1_room_temp",
        address=34304,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        range_data=(0, 40),
        poll_time=0,
        conf_option=6,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR1 type number > WRITE
        name="hkr1_room_temp",
        address=34304,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        input_type=2,  # number
        edit=True,  # writeable
        register=2,
        range_data=(0, 40),
        poll_time=0,
        conf_option=7,
    ),
    ModbusFieldConfig(  # A9 Mischer Heizkreis 1 zu
        name="hkr1_mixer_heating_circuit_close_a9",
        address=33288,
        state_class="measurement",
        device_class=None,
        poll_time=0,
        unit=None,
        # multiplier=0.001,
        multiplier=1,
        input_type=4,
    ),
    ModbusFieldConfig(  # A8 Mischer Heizkreis 1 auf
        name="hkr1_mixer_heating_circuit_open_a8",
        address=33287,
        state_class="measurement",
        device_class=None,
        poll_time=0,
        unit=None,
        # multiplier=0.001,
        multiplier=1,
        input_type=4,
    ),
    ModbusFieldConfig(  # HKR2 Betriebsart
        name="hkr2_operating_mode",
        address=3074,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        conf_option=1,
        input_type=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Vorlaufart
        name="hkr2_flow_type",
        address=3075,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        conf_option=1,
        poll_rate=1,
        poll_time=0,
        input_type=1,
        options=("0", "1"),
    ),
    ModbusFieldConfig(  # HKR2 Warmwasser Vorrang
        name="hkr2_warm_water_priority",
        address=3073,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=3,
        conf_option=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Fix Vorlauf Tag
        name="hkr2_fix_day_temp",
        address=3076,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 75),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Fix Vorlauf Nacht
        name="hkr2_fix_reduction_temp",
        address=3077,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 75),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 1
        name="hkr2_heating_curve_day_temp_1",
        address=3078,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 50),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 2
        name="hkr2_heating_curve_day_temp_2",
        address=3079,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 3
        name="hkr2_heating_curve_day_temp_3",
        address=3080,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Absenkung
        name="hkr2_heating_curve_reduction_temp",
        address=3081,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Steilheit
        name="hkr2_heating_curve_slope",
        address=3082,
        unit=None,
        device_class=None,
        state_class="measurement",
        register=2,
        multiplier=0.01,
        edit=True,
        input_type=2,
        range_data=(0.2, 2.5),
        conf_option=1,
        step_size=0.05,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Raumtemperatur HKR2 - readonly
        name="hkr2_room_temp",
        address=34305,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        range_data=(0, 40),
        conf_option=(1, 6),
        poll_time=0,
    ),
    ModbusFieldConfig(  # Raumtemperatur HKR2 - writeable
        name="hkr2_room_temp",
        address=34305,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        range_data=(0, 40),
        conf_option=(1, 7),
        poll_time=0,
        input_type=2,
        edit=True,
    ),
    ModbusFieldConfig(  # HKR3 Betriebsart
        name="hkr3_operating_mode",
        address=3330,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        conf_option=2,
        input_type=1,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Vorlaufart
        name="hkr3_flow_type",
        address=3331,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        conf_option=2,
        poll_rate=1,
        poll_time=0,
        input_type=1,
        options=("0", "1"),
    ),
    ModbusFieldConfig(  # HKR3 Warmwasser Vorrang
        name="hkr3_warm_water_priority",
        address=3329,
        unit=None,
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=3,
        conf_option=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Fix Vorlauf Tag
        name="hkr3_fix_day_temp",
        address=3332,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        range_data=(5, 75),
        conf_option=2,
        input_type=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Fix Vorlauf Nacht
        name="hkr3_fix_reduction_temp",
        address=3333,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 75),
        conf_option=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 1
        name="hkr3_heating_curve_day_temp_1",
        address=3334,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 50),
        conf_option=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 2
        name="hkr3_heat_curve_day_temp_2",
        address=3335,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 3
        name="hkr3_heating_curve_day_temp_3",
        address=3336,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=2,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Absenkung
        name="hkr3_heating_curve_reduction_temp",
        address=3336,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
        conf_option=2,
        poll_time=0,
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Steilheit
        name="hkr3_heating_curve_slope",
        address=3338,
        unit=None,
        device_class=None,
        state_class="measurement",
        register=2,
        multiplier=0.01,
        edit=True,
        input_type=2,
        range_data=(0.2, 2.5),
        conf_option=2,
        step_size=0.05,
        poll_rate=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR3 - read only
        name="hkr3_room_temp",
        address=34306,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        range_data=(0, 40),
        conf_option=(2, 6),
        poll_time=0,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR3 - write
        name="hkr3_room_temp",
        address=34306,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        range_data=(0, 40),
        conf_option=(2, 7),
        poll_time=0,
        edit=True,
        input_type=2,
    ),
    ModbusFieldConfig(  # VersionSC
        name="version_sc",
        address=32770,
        unit=None,
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
        data_processing=1,
        poll_rate=1,
        poll_time=0,
        suggested_precision=None,
    ),
    ModbusFieldConfig(  # VersionNBG
        name="version_nbg",
        address=32771,
        unit=None,
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
        data_processing=1,
        poll_rate=1,
        poll_time=0,
        suggested_precision=None,
    ),
    ModbusFieldConfig(
        name="digin_error",
        address=33045,
        unit=None,
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
        poll_time=0,
        suggested_precision=0,
        data_processing=4,
        input_type=4,
    ),
    ModbusFieldConfig(  # ZirkulationBetriebsart
        name="circulation_operating_mode",
        address=2049,
        unit=None,
        device_class=None,
        state_class=None,
        multiplier=1,
        poll_time=0,
    ),
    ModbusFieldConfig(  # Wärmepumenleistung - Leistungsabgabe thermisch
        name="heatpump_power_output_thermal",
        address=33544,
        unit="kW",
        device_class="power",
        state_class="measurement",
        register=2,
        edit=False,
        conf_option=4,
        poll_time=0,
    ),
    ModbusFieldConfig(  # elektrische Wärmepumenleistung - Leistungsaufnahme elektrisch
        name="heatpump_power_input_electric",
        address=33545,
        unit="kW",
        device_class="power",
        state_class="measurement",
        register=2,
        edit=False,
        conf_option=4,
        poll_time=0,
    ),
    ModbusFieldConfig(  # to be verified: PV2Heat Leistung elektrisch
        name="pv2heat_power_electric",
        address=33548,
        unit="kW",
        device_class="power",
        state_class="measurement",
        register=2,
        edit=False,
        poll_time=0,
        conf_option=8,
    ),
    ModbusFieldConfig(  # Umschaltventil Wärmepumpe A14
        name="heatpump_switching_valve_a14",
        address=33293,
        unit=None,
        state_class="measurement",
        device_class=None,
        conf_option=4,
        poll_time=0,
        byte_swap=1,
        multiplier=1,
        input_type=4,
    ),
    ModbusFieldConfig(  # Wärmemengenzähler Leistung
        name="heat_meter_power_thermal",
        address=33550,
        unit="kW",
        state_class="measurement",
        device_class="power",
        poll_time=0,
        conf_option=5,
    ),  # Added with #121
    ModbusFieldConfig(
        name="burner_modulation_o1",
        address=33294,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        conf_option=0,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
    ModbusFieldConfig(
        name="solar_pump_primary_o2",
        address=33295,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        conf_option=3,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
    ModbusFieldConfig(
        name="solar_pump_secondary_o3",
        address=33296,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        conf_option=3,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
    ModbusFieldConfig(
        name="heatpump_charging_pump_o4",
        address=33297,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        conf_option=4,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
    ModbusFieldConfig(
        name="warm_water_pump_o5",
        address=33298,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        conf_option=0,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
    ModbusFieldConfig(
        name="analog_out_o6",
        address=33299,
        unit="%",
        device_class=None,
        state_class="measurement",
        register=1,
        enabled_by_default=False,
        conf_option=0,
        input_type=0,
        poll_time=0,
        suggested_precision=0,
    ),  #  Added with #144
]
