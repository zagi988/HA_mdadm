import logging
import mdstat
import simplejson as json
from types import SimpleNamespace
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)

DOMAIN = "mdadm_state"


def parse_progress(progress_str):
    """Parse progress string like '45%' into float 45.0."""
    try:
        if progress_str is None:
            return None
        return float(str(progress_str).strip().replace("%", ""))
    except Exception as e:
        _LOGGER.debug(f"Failed to parse progress '{progress_str}': {e}")
        return None


def parse_finish_time(time_str):
    """Parse finish time strings into seconds as int.

    Supports:
     - '148.8min' (minutes, decimal allowed)
     - '148.8 min' (with space)
     - '00:45:30' (HH:MM:SS)
     - '45:30' (MM:SS)
     - plain seconds as float or int
    """
    try:
        if time_str is None:
            return None

        val_str = str(time_str).strip().lower()

        # Handle '148.8min' or '148.8 min'
        if val_str.endswith("min"):
            val_num = val_str[:-3].strip()  # strip 'min' suffix and whitespace
            minutes = float(val_num)
            return int(minutes * 60)

        # Handle "HH:MM:SS" or "MM:SS"
        if ":" in val_str:
            parts = val_str.split(":")
            if len(parts) == 3:
                h, m, s = map(int, parts)
                return h * 3600 + m * 60 + s
            elif len(parts) == 2:
                m, s = map(int, parts)
                return m * 60 + s

        # Fallback: treat as seconds directly
        return int(float(val_str))

    except Exception as e:
        _LOGGER.debug(f"Failed to parse finish time '{time_str}': {e}")
        return None


def parse_speed(speed_str):
    """Parse speed strings like '178452K/sec', '830.0 kb/s', or '123 MB/sec' to MB/s float."""
    try:
        if speed_str is None:
            return None
        val_str = str(speed_str).strip().lower()

        # KB/sec variants (no space)
        for kb_unit in ("k/sec", "kb/sec", "k/s", "kb/s"):
            if val_str.endswith(kb_unit):
                num_str = val_str[:-len(kb_unit)]
                num = float(num_str)
                return num / 1024  # Convert KB/s to MB/s

        # MB/sec variants
        for mb_unit in ("m/sec", "mb/sec", "m/s", "mb/s"):
            if val_str.endswith(mb_unit):
                num_str = val_str[:-len(mb_unit)]
                return float(num_str)

        # Handle space-separated number/unit
        if " " in val_str:
            num_str, unit = val_str.split(" ", 1)
            num = float(num_str)
            unit = unit.strip()
            if unit.startswith("kb") or unit.startswith("k"):
                return num / 1024
            elif unit.startswith("mb") or unit.startswith("m"):
                return num
            else:
                return num

        # No unit suffix or unknown, parse directly
        return float(val_str)

    except Exception as e:
        _LOGGER.debug(f"Failed to parse speed '{speed_str}': {e}")
        return None


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

            state = "on" if device_config.active else "off"
            synced = all(device_config.status.synced) if device_config.status.synced else None
            raid_type = device_config.personality
            disks_number = device_config.status.raid_disks
            disks_not_working = device_config.status.raid_disks - device_config.status.non_degraded_disks

            if device_config.resync is not None:
                resync_operation = device_config.resync.operation
                resync_progress = parse_progress(device_config.resync.progress)
                resync_finish = parse_finish_time(device_config.resync.finish)
                resync_speed = parse_speed(device_config.resync.speed)
            else:
                resync_operation = None
                resync_progress = None
                resync_finish = None
                resync_speed = None

            self.data = {
                "state": state,
                "raid_type": raid_type,
                "disks_number": disks_number,
                "disks_not_working": disks_not_working,
                "sync": synced,
                "resync_operation": resync_operation,
                "resync_progress": resync_progress,
                "resync_finish": resync_finish,
                "resync_speed": resync_speed,
            }

            _LOGGER.debug(f"Raw resync values: progress={device_config.resync.progress if device_config.resync else None}, "
                          f"finish={device_config.resync.finish if device_config.resync else None}, "
                          f"speed={device_config.resync.speed if device_config.resync else None}")
            _LOGGER.debug(f"Parsed resync values: progress={resync_progress}, finish={resync_finish}, speed={resync_speed}")

        except Exception as e:
            _LOGGER.error(f"Error updating MDADM data: {e}")
            self.data = None


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the integration.

    No YAML configuration is used since this integration uses config entries.
    """
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up mdadm_state from a config entry."""

    device = entry.data["device"]
    coordinator = MDADMData(device)

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor and binary_sensor platforms (use plural)
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor", "binary_sensor"])

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_forward_entry_unload(entry, "sensor")
    unload_ok &= await hass.config_entries.async_forward_entry_unload(entry, "binary_sensor")

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
