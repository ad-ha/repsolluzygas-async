"""Platform for Repsol Luz y Gas sensor integration."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN, LOGGER, RepsolLuzYGasAPI

import logging


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Repsol Luz y Gas sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    api = hass.data[DOMAIN][entry.entry_id]["api"]

    if not hasattr(api, "async_get_contracts"):
        LOGGER.error("API object is not set correctly.")
        return

    contract_data = await api.async_get_contracts()

    # List to hold all our sensors
    sensors = []

    # Define sensor names, variables, units, and if it's a master sensor
    for contract in contract_data[
        "information"
    ]:  # Correctly iterate over 'information' which contains the contracts
        sensor_definitions = [
            {
                "name": "Amount",
                "variable": "amount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": True,
            },
            {
                "name": "Consumption",
                "variable": "consumption",
                "device_class": SensorDeviceClass.ENERGY,
                "is_master": False,
            },
            {
                "name": "Total Days",
                "variable": "totalDays",
                "device_class": None,
                "is_master": False,
            },
            {
                "name": "Amount Variable",
                "variable": "amountVariable",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Amount Fixed",
                "variable": "amountFixed",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Average Daily Amount",
                "variable": "averageAmount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Last Invoice",
                "variable": "lastInvoiceAmount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Last Invoice Paid",
                "variable": "lastInvoicePaid",
                "device_class": None,
                "is_master": False,
            },
            {
                "name": "Next Invoice Amount",
                "variable": "nextInvoiceAmount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Next Invoice Variable Amount",
                "variable": "nextInvoiceVariableAmount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
            {
                "name": "Next Invoice Fixed Amount",
                "variable": "nextInvoiceFixedAmount",
                "device_class": SensorDeviceClass.MONETARY,
                "is_master": False,
            },
        ]

        for contract in contract_data["information"]:
            for sensor_def in sensor_definitions:
                sensors.append(
                    RepsolLuzYGasSensor(
                        coordinator=coordinator,
                        name=sensor_def["name"],
                        variable=sensor_def["variable"],
                        device_class=sensor_def["device_class"],
                        is_master=sensor_def["is_master"],
                        house_id=contract_data["house_id"],
                        contractType=contract["contractType"],
                        contract_id=contract["contract_id"],
                        cups=contract["cups"],
                    )
                )

    async_add_entities(sensors, True)


class RepsolLuzYGasSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Repsol Luz y Gas Sensor."""

    def __init__(
        self,
        coordinator,
        name,
        variable,
        device_class,
        is_master,
        house_id,
        contractType,
        contract_id,
        cups,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Repsol {cups} {name}"
        self.variable = variable
        self._attr_device_class = device_class
        self.is_master = is_master
        self.house_id = house_id
        self.contractType = contractType
        self.contract_id = contract_id
        self.cups = cups

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.contract_id, {})

        # Accessing costs data
        if self.variable in [
            "amount",
            "consumption",
            "totalDays",
            "amountVariable",
            "amountFixed",
            "averageAmount",
        ]:
            return data.get("costs", {}).get(self.variable)

        # Accessing the latest invoice data
        if self.variable in ["lastInvoiceAmount", "lastInvoicePaid"]:
            invoices = data.get("invoices", [])
            if invoices:
                invoice = invoices[0]
                if self.variable == "lastInvoiceAmount":
                    return invoice.get("amount")
                elif self.variable == "lastInvoicePaid":
                    return "Yes" if invoice.get("status") == "PAID" else "No"

        if self.variable in [
            "nextInvoiceAmount",
            "nextInvoiceVariableAmount",
            "nextInvoiceFixedAmount",
        ]:
            nextInvoice = data.get("nextInvoice", {})
            if nextInvoice:
                if self.variable == "nextInvoiceAmount":
                    return nextInvoice.get("amount")
                elif self.variable == "nextInvoiceVariableAmount":
                    return nextInvoice.get("amountVariable")
                elif self.variable == "nextInvoiceFixedAmount":
                    return nextInvoice.get("amountFixed")

        return "Unavailable"

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"{self.house_id}_{self.contract_id}_{self.variable}"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {(DOMAIN, f"{self.house_id}_{self.contract_id}")},
            "name": f"{self.contractType} - {self.cups}",
            "manufacturer": "Repsol Luz y Gas",
            "model": f"{self.contractType} - {self.cups}",
            "serial_number": f"{self.contract_id}",
            "configuration_url": f"https://areacliente.repsolluzygas.com/mis-hogares",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement based on the device class."""
        if self._attr_device_class == SensorDeviceClass.ENERGY:
            return "kWh"
        elif self._attr_device_class == SensorDeviceClass.MONETARY:
            return "EUR"
        return None

    def update(self):
        """Update the sensor (handled by the Coordinator)."""
        pass
