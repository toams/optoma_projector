# optoma_projector
Home assistant integration for the Optoma HD36 projector (and possibly other Optoma projectors).

The projector is controlled by communicating over RS-232. Any USB to RS-232 dongle should work.
This integration is a modification of [Acer Projector](https://github.com/home-assistant/core/tree/dev/homeassistant/components/acer_projector) integration.
It currently supports turning the projector on and off. Additionally it also displays the lamp hours and what video input is currently in use.

Using this integration should be as simple as cloning this repo in you custom_integration folder and adding following lines to your configuration.yaml:


```yaml
switch:
  - platform: optoma_projector
    filename: /dev/ttyUSB0
```

```filename:``` should point to the correct path of your RS-232 port
