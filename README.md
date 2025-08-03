# RAID Status - Custom Component for Home Assistant

Monitor the status of `mdadm` RAID devices in Home Assistant, with each RAID parameter exposed as a dedicated sensor entity.

## Requirements

- `mdadm` installed on your server (for monitoring RAID)
- Python packages: `mdstat`, `simplejson` (automatically required by this integration)

## How to Install

### Using HACS

1. Go to **HACS → 3 dots → Custom Repositories**.
2. Add your repository link and select "Integration" as the category.
3. Search for **"RAID Status - MDADM"** under HACS Integrations and install it.

### Manual Installation (without HACS)

1. Download this repository.
2. Copy the `custom_components/mdadm_state` folder into your Home Assistant `config/custom_components/` directory.

## YAML Configuration

> You should configure **both** a `binary_sensor` (RAID state, on/off) and `sensor` entries (for all other RAID details):

```yaml
# configuration.yaml example
binary_sensor:
  - platform: mdadm_state
    device: md0        # Replace md0 with your actual RAID device name (e.g., md127)

sensor:
  - platform: mdadm_state
    device: md0        # Same device as above, adds sensor entities for RAID status attributes
```

### Configuration Variables

| Variable | Required | Description                          | Example    |
|----------|----------|--------------------------------------|------------|
| device   | Yes      | mdadm RAID device name (no `/dev/`)  | `md0`      |

- For `/dev/md0`, use `device: md0`, for `/dev/md127` use `device: md127`, etc.

## Entities Created

- **Binary Sensor:** `binary_sensor.raid_dev_md0_state` (on/off)
- **Sensors:** `sensor.raid_dev_md0_raid_type`, `sensor.raid_dev_md0_disks_number`, `sensor.raid_dev_md0_sync`, `sensor.raid_dev_md0_resync_speed`, and others, exposing all available RAID attributes.

Each sensor has a unique ID for easy customization in Home Assistant’s UI.

## Contributions

- Uses [`mdstat`](https://pypi.org/project/mdstat/) for parsing Linux RAID status.
- Uses [`simplejson`](https://pypi.org/project/simplejson/) for efficient JSON parsing.
