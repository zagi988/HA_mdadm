import logging
from homeassistant.helpers.entity import Entity
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

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up mdadm sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    sensors = [RaidStatusSensor(coordinator, attr, entry.entry_id) for attr in SENSOR_TYPES]
    async_add_entities(sensors, update_before_add=True)


class RaidStatusSensor(Entity):
    def __init__(self, coordinator, attribute, entry_id):
        self.coordinator = coordinator
        self.attribute = attribute
        self.entry_id = entry_id
        self._attr_name = f"RAID /dev/{self.coordinator._device} {self.attribute.replace('_', ' ').title()}"
        self._attr_unique_id = f"mdadm_{self.coordinator._device}_{self.attribute}_{entry_id}"
        self._state = None

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def state(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(self.attribute)

    @property
    def device_info(self):
        """Return device information to group sensors under one device."""
        return {
            "identifiers": {(DOMAIN, f"mdadm_{self.coordinator._device}")},
            "name": f"RAID {self.coordinator._device}",
            "manufacturer": "Linux mdadm",
            "model": f"mdadm ({self.coordinator._device})",
        }

    def update(self):
        self.coordinator.update()
