import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from . import MDADMData

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_entities, discovery_info=None):
    device = config["device"]
    coordinator = MDADMData(device)
    add_entities([RaidStateBinarySensor(coordinator)], True)


class RaidStateBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self._attr_name = f"RAID /dev/{self.coordinator._device} State"
        self._attr_unique_id = f"mdadm_{self.coordinator._device}_state"

    @property
    def name(self):
        return self._attr_name

    @property
    def unique_id(self):
        return self._attr_unique_id

    @property
    def is_on(self):
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("state") == "on"

    def update(self):
        self.coordinator.update()
