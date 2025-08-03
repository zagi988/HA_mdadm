import logging
import mdstat
import simplejson as json
from types import SimpleNamespace

_LOGGER = logging.getLogger(__name__)

class MDADMData:
    def __init__(self, device):
        self._device = device
        self.data = None

    def update(self):
        try:
            parsed_data = json.loads(json.dumps(mdstat.parse()), object_hook=lambda d: SimpleNamespace(**d))
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
