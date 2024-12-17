from homeassistant import config_entries, core, exceptions
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
import voluptuous as vol

from .const import (
    DOMAIN,
    LOGGER,
)
from . import RepsolLuzYGasAPI


class RepsolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            # Initialize the API client and attempt to login
            api = RepsolLuzYGasAPI(
                async_get_clientsession(self.hass),
                user_input["username"],
                user_input["password"],
            )
            try:
                await api.async_login()
                # Store the API client instance for use in the next step
                self.hass.data.setdefault(DOMAIN, {})["api"] = api
                # Store credentials for potential future use
                self.hass.data[DOMAIN]["credentials"] = user_input
                return await self.async_step_contract()
            except exceptions.HomeAssistantError:
                errors["base"] = "login_failed"

        data_schema = vol.Schema(
            {
                vol.Required("username"): str,
                vol.Required("password"): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_contract(self, user_input=None):
        errors = {}
        api = self.hass.data[DOMAIN]["api"]
        contracts_data = await api.async_get_contracts()

        if not isinstance(contracts_data, dict) or "information" not in contracts_data:
            LOGGER.error("Unexpected contracts data structure: %s", contracts_data)
            errors["base"] = "invalid_contracts_data"
            return self.async_show_form(step_id="user", errors=errors)

        if user_input is not None:
            selected_contract = contracts_data["information"][
                int(user_input["contract_index"])
            ]

            # Check if the contract is already configured
            existing_ids = {
                entry.data["contract_id"] for entry in self._async_current_entries()
            }
            if selected_contract["contract_id"] in existing_ids:
                errors["base"] = "already_configured"
                return self.async_show_form(
                    step_id="contract",
                    data_schema=self._get_contracts_schema(contracts_data),
                    errors=errors,
                )

            self.hass.data[DOMAIN]["contract_id"] = selected_contract["contract_id"]
            self.hass.data[DOMAIN]["house_id"] = contracts_data["house_id"]
            return self.async_create_entry(
                title="Repsol Luz y Gas",
                data={
                    **self.hass.data[DOMAIN]["credentials"],
                    "contract_id": self.hass.data[DOMAIN]["contract_id"],
                    "house_id": self.hass.data[DOMAIN]["house_id"],
                },
            )

        return self.async_show_form(
            step_id="contract",
            data_schema=self._get_contracts_schema(contracts_data),
            errors=errors,
        )

    def _get_contracts_schema(self, contracts_data):
        """Generate dynamic schema for contract selection based on available contracts."""
        return vol.Schema(
            {
                vol.Required("contract_index"): vol.In(
                    {
                        i: f'{contract["contractType"]} - {contract["cups"]}'
                        for i, contract in enumerate(contracts_data["information"])
                    }
                ),
            }
        )
