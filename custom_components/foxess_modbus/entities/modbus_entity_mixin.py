import logging

from homeassistant.const import ATTR_IDENTIFIERS
from homeassistant.const import ATTR_MANUFACTURER
from homeassistant.const import ATTR_MODEL
from homeassistant.const import ATTR_NAME

from ..const import DOMAIN
from ..const import FRIENDLY_NAME
from ..const import INVERTER_CONN
from ..const import INVERTER_MODEL

_LOGGER = logging.getLogger(__name__)


class ModbusEntityMixin:
    """
    Mixin for subclasses of Entity

    This provides properties which are common to all FoxESS entities.
    It assumes that the following propties are defined on the class:

        controller: CallbackController
        entity_description: EntityDescription
        _inv_details
    """

    @property
    def unique_id(self) -> str:
        """Return a unique ID."""
        return "foxess_modbus_" + self._get_unique_id()

    @property
    def device_info(self):
        """Return device specific attributes."""
        friendly_name = self._inv_details[FRIENDLY_NAME]
        inv_model = self._inv_details[INVERTER_MODEL]
        conn_type = self._inv_details[INVERTER_CONN]
        if friendly_name != "":
            attr_name = f"FoxESS - Modbus ({friendly_name})"
        else:
            attr_name = "FoxESS - Modbus"

        return {
            ATTR_IDENTIFIERS: {(DOMAIN, inv_model, conn_type, friendly_name)},
            ATTR_NAME: attr_name,
            ATTR_MODEL: f"{inv_model} - {conn_type}",
            ATTR_MANUFACTURER: "FoxESS",
        }

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        friendly_name = self._inv_details[FRIENDLY_NAME]
        if friendly_name != "":
            return f"{self.entity_description.name} ({friendly_name})"
        else:
            return self.entity_description.name

    def _get_unique_id(self):
        """Get unique ID"""
        friendly_name = self._inv_details[FRIENDLY_NAME]
        if friendly_name != "":
            return f"{friendly_name}_{self.entity_description.key}"
        else:
            return f"{self.entity_description.key}"

    async def async_added_to_hass(self) -> None:
        """Add update callback after being added to hass."""
        await super().async_added_to_hass()
        self._controller.add_update_listener(self)

    def update_callback(self, changed_addresses: set[int]) -> None:
        """Schedule a state update."""
        if self.entity_description.address in changed_addresses:
            self.schedule_update_ha_state(True)
