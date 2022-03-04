"""Platform for sensor integration."""
from __future__ import annotations

import homeassistant.helpers.config_validation as cv
import requests
import voluptuous as vol
from homeassistant.components.sensor import SensorEntity, PLATFORM_SCHEMA, SensorStateClass, SensorDeviceClass
from homeassistant.const import CONF_USERNAME, CONF_PASSWORD, CONF_API_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
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
    url = "https://secure.kontomierz.pl/k4/user_accounts.json?api_key=" + config.get(CONF_API_TOKEN)
    payload = {}
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }
    response = requests.get(url, auth=HTTPBasicAuth(config.get(CONF_USERNAME), config.get(CONF_PASSWORD)),
                            headers=headers, data=payload)
    response_json = response.json()
    for x in response_json:
        account = x.get('user_account')
        add_entities(
            [KontomierzSensor(hass, config, account.get('bank_name') + " - " + account.get('display_name'),
                              account.get('iban'))])


class KontomierzSensor(SensorEntity):
    """Representation of a Sensor."""

    def __init__(self, hass, config: dict, entity_name: string, iban: string) -> None:
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._state = None
        self.hass = hass
        self.username = config.get(CONF_USERNAME)
        self.password = config.get(CONF_PASSWORD)
        self.apiToken = config.get(CONF_API_TOKEN)
        self.entity_name = entity_name
        self.iban = iban

    @property
    def name(self) -> str:
        return self.entity_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    def update(self) -> None:
        """Fetch new state data for the sensor.
        This is the only method that should fetch new data for Home Assistant.
        """

        url = "https://secure.kontomierz.pl/k4/user_accounts.json?api_key=" + self.apiToken

        response = requests.get(url, auth=HTTPBasicAuth(self.username, self.password), headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }, data={})
        response_json = response.json()
        result = 0.0
        for x in response_json:
            user_account = x.get('user_account')
            if self.iban == user_account.get('iban'):
                result = float(user_account.get('balance'))
                self._attr_native_unit_of_measurement = user_account.get('currency_name')

        self._state = result
