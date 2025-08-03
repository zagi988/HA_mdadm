import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from .const import DOMAIN

class MDADMConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MDADM RAID Status."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            return self.async_create_entry(
                title=f"RAID /dev/{user_input['device']}", data=user_input
            )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("device"): str
            }),
            errors=errors,
        )
