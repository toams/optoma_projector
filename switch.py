"""Use serial protocol of Optoma projector to obtain state of the projector."""
import logging
import re

import serial
import voluptuous as vol

from homeassistant.components.switch import PLATFORM_SCHEMA, SwitchEntity
from homeassistant.const import (
    CONF_FILENAME,
    CONF_NAME,
    CONF_TIMEOUT,
    STATE_OFF,
    STATE_ON,
    STATE_UNKNOWN,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_WRITE_TIMEOUT = "write_timeout"

DEFAULT_NAME = "Optoma Projector"
DEFAULT_TIMEOUT = 1
DEFAULT_WRITE_TIMEOUT = 1

ICON = "mdi:projector"

INPUT_SOURCE = "Input Source"
LAMP = "Lamp"
LAMP_HOURS = "Lamp Hours"


# Commands known to the projector
GET_STATE = "~00124 1\r"
INFO = "~00150 1\r"
SET_STATE_ON = "~0000 1\r"
SET_STATE_OFF = "~0000 0\r"
SOURCE_LIST = ["None","VGA1","VGA2","Video","S-Video","HDMI","DVI"]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_FILENAME): cv.isdevice,
        vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
        vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): cv.positive_int,
        vol.Optional(
            CONF_WRITE_TIMEOUT, default=DEFAULT_WRITE_TIMEOUT
        ): cv.positive_int,
    }
)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Connect with serial port and return Optoma Projector."""
    serial_port = config[CONF_FILENAME]
    name = config[CONF_NAME]
    timeout = config[CONF_TIMEOUT]
    write_timeout = config[CONF_WRITE_TIMEOUT]

    add_entities([OptomaSwitch(serial_port, name, timeout, write_timeout)], True)


class OptomaSwitch(SwitchEntity):
    """Represents an Optoma Projector as a switch."""

    def __init__(self, serial_port, name, timeout, write_timeout, **kwargs):
        """Init of the Optoma projector."""
        self.ser = serial.Serial(
            port=serial_port, timeout=timeout, write_timeout=write_timeout, **kwargs
        )
        self._serial_port = serial_port
        self._name = name
        self._state = False
        self._available = False
        self._attributes = {
            LAMP_HOURS: STATE_UNKNOWN,
            INPUT_SOURCE: STATE_UNKNOWN,
        }

    def _write_read(self, msg):
        """Write to the projector and read the return."""
        ret = ""
        # Sometimes the projector won't answer for no reason or the projector
        # was disconnected during runtime.
        # This way the projector can be reconnected and will still work
        try:
            if not self.ser.is_open:
                self.ser.open()
            msg = msg.encode("ascii")
            self.ser.write(msg)
            # Read until a <CR> is recieved
            ret = self.ser.read_until(b'\r').decode("ascii")
            # _LOGGER.error("ret: %s", ret)
        except serial.SerialException:
            _LOGGER.error("Problem communicating with %s", self._serial_port)
        self.ser.close()
        return ret

    @property
    def available(self):
        """Return if projector is available."""
        return self._available

    @property
    def name(self):
        """Return name of the projector."""
        return self._name

    @property
    def is_on(self):
        """Return if the projector is turned on."""
        return self._state

    @property
    def state_attributes(self):
        """Return state attributes."""
        return self._attributes

    def update(self):
        """Get the latest state from the projector."""
        awns = self._write_read(GET_STATE)
        if awns == "OK1\r":
            self._state = True
            self._available = True
        elif awns == "OK0\r":
            self._state = False
            self._available = True
        else:
            self._available = False

        if self._state == True:
            awns = self._write_read(INFO)
            self._attributes[LAMP_HOURS] = awns[3:7]
            self._attributes[INPUT_SOURCE] = SOURCE_LIST[int(awns[8:9])]

    def turn_on(self, **kwargs):
        """Turn the projector on."""
        self._write_read(SET_STATE_ON)
        self._state = STATE_ON

    def turn_off(self, **kwargs):
        """Turn the projector off."""
        self._write_read(SET_STATE_OFF)
        self._state = STATE_OFF
