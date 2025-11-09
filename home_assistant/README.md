# OKIN Bed Home Assistant Integration

Home Assistant custom component for controlling OKIN adjustable beds via Bluetooth LE.

## Features

- **Cover Entities**: Control bed sections (head, lumbar, foot) as covers
- **Switch Entities**: Control massage and preset positions
- **Light Entity**: Control under-bed lighting
- **Sensor Entities**: Monitor bed status

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "OKIN Bed" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/okin_bed` directory to your Home Assistant `custom_components` directory
2. Restart Home Assistant

## Configuration

### Via UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "OKIN Bed"
4. Follow the configuration wizard

### Via YAML (Legacy)

Add to your `configuration.yaml`:

```yaml
okin_bed:
  mac_address: "XX:XX:XX:XX:XX:XX"  # Your bed's Bluetooth MAC address
```

## Finding Your Bed's MAC Address

Use the scanner utility from the Python library:

```bash
python -m okin_bed.scanner
```

Or use a Bluetooth scanner app on your phone:
- Android: BLE Scanner, nRF Connect
- iOS: LightBlue

Look for devices with names containing "OKIN", "Adjustable", or "Comfort".

## Entities

After configuration, the following entities will be created:

### Covers
- `cover.okin_bed_head` - Head section control
- `cover.okin_bed_lumbar` - Lumbar section control
- `cover.okin_bed_foot` - Foot section control

### Switches
- `switch.okin_bed_massage` - Massage on/off
- `switch.okin_bed_flat` - Flat position
- `switch.okin_bed_zero_gravity` - Zero gravity position
- `switch.okin_bed_lounge` - Lounge position
- `switch.okin_bed_anti_snore` - Anti-snore position

### Lights
- `light.okin_bed_underbed` - Under-bed lighting

## Example Automations

### Good Morning Routine

```yaml
automation:
  - alias: "Wake Up Gently"
    trigger:
      - platform: time
        at: "07:00:00"
    action:
      - service: light.turn_on
        target:
          entity_id: light.okin_bed_underbed
        data:
          brightness: 50
      - delay: "00:01:00"
      - service: cover.open_cover
        target:
          entity_id: cover.okin_bed_head
        data:
          position: 30
```

### Bedtime Routine

```yaml
automation:
  - alias: "Bedtime Comfort"
    trigger:
      - platform: time
        at: "22:00:00"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.okin_bed_zero_gravity
      - delay: "00:00:05"
      - service: switch.turn_on
        target:
          entity_id: switch.okin_bed_massage
```

### Anti-Snore Activation

```yaml
automation:
  - alias: "Anti-Snore When Snoring Detected"
    trigger:
      - platform: state
        entity_id: binary_sensor.snore_detection
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.okin_bed_anti_snore
```

## Services

### Set Massage Wave

```yaml
service: okin_bed.set_massage_wave
data:
  wave: 2
```

### Set Brightness

```yaml
service: light.turn_on
target:
  entity_id: light.okin_bed_underbed
data:
  brightness: 128
```

## Lovelace Card Example

```yaml
type: vertical-stack
cards:
  - type: entities
    title: Bed Position
    entities:
      - cover.okin_bed_head
      - cover.okin_bed_lumbar
      - cover.okin_bed_foot

  - type: horizontal-stack
    cards:
      - type: button
        name: Flat
        tap_action:
          action: call-service
          service: switch.turn_on
          target:
            entity_id: switch.okin_bed_flat
      - type: button
        name: Zero G
        tap_action:
          action: call-service
          service: switch.turn_on
          target:
            entity_id: switch.okin_bed_zero_gravity
      - type: button
        name: Lounge
        tap_action:
          action: call-service
          service: switch.turn_on
          target:
            entity_id: switch.okin_bed_lounge

  - type: entities
    title: Massage & Lighting
    entities:
      - switch.okin_bed_massage
      - light.okin_bed_underbed
```

## Troubleshooting

### Can't Find Bed

1. Ensure Bluetooth is enabled on your Home Assistant host
2. Make sure the bed is powered on
3. Run the scanner to verify the bed is advertising
4. Check the MAC address is correct

### Connection Issues

1. Restart the integration
2. Restart Home Assistant
3. Power cycle the bed
4. Check Bluetooth adapter is working: `hcitool dev`

### Commands Not Working

⚠️ **Note**: This integration is based on reverse engineering. The actual BLE command protocol needs to be captured from the official app using packet sniffing. See `../PROTOCOL_ANALYSIS.md` for details on how to capture and analyze the protocol.

## Support

For issues and feature requests, please visit:
https://github.com/yourusername/okin-bed-control/issues

## License

MIT License
