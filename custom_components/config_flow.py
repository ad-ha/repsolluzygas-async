from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant
import voluptuous as vol
import logging

from .const import (
    DOMAIN,
    LOGGER,
)  # Make sure you have a DOMAIN constant in your const.py
from . import RepsolLuzYGasAPI  # Import your API class


class RepsolConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Manage the Repsol Luz y Gas config flow."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_CLOUD_POLL

    def __init__(self):
        self.api = None  # Initialize the api attribute to None

    async def async_step_user(self, user_input=None):
        errors = {}
        if user_input is not None:
            LOGGER.debug("Credentials provided: %s", user_input)
            # Assume credentials validation and API client initialization occur here
            contracts = []  # Initialize contracts to an empty list as a default
            try:
                LOGGER.debug("Trying to get contracts")
                fetched_contracts = (
                    await self.api.async_get_contracts()
                )  # Fetch contracts
                if fetched_contracts is not None:
                    contracts = (
                        fetched_contracts  # Update contracts if fetch was successful
                    )
                else:
                    LOGGER.error("Failed to fetch contracts: Received None")
                    errors["base"] = "fetch_contracts_failed"
                    return self.async_show_form(step_id="user", errors=errors)
            except Exception as e:
                LOGGER.error("Exception when fetching contracts: %s", e)
                errors["base"] = "fetch_contracts_failed"
                return self.async_show_form(step_id="user", errors=errors)

            # Now contracts is guaranteed to be defined
            if len(contracts) > 1:
                return await self.async_step_contract()
            elif len(contracts) == 1:
                # Proceed directly if only one contract is available
                # Additional logic to handle a single contract scenario
                pass
            else:
                # Handle case where no contracts are fetched
                LOGGER.error("No contracts were fetched.")
                errors["base"] = "no_contracts_found"
                return self.async_show_form(step_id="user", errors=errors)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("username"): str,
                    vol.Required("password"): str,
                }
            ),
            errors=errors,
        )

    async def async_step_contract(self, user_input=None):
        errors = {}
        LOGGER.debug("Entering async_step_contract with user_input: %s", user_input)

        if user_input is not None:
            # Set the selected house_id and contract_id in the API client
            self.api.set_contract_details(
                user_input["house_id"], user_input["contract_id"]
            )

            # Here, you can perform any additional operations needed with the API client
            # now that it has been fully initialized with house_id and contract_id

            # Finally, create the configuration entry with all necessary information
            # including the selected house_id and contract_id
            return self.async_create_entry(
                title=f"Contract {user_input['contract_id']}",
                data={
                    "username": self.credentials["username"],
                    "password": self.credentials["password"],
                    "house_id": user_input["house_id"],
                    "contract_id": user_input["contract_id"],
                },
            )

        # If we're here, it means the user has not yet submitted the form,
        # so we need to present the contract selection form to the user.
        # This involves fetching the available contracts and generating the form.

        try:
            LOGGER.debug("Attempting to fetch contracts")

            contracts = (
                await self.api.async_get_contracts()
            )  # Assuming this fetches a list of contracts
            LOGGER.debug("Successfully fetched contracts: %s", contracts)

            if not contracts:
                errors["base"] = "fetch_contracts_failed"
                return self.async_show_form(step_id="user", errors=errors)

            # Generate a dropdown list of contracts for the user to choose from
            contracts_dropdown = {
                contract[
                    "contract_id"
                ]: f"{contract['name']} ({contract['contract_id']})"
                for contract in contracts
            }

            return self.async_show_form(
                step_id="contract",
                data_schema=vol.Schema(
                    {
                        vol.Required("house_id"): vol.In(
                            {
                                contract["house_id"]: contract["house_id"]
                                for contract in contracts
                            }
                        ),
                        vol.Required("contract_id"): vol.In(contracts_dropdown),
                    }
                ),
                errors=errors,
            )
        except Exception as e:
            LOGGER.error("Failed to fetch contracts: %s", e)
            errors["base"] = "unknown_error"

        if errors:
            return self.async_show_form(step_id="contract", errors=errors)
