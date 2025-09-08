from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .api import TrackimoApiClient

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Trackimo component from configuration.yaml."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trackimo from a config entry."""
    _LOGGER.debug("async_setup_entry called for entry: %s", entry.entry_id)
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

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok