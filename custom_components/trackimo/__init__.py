"""The Trackimo integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, PLATFORMS
from .api import TrackimoApiClient


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Trackimo from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    api_client = TrackimoApiClient(entry.data["username"], entry.data["password"])
    if not await hass.async_add_executor_job(api_client.get_access_token):
        return False
    if not await hass.async_add_executor_job(api_client.get_user_details):
        return False

    hass.data[DOMAIN][entry.entry_id] = api_client

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
