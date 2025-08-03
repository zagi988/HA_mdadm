import logging
from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback):
    """Set up mdadm binary sensor based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([RaidStateBinarySensor(coordinator, entry.entry_id)], update_before_add=True)


class RaidStateBinarySensor(BinarySensorEntity):
    def __init__(self, coordinator, entry_id):
        self.coordinator = coordinator
        self.entry_id = entry_id
        self._attr_name = f"RAID /dev/{self.coordinator._device} State"
        self._attr_unique_id = f"mdadm_{self.coordinator._device}_state_{entry_id}"
        self._is_on = None

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

    @property
    def device_info(self):
        """Return device information to group binary sensor under one device."""
        return {
            "identifiers": {(DOMAIN, f"mdadm_{self.coordinator._device}")},
            "name": f"RAID {self.coordinator._device}",
            "manufacturer": "Linux mdadm",
            "model": f"mdadm ({self.coordinator._device})",
        }

    def update(self):
        self.coordinator.update()
