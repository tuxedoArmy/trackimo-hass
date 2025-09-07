from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

from .const import DOMAIN
from .api import TrackimoApiClient

def setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    """Set up the sensor platform."""
    api_client = hass.data[DOMAIN][config.entry_id]
    devices = api_client.get_devices()
    add_entities([TrackimoBatterySensor(api_client, device) for device in devices])


class TrackimoBatterySensor(SensorEntity):
    """Representation of a Trackimo battery sensor."""

    def __init__(self, api_client: TrackimoApiClient, device: dict) -> None:
        """Initialize the sensor."""
        self.api_client = api_client
        self.device = device

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return f"{self.device['deviceId']}_battery"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return f"{self.device['deviceName']} Battery"

    @property
    def native_value(self) -> int | None:
        """Return the state of the sensor."""
        location = self.api_client.get_device_last_location(self.device["deviceId"])
        return location["battery"] if location else None

    @property
    def device_class(self) -> SensorDeviceClass:
        """Return the device class of the sensor."""
        return SensorDeviceClass.BATTERY

    @property
    def state_class(self) -> SensorStateClass:
        """Return the state class of the sensor."""
        return SensorStateClass.MEASUREMENT

    @property
    def native_unit_of_measurement(self) -> str:
        """Return the unit of measurement of the sensor."""
        return "%"

    @property
    def device_info(self):
        """Return the device info."""
        return {
            "identifiers": {(DOMAIN, self.device["deviceId"])},
            "name": self.device["deviceName"],
            "manufacturer": "Trackimo",
            "model": self.device.get("typeId"),
        }
