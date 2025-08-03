import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPES = [
    "raid_type",
    "disks_number",
    "disks_not_working",
    "sync",
    "resync_operation",
    "resync_progress",
    "resync_finish",
    "resync_speed",
]

DEVICE_CLASS_MAPPING = {
    "resync_progress": None,  # No official percentage device_class yet
    "resync_speed": "data_rate",
    "resync_finish": "duration",
    "disks_number": None,
    "disks_not_working": None,
    "sync": None,
    "raid_type": None,
    "resync_operation": None,
}

UNIT_MAPPING = {
    "resync_progress": "%",
    "resync_speed": "MB/s",
    "resync_finish": "min",  # Showing minutes instead of seconds
    "disks_number": "disks",
    "disks_not_working": "disks",
    # raid_type, sync, resync_operation do not use units
}


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up mdadm sensors from a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [RaidStatusSensor(coordinator, attr, entry.entry_id) for attr in SENSOR_TYPES]
    async_add_entities(sensors, update_before_add=True)


class RaidStatusSensor(SensorEntity):
    def __init__(self, coordinator, attribute, entry_id):
        self.coordinator = coordinator
        self.attribute = attribute
        self.entry_id = entry_id
        self._attr_name = f"RAID /dev/{self.coordinator._device} {self.attribute.replace('_', ' ').title()}"
        self._attr_unique_id = f"mdadm_{self.coordinator._device}_{self.attribute}_{entry_id}"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def native_value(self):
        """Return the native value with default fallbacks for resync sensors."""

        if self.coordinator.data is None:
            return None

        val = self.coordinator.data.get(self.attribute)

        if self.attribute == "resync_progress":
            # Return 100% if not syncing
            return val if val is not None else 100

        if self.attribute == "resync_speed":
            # Return 0 when not syncing
            return val if val is not None else 0

        if self.attribute == "resync_finish":
            # Return 0 minutes when not syncing, else convert seconds -> minutes rounded 1 decimal
            if val is None or val == 0:
                return 0
            return round(val / 60, 1)

        if self.attribute == "resync_operation":
            # Return "none" string if no operation active
            return val if val is not None else "none"

        # For all others return value as is
        return val

    @property
    def native_unit_of_measurement(self):
        return UNIT_MAPPING.get(self.attribute)

    @property
    def device_class(self):
        return DEVICE_CLASS_MAPPING.get(self.attribute)

    @property
    def state_class(self):
        # Enable graphing for numeric resync sensors
        if self.attribute in ("resync_progress", "resync_speed", "resync_finish"):
            return "measurement"
        return None

    @property
    def device_info(self):
        """Group all RAID sensors under one logical device."""
        return {
            "identifiers": {(DOMAIN, f"mdadm_{self.coordinator._device}")},
            "name": f"RAID {self.coordinator._device}",
            "manufacturer": "Linux mdadm",
            "model": f"mdadm ({self.coordinator._device})",
        }

    def update(self):
        self.coordinator.update()
