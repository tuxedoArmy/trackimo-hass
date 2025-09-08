"""The Trackimo integration."""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN, PLATFORMS
from .api import TrackimoApiClient


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required("username"): cv.string,
                vol.Required("password"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the Trackimo component from configuration.yaml."""
    if DOMAIN not in config:
        return True

    hass.async_create_task(
        hass.config_entries.flow.async_init(
            DOMAIN,
            context={"source": config_entries.SOURCE_IMPORT},
            data=config[DOMAIN],
        )
    )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trackimo from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_client = TrackimoApiClient(entry.data["username"], entry.data["password"], hass, debug=True)
    try:
        if not await api_client.async_get_access_token():
            _LOGGER.error("Failed to get access token")
            return False
        if not await api_client.async_get_user_details():
            _LOGGER.error("Failed to get user details")
            return False
    except Exception as e:
        _LOGGER.error("Error during API client setup: %s", e)
        return False

    hass.data[DOMAIN][entry.entry_id] = api_client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await hass.config_entries.async_forward_entry_setup(entry, "config_flow")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
