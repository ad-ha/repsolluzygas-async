"""Integration for Repsol Luz y Gas."""
import aiohttp
import asyncio

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from aiohttp.client_exceptions import ClientError

from .const import (
    DOMAIN,
    LOGGER,
    LOGIN_URL,
    CONTRACTS_URL,
    HOUSES_URL,
    INVOICES_URL,
    COSTS_URL,
    NEXT_INVOICE_URL,
    VIRTUAL_BATTERY_HISTORY_URL,
    UPDATE_INTERVAL,
    LOGIN_HEADERS,
    CONTRACTS_HEADERS,
    COOKIES_CONST,
    LOGIN_DATA,
)

PLATFORMS: list[str] = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    session = aiohttp.ClientSession()
    client = RepsolLuzYGasAPI(session, entry.data["username"], entry.data["password"])

    async def async_update_data_start():
        try:
            # Implement the logic to fetch all necessary data here.
            # This should return the combined data from all necessary endpoints.
            return await client.fetch_all_data()
        except Exception as e:
            raise UpdateFailed(f"Error fetching data: {e}")

    coordinator = DataUpdateCoordinator(
        hass,
        LOGGER,
        name="repsolluzygas",
        update_method=async_update_data_start,
        update_interval=UPDATE_INTERVAL,
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        "api": client,
        "coordinator": coordinator,
    }

    for platform in ["sensor"]:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setup(entry, platform)
        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)


async def async_update_data(client):
    async def update_data():
        """Fetch data."""
        try:
            async with asyncio.timeout(10):
                data = await client.fetch_data()
                return data
        except (ClientError, asyncio.TimeoutError) as err:
            LOGGER.error("Error fetching Repsol Luz y Gas data: %s", err)
            raise UpdateFailed(f"Error fetching data: {err}") from err

    return update_data


class RepsolLuzYGasAPI:
    """Class to communicate with Repsol Luz y Gas API."""

    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        """Initialize."""
        self.session = session
        self.username = username
        self.password = password
        self.uid = None
        self.signature = None
        self.timestamp = None

    cookies = COOKIES_CONST.copy()

    async def async_login(self):
        """Async login to Repsol API."""
        data = LOGIN_DATA.copy()
        data.update(
            {
                "loginID": self.username,
                "password": self.password,
            }
        )

        headers = LOGIN_HEADERS.copy()

        try:
            async with self.session.post(
                LOGIN_URL, headers=headers, cookies=self.cookies, data=data
            ) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    LOGGER.debug(f"Response: {data}")
                    self.uid = data["userInfo"]["UID"]
                    self.signature = data["userInfo"]["UIDSignature"]
                    self.timestamp = data["userInfo"]["signatureTimestamp"]
                else:
                    LOGGER.error(f"Unexpected response status: {response.status}")
                    return None
        except Exception as e:
            LOGGER.error(f"Error during login to Repsol API: {e}")
            return None

    async def async_get_contracts(self):
        """Retrieve contracts."""
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )

        url = CONTRACTS_URL

        contracts = {}

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    LOGGER.debug(f"Headers: {headers}")
                    if response.status == 200:
                        data = await response.json()

                        LOGGER.debug("Contracts Data %s", data)

                        if data:  # Check if data is not empty
                            data = data[0]
                            contracts["house_id"] = data["code"]
                            contracts["information"] = []

                            for contract in data.get("contracts", []):
                                info = {}
                                info["contract_id"] = contract["code"]
                                info["contractType"] = contract["contractType"]
                                info["cups"] = contract["cups"]
                                info["active"] = contract["status"] == "ACTIVE"
                                contracts["information"].append(info)

                            LOGGER.debug("Contracts Parsed %s", contracts)
                        else:
                            LOGGER.warning("No contract data received")
                    else:
                        LOGGER.error(
                            "Failed to fetch contracts data. HTTP Status: %s",
                            response.status,
                        )
                        return None
        except Exception as e:
            LOGGER.error("Error fetching contracts data: %s", e)
            return None

        return contracts

    async def async_get_houseDetails(self, house_id):
        """Fetch house details including contracts and SVA data."""
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )

        url = HOUSES_URL.format(house_id)

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        LOGGER.debug("House Data %s", response_data)
                        return response_data
                    else:
                        LOGGER.error(
                            "Failed to fetch house data. HTTP Status: %s",
                            response.status,
                        )
                        return None

        except Exception as e:
            LOGGER.error("Error fetching house data: %s", e)
            return None

    async def async_get_invoices(self, house_id, contract_id):
        """Retrieve the latest invoice for a given contract."""
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )
        url = INVOICES_URL.format(house_id, contract_id)

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        LOGGER.debug("Invoices Data %s", response_data)
                        return response_data
                    else:
                        LOGGER.error(
                            "Failed to fetch invoice data. HTTP Status: %s",
                            response.status,
                        )
                        return None

        except Exception as e:
            LOGGER.error("Error fetching invoice data: %s", e)
            return None

    async def async_get_costs(self, house_id, contract_id):
        """Retrieve cost data for a given contract."""
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )
        url = COSTS_URL.format(house_id, contract_id)
        data = {
            "totalDays": 0,
            "consumption": 0,
            "amount": 0,
            "amountVariable": 0,
            "amountFixed": 0,
            "averageAmount": 0,
        }

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        for var in data.keys():
                            data[var] = response_data.get(var, 0)

                        LOGGER.debug("Costs Data %s", data)
                    else:
                        LOGGER.error(
                            "Failed to fetch costs data. HTTP Status: %s",
                            response.status,
                        )
        except Exception as e:
            LOGGER.error("Error fetching costs data: %s", e)

        return data

    async def async_get_next_invoice(self, house_id, contract_id):
        """Retrieve cost data for a given contract."""
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )
        url = NEXT_INVOICE_URL.format(house_id, contract_id)
        data = {
            "amount": 0,
            "amountVariable": 0,
            "amountFixed": 0,
        }

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        for var in data.keys():
                            data[var] = response_data.get(var, 0)

                        LOGGER.debug("Next Invoice Data %s", data)
                    else:
                        LOGGER.debug(
                            "Failed to fetch next invoice data. HTTP Status: %s",
                            response.status,
                        )
        except Exception as e:
            LOGGER.debug("Error fetching next invoice data: %s", e)

        return data

    def extract_sva_ids(self, house_details):
        """Extract SVA IDs from house details response."""
        sva_ids = []
        for contract in house_details.get("contracts", []):
            for sva in contract.get("sva", []):
                sva_ids.append(sva["code"])
        return sva_ids

    async def async_get_virtual_battery_history(self, house_id, contract_id):
        headers = CONTRACTS_HEADERS.copy()
        headers.update(
            {
                "UID": self.uid,
                "signature": self.signature,
                "signatureTimestamp": self.timestamp,
            }
        )
        url = VIRTUAL_BATTERY_HISTORY_URL.format(house_id, contract_id)

        try:
            async with asyncio.timeout(10):
                async with self.session.get(
                    url, headers=headers, cookies=self.cookies
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()

                        LOGGER.debug("Virtual Battery History Data %s", response_data)
                        return response_data
                    else:
                        LOGGER.error(
                            "Failed to fetch Virtual Battery History data. HTTP Status: %s",
                            response.status,
                        )
                        return None

        except Exception as e:
            LOGGER.error("Error fetching Virtual Battery History data: %s", e)
            return None

    async def async_update(self):
        """Asynchronously update data from the Repsol API."""
        data = {
            "consumption": 0,
            "amount": 0,
            "amountVariable": 0,
            "amountFixed": 0,
            "averageAmount": 0,
        }

        # Log in and get contracts asynchronously
        uid, signature, timestamp = await self.async_login()
        contracts = await self.async_get_contracts(uid, signature, timestamp)

        if "information" in contracts:
            for contract in contracts["information"]:
                if not contract.get("active", False):
                    continue

                # Get costs asynchronously
                response = await self.async_get_costs(
                    uid,
                    signature,
                    timestamp,
                    contracts["house_id"],
                    contract["contract_id"],
                )
                for var in data:
                    data[var] += response.get(var, 0)

                if response.get("totalDays", 0) > 0:
                    data["totalDays"] = response["totalDays"]
                    data["averageAmount"] = round(response["averageAmount"], 2)

                nextInvoice = await self.async_get_next_invoice(
                    uid,
                    signature,
                    timestamp,
                    contracts["house_id"],
                    contract["contract_id"],
                )
                for var in data:
                    data[var] += nextInvoice.get(var, 0)

                if nextInvoice.get("amount", 0) > 0:
                    data["nextInvoiceAmount"] = nextInvoice["amount"]
                    data["nextInvoiceAmountVariable"] = nextInvoice["amountVariable"]
                    data["nextInvoiceAmountFixed"] = nextInvoice["amountFixed"]

            if len(contracts["information"]) > 0:
                # Get the last invoice asynchronously
                last_contract = contracts["information"][-1]

                invoices = await self.async_get_invoices(
                    uid,
                    signature,
                    timestamp,
                    contracts["house_id"],
                    last_contract["contract_id"],
                )
                if invoices:
                    data["lastInvoiceAmount"] = invoices[0]["amount"]
                    data["lastInvoicePaid"] = invoices[0]["status"] == "PAID"

        self.data = data
        LOGGER.debug("Sensor Data %s", self.data)

    async def fetch_all_data(self):
        """Fetch and combine all necessary data from the API."""
        try:
            await self.async_login()
            contracts_data = await self.async_get_contracts()

            if not contracts_data:
                raise Exception("Failed to fetch contracts.")

            all_data = {}
            for contract in contracts_data.get("information", []):
                house_id = contracts_data["house_id"]
                contract_id = contract["contract_id"]
                house_data = await self.async_get_houseDetails(house_id)
                invoices_data = await self.async_get_invoices(house_id, contract_id)
                costs_data = await self.async_get_costs(house_id, contract_id)
                next_invoice_data = await self.async_get_next_invoice(
                    house_id, contract_id
                )
                virtual_battery_history_data = (
                    await self.async_get_virtual_battery_history(house_id, contract_id)
                )

                all_data[contract_id] = {
                    "contracts": contract,
                    "house_data": house_data,
                    "invoices": invoices_data,
                    "costs": costs_data,
                    "nextInvoice": next_invoice_data,
                    "virtual_battery_history": virtual_battery_history_data,
                }
            LOGGER.debug("Sensor Data %s", all_data)

            return all_data

        except Exception as e:
            LOGGER.error(f"Error fetching all data: {e}")
            raise
