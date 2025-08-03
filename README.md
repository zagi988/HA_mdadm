# RAID Status - Custom Component for Home Assistant

Monitor the status of `mdadm` RAID devices in Home Assistant, with each RAID parameter exposed as individual sensors grouped under a single RAID device.

## Requirements

- `mdadm` installed on your server (for RAID management)
- Python packages: `mdstat`, `simplejson` (these are installed automatically with the integration)

## Installation

### Using HACS

1. Go to **HACS → 3 dots → Custom Repositories**.
2. Add the repository URL and select **Integration** as the category.
3. Search for **RAID Status - MDADM** and install it.

### Manual Installation (without HACS)

1. Download this repository.
2. Copy the folder `custom_components/mdadm_state` into your Home Assistant `config/custom_components/` directory.

## Configuration via Home Assistant UI

This integration supports UI configuration via the **Integrations** page. No manual YAML editing is required.

1. Go to **Settings → Devices & Services → Add Integration**.
2. Search for **RAID Status - MDADM**.
3. Enter your RAID device name (e.g., `md0` for `/dev/md0`) when prompted.
4. The integration will create:
   - A **binary sensor** representing RAID state (on/off).
   - Multiple **sensors** representing individual RAID attributes such as RAID type, disk count, sync status, resync progress, and more.
5. All these entities will be grouped under a single **device** named like `RAID md0`.

## Entities Created

- **Device:** `RAID ` (e.g., `RAID md0`)
- **Binary Sensor:** e.g., `binary_sensor.raid_md0_state` — indicating if RAID device is active (`on`/`off`).
- **Sensors:** e.g., `sensor.raid_md0_raid_type`, `sensor.raid_md0_disks_number`, `sensor.raid_md0_sync`, `sensor.raid_md0_resync_speed`, etc., exposing detailed RAID status values.

## Configuration Variables

| Variable | Required | Description                               | Example  |
| -------- | -------- | ----------------------------------------- | -------- |
| device   | Yes      | RAID device name (just the basename, no `/dev/` prefix) | `md0`     |

## Notes

- The integration periodically polls local RAID status using the `mdstat` Python library.
- Unique IDs are assigned for each entity, allowing you to customize, rename, or disable them via the Home Assistant UI.
- Entities are grouped in a device for easier management.
- No YAML configuration is required after installation; integration config is fully UI-driven.

## Contributions & Libraries Used

- [`mdstat`](https://pypi.org/project/mdstat/) — parsing Linux RAID status.
- [`simplejson`](https://pypi.org/project/simplejson/) — JSON encoding and decoding.
