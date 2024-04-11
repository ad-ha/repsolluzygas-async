"""Platform for Repsol Luz y Gas sensor integration."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity
from . import DOMAIN, RepsolLuzYGasAPI

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Repsol Luz y Gas sensors based on a config entry."""
    api: RepsolLuzYGasAPI = hass.data[DOMAIN][entry.entry_id]
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    # List to hold all our sensors
    sensors = []

    # Define sensor names, variables, units, and if it's a master sensor
    sensor_definitions = [
        {"name": "Amount", "variable": "amount", "unit": "€", "is_master": True},
        {
            "name": "Consumption",
            "variable": "consumption",
            "unit": "kWh",
            "is_master": False,
        },
        {
            "name": "Total Days",
            "variable": "totalDays",
            "unit": "days",
            "is_master": False,
        },
        {
            "name": "Amount Variable",
            "variable": "amountVariable",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Amount Fixed",
            "variable": "amountFixed",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Average Daily Amount",
            "variable": "averageAmount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Number of Contracts",
            "variable": "numberOfContracts",
            "unit": "",
            "is_master": False,
        },
        {
            "name": "Last Invoice",
            "variable": "lastInvoiceAmount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Last Invoice Paid",
            "variable": "lastInvoicePaid",
            "unit": "",
            "is_master": False,
        },
        {
            "name": "Next Invoice Amount",
            "variable": "nextInvoiceAmount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Next Invoice Variable Amount",
            "variable": "nextInvoiceVariableAmount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Next Invoice Fixed Amount",
            "variable": "nextInvoiceFixedAmount",
            "unit": "€",
            "is_master": False,
        },
    ]

    for sensor_def in sensor_definitions:
        sensors.append(
            RepsolLuzYGasSensor(
                coordinator=coordinator,
                name=sensor_def["name"],
                variable=sensor_def["variable"],
                unit=sensor_def["unit"],
                is_master=sensor_def["is_master"],
            )
        )

    async_add_entities(sensors, True)


class RepsolLuzYGasSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Repsol Luz y Gas Sensor."""

    def __init__(self, coordinator, name, variable, unit, is_master):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Repsol - {name}"
        self.variable = variable
        self._attr_unit_of_measurement = unit
        self.is_master = is_master

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data

        # Accessing contracts data
        if self.variable == "numberOfContracts":
            return data.get("contracts", {}).get("numberOfContracts")

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
        return f"{self.coordinator.name}_{self.variable}"

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._attr_unit_of_measurement

    def update(self):
        """Update the sensor."""
        # In the new structure, updates are handled by the CoordinatorEntity.
        pass
