import unittest
import pytest
import asyncio
import voluptuous as vol

from voluptuous.error import Invalid
# from pytest_homeassistant_custom_component.common import MockConfigEntry
from unittest.mock import Mock, AsyncMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException, ModbusException
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from scapy.all import ARP, Ether
from custom_components.solvis_control.config_flow import SolvisConfigFlow
from custom_components.solvis_control.config_flow import get_solvis_modules_options
from custom_components.solvis_control.const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    POLL_RATE_SLOW,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    DEVICE_VERSION,
    SolvisDeviceVersion,
)


@pytest.mark.asyncio
async def test_debug_modbus_patch(patch_modbus_client):
    client = patch_modbus_client("127.0.0.1", 502)
    assert client is not None
    assert hasattr(client, "read_input_registers")


@pytest.mark.asyncio
@pytest.mark.parametrize("mock_get_mac", [{"mac": "00:11:22:33:44:55"}], indirect=True)
@pytest.mark.parametrize("mock_modbus", [{"32770": [12345], "32771": [56789]}], indirect=True)
async def test_config_flow_full(hass, mock_get_mac, mock_modbus) -> None:

    # start config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": "user"})

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # user input step user
    user_input = {
        CONF_NAME: "Solvis Heizung Test",
        CONF_HOST: "10.0.0.131",
        CONF_PORT: 502,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"

    # user input step device
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"

    # user input step features
    feature_input = {
        CONF_OPTION_1: False,
        CONF_OPTION_2: False,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_6: False,
        CONF_OPTION_7: False,
        CONF_OPTION_8: False,
    }
    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)

    # check
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis Heizung Test"

    # check
    assert result["data"] == {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
    }
