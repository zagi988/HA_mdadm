import logging
from homeassistant.helpers.entity import Entity
from . import MDADMData

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

def setup_platform(hass, config, add_entities, discovery_info=None):
    device = config["device"]
    coordinator = MDADMData(device)
    sensors = [RaidStatusSensor(coordinator, attr) for attr in SENSOR_TYPES]
    add_entities(sensors, True)


class RaidStatusSensor(Entity):
    def __init__(self, coordinator, attribute):
        self.coordinator = coordinator
        self.attribute = attribute
        self._attr_name = f"RAID /dev/{self.coordinator._device} {self.attribute.replace('_', ' ').title()}"
        self._attr_unique_id = f"mdadm_{self.coordinator._device}_{self.attribute}"

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

    def update(self):
        self.coordinator.update()
