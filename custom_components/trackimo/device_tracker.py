from __future__ import annotations

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .api import TrackimoApiClient

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the device_tracker platform."""
    api_client = hass.data[DOMAIN][config_entry.entry_id]
    devices = await api_client.async_get_devices()
    async_add_entities([TrackimoDeviceTracker(api_client, device) for device in devices])


class TrackimoDeviceTracker(TrackerEntity):
    """Representation of a Trackimo device tracker."""

    def __init__(self, api_client: TrackimoApiClient, device: dict) -> None:
        """Initialize the device tracker."""
        self.api_client = api_client
        self.device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return str(self.device["deviceId"])

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self.device["deviceName"]

    @property
    async def async_latitude(self) -> float | None:
        """Return latitude value of the device."""
        location = await self.api_client.async_get_device_last_location(self.device["deviceId"])
        return location["lat"] if location else None

    @property
    async def async_longitude(self) -> float | None:
        """Return longitude value of the device."""
        location = await self.api_client.async_get_device_last_location(self.device["deviceId"])
        return location["lng"] if location else None

    @property
    def source_type(self) -> SourceType:
        """Return the source type, eg gps or router, of the device."""
        return SourceType.GPS

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.device["deviceId"])},
            "name": self.device["deviceName"],
            "manufacturer": "Trackimo",
            "model": self.device.get("typeId"),
        }