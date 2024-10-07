from dataclasses import dataclass

DOMAIN = "solvis_control"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"
# Option attributes to make certain values configurable
CONF_OPTION_1 = "HKR2"  # HKR 2
CONF_OPTION_2 = "HKR3"  # HKR 3
CONF_OPTION_3 = "solar collector"  # Solar collector
CONF_OPTION_4 = "heat pump"  # heat pump

DATA_COORDINATOR = "coordinator"
MANUFACTURER = "Solvis"


@dataclass(frozen=True)
class ModbusFieldConfig:
    name: str
    address: int
    unit: str
    device_class: str
    state_class: str
    multiplier: float = 0.1
    absolute_value: bool = False

    register: int = 1
    # 1 = INPUT, 2 = HOLDING
    entity_category: str = None
    # Option to disable entitiy by default
    enabled_by_default: bool = True
    # Allows entities to be set to editable
    edit: bool = False
    # Assigns a range for number entities input_type = 2
    range_data: tuple = None
    # Assigns possible potions for select entities input_type = 1
    options: tuple = None

    # Assign CONF_OPTION to entities
    conf_option: int = 0

    # Configuration for which state class a register belongs to
    # Possibilites:
    # sensor (0), select (1), number (2), switch (3)
    input_type: int = 0


PORT = 502
REGISTERS = [
    ModbusFieldConfig(  # Brennerleistung
        name="gas_power",
        address=33539,
        unit="kW",
        device_class="power",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Außentemperatur
        name="outdoor_air_temp",
        address=33033,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="roof_air_temp",
        address=33031,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
    ),
    ModbusFieldConfig(  # Zirkulationsdurchfluss
        name="cold_water_temp",
        address=33034,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        multiplier=0.1,
    ),
    ModbusFieldConfig(  # Vorlauftemperatur
        name="flow_water_temp",
        address=33035,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Warmwassertemperatur
        name="domestic_water_temp",
        address=33025,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="solar_water_temp",
        address=33030,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_in_water_temp",
        address=33029,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_out_water_temp",
        address=33028,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        conf_option=3,
    ),
    ModbusFieldConfig(  # Speicherreferenztemperatur
        name="tank_layer1_water_temp",
        address=33026,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur unten
        name="tank_layer2_water_temp",
        address=33032,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        absolute_value=True,
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur oben
        name="tank_layer3_water_temp",
        address=33027,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        absolute_value=True,
    ),
    ModbusFieldConfig(  # Warmwasserpuffer
        name="tank_layer4_water_temp",
        address=33024,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Kaltwassertemperatur
        name="cold_water_temperatur",
        address=33038,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Laufzeit Brenner
        name="runtime_gasburner",
        address=33536,
        unit="h",
        device_class="time",
        state_class="measurement",
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # Brennerstarts
        name="number_gas_burner_start",
        address=33537,
        unit="",
        device_class="",
        state_class="measurement",
        multiplier=1,
        entity_category="diagnostic",
        absolute_value=True,
    ),
    ModbusFieldConfig(  # Ionisationsstrom
        name="ionisation_voltage",
        address=33540,
        unit="mA",
        device_class="current",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A01.Pumpe Zirkulation
        name="a01_pumpe_zirkulation",
        address=33280,
        unit="%",
        device_class="power_factor",
        state_class="measurement",
        multiplier=0.01,
    ),
    ModbusFieldConfig(  # A02.Pumpe Warmwasser
        name="a02_pumpe_warmwasser",
        address=33281,
        unit="%",
        device_class="power_factor",
        state_class="measurement",
        multiplier=0.01,
    ),
    ModbusFieldConfig(  # A03.Pumpe HKR 1
        name="a03_pumpe_hkr1",
        address=33282,
        unit="%",
        device_class="power_factor",
        state_class="measurement",
        multiplier=0.01,
    ),
    ModbusFieldConfig(  # A04.Pumpe HKR 2
        name="a04_pumpe_hkr2",
        address=33283,
        unit="V",
        device_class="voltage",
        state_class="measurement",
        multiplier=0.01,
        conf_option=1,
    ),
    ModbusFieldConfig(  # A05.Pumpe HKR 3
        name="a05_pumpe_hkr3",
        address=33284,
        unit="%",
        device_class="power_factor",
        state_class="measurement",
        multiplier=0.01,
        conf_option=2,
    ),
    ModbusFieldConfig(  # A12.Brennerstatus
        name="a12_brennerstatus",
        address=33291,
        unit="%",
        device_class="power_factor",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="solar_water_flow",
        address=33040,
        unit="l/min",
        device_class=None,
        state_class="measurement",
        conf_option=3,
    ),
    ModbusFieldConfig(  # Durchfluss Warmwasserzirkualation
        name="domestic_water_flow",
        address=33041,
        unit="l/min",
        device_class=None,
        state_class="measurement",
    ),
    ModbusFieldConfig(  # HKR1 Betriebsart
        name="hkr1_betriebsart",
        address=2818,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        input_type=1,
    ),
    ModbusFieldConfig(  # HKR1 Vorlaufart
        name="hkr1_vorlaufart",
        address=2819,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=1,
    ),
    ModbusFieldConfig(  # HKR1 Fix Vorlauf Tag
        name="hkr1_fix_vorlauf_tag",
        address=2820,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        input_type=2,
        range_data=(5, 75),
    ),
    ModbusFieldConfig(  # HKR1 Fix Vorlauf Nacht
        name="hkr1_fix_vorlauf_nacht",
        address=2821,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 75),
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 1
        name="hkr1_heizkurve_temp_tag_1",
        address=2822,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 50),
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 2
        name="hkr1_heizkurve_temp_tag_2",
        address=2823,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Tag Temp. 3
        name="hkr1_heizkurve_temp_tag_3",
        address=2824,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Absenkung
        name="hkr1_heizkurve_temp_absenkung",
        address=2825,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(5, 30),
    ),
    ModbusFieldConfig(  # HKR1 Heizkurve Steilheit
        name="hkr1_heizkurve_steilheit",
        address=2832,
        unit="",
        device_class="",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(20, 250),
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR1
        name="raumtemperatur_hkr1",
        address=34304,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        edit=True,
        input_type=2,
        range_data=(0, 40),
    ),
    ModbusFieldConfig(  # HKR2 Betriebsart
        name="hkr2_betriebsart",
        address=3074,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        conf_option=1,
        input_type=1,
    ),
    ModbusFieldConfig(  # HKR2 Vorlaufart
        name="hkr2_vorlaufart",
        address=3075,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=1,
        conf_option=1,
    ),
    ModbusFieldConfig(  # HKR2 Fix Vorlauf Tag
        name="hkr2_fix_vorlauf_tag",
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
    ),
    ModbusFieldConfig(  # HKR2 Fix Vorlauf Nacht
        name="hkr2_fix_vorlauf_nacht",
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
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 1
        name="hkr2_heizkurve_temp_tag_1",
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
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 2
        name="hkr2_heizkurve_temp_tag_2",
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
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Tag Temp. 3
        name="hkr2_heizkurve_temp_tag_3",
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
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Absenkung
        name="hkr2_heizkurve_temp_absenkung",
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
    ),
    ModbusFieldConfig(  # HKR2 Heizkurve Steilheit
        name="hkr2_heizkurve_steilheit",
        address=3088,
        unit="",
        device_class="",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(20, 250),
        conf_option=1,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR2
        name="raumtemperatur_hkr2",
        address=34305,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        edit=True,
        input_type=2,
        range_data=(0, 40),
        conf_option=1,
    ),
    ModbusFieldConfig(  # HKR3 Betriebsart
        name="hkr3_betriebsart",
        address=3330,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        options=("2", "3", "4", "5", "6", "7"),
        conf_option=2,
        input_type=1,
    ),
    ModbusFieldConfig(  # HKR3 Vorlaufart
        name="hkr3_vorlaufart",
        address=3331,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
        input_type=1,
        conf_option=2,
    ),
    ModbusFieldConfig(  # HKR3 Fix Vorlauf Tag
        name="hkr3_fix_vorlauf_tag",
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
    ),
    ModbusFieldConfig(  # HKR3 Fix Vorlauf Nacht
        name="hkr3_fix_vorlauf_nacht",
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
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 1
        name="hkr3_heizkurve_temp_tag_1",
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
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 2
        name="hkr3_heizkurve_temp_tag_2",
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
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Tag Temp. 3
        name="hkr3_heizkurve_temp_tag_3",
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
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Absenkung
        name="hkr3_heizkurve_temp_absenkung",
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
    ),
    ModbusFieldConfig(  # HKR3 Heizkurve Steilheit
        name="hkr3_heizkurve_steilheit",
        address=3344,
        unit="",
        device_class="",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(20, 250),
        conf_option=2,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR3
        name="raumtemperatur_hkr3",
        address=34306,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        edit=True,
        input_type=2,
        range_data=(0, 40),
        conf_option=2,
    ),
    ModbusFieldConfig(  # DigIn Stoerungen
        name="digin_stoerungen",
        address=33045,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # WW Solltemperatur
        name="ww_solltemperatur",
        address=2305,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        register=2,
        multiplier=1,
        edit=True,
        input_type=2,
        range_data=(10, 65),
    ),
    ModbusFieldConfig(  # VersionSC3
        name="version_sc3",
        address=32770,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # VersionNBG
        name="version_nbg",
        address=32771,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # ZirkulationBetriebsart
        name="zirkulation_betriebsart",
        address=2049,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Wärmepumenleistung
        name="waermepumpe_leistung",
        address=33544,
        unit="kW",
        device_class="power",
        state_class="measurement",
        register=2,
        edit=False,
        conf_option=4,
    ),
    ModbusFieldConfig(  # elektrische Wärmepumenleistung
        name="elek_waermepumpe_leistung",
        address=33545,
        unit="kWh",
        device_class="energy",
        state_class="total",
        register=2,
        edit=False,
        conf_option=4,
    ),
]
