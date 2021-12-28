"""Platform for sensor integration."""
from __future__ import annotations
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_API_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import json
import requests
from requests.auth import HTTPBasicAuth

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required(CONF_API_TOKEN): cv.string,
})


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    """Set up the sensor platform."""
    add_entities([KontomierzSensor()])


class KontomierzSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, config: dict):
        """Initialize the sensor."""
        self._state = None
        self.hass = hass
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self.apiToken = config.get(CONF_API_TOKEN)

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return 'Example Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        url = "https://secure.kontomierz.pl/k4/user_accounts.json?api_key=" + self.apiToken

        payload = {}
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }
        response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password), headers=headers, data=payload)

        self._state = response.json()[0].get('user_account').get('balance')
