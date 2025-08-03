import logging
import mdstat
import simplejson as json
from types import SimpleNamespace
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mdadm_state"


class MDADMData:
    """Coordinator class to read and parse the mdadm RAID status."""

    def __init__(self, device: str):
        self._device = device
        self.data = None

    def update(self):
        """Fetch and parse RAID status from mdstat."""
        try:
            parsed_data = json.loads(
                json.dumps(mdstat.parse()),
                object_hook=lambda d: SimpleNamespace(**d),
            )
            device_config = getattr(parsed_data.devices, self._device)

            state = 'on' if device_config.active else 'off'
            synced = all(device_config.status.synced) if device_config.status.synced else None
            raid_type = device_config.personality
            disks_number = device_config.status.raid_disks
            disks_not_working = device_config.status.raid_disks - device_config.status.non_degraded_disks

            if device_config.resync is not None:
                resync_operation = device_config.resync.operation
                resync_progress = device_config.resync.progress
                resync_finish = device_config.resync.finish
                resync_speed = device_config.resync.speed
            else:
                resync_operation = None
                resync_progress = None
                resync_finish = None
                resync_speed = None

            self.data = {
                'state': state,
                'raid_type': raid_type,
                'disks_number': disks_number,
                'disks_not_working': disks_not_working,
                'sync': synced,
                'resync_operation': resync_operation,
                'resync_progress': resync_progress,
                'resync_finish': resync_finish,
                'resync_speed': resync_speed,
            }
        except Exception as e:
            _LOGGER.error("Error updating MDADM data: %s", e)
            self.data = None


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration.

    No YAML configuration is used since this integration uses config entries.
    """
    # Nothing to set up here because we use config_flow.
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up mdadm_state from a config entry."""

    device = entry.data["device"]
    coordinator = MDADMData(device)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor and binary_sensor platforms (plural method)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok &= await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
