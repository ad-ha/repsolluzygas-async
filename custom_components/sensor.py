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
            "name": "Average daily amount",
            "variable": "averageAmount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Number of contracts",
            "variable": "number_of_contracts",
            "unit": "",
            "is_master": False,
        },
        {
            "name": "Last invoice",
            "variable": "last_invoice_amount",
            "unit": "€",
            "is_master": False,
        },
        {
            "name": "Last invoice was paid",
            "variable": "last_invoice_paid",
            "unit": "",
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
        if self.variable == "number_of_contracts":
            return data.get("contracts", {}).get("number_of_contracts")

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
        if self.variable in ["last_invoice_amount", "last_invoice_paid"]:
            invoices = data.get("invoices", [])
            if invoices:
                invoice = invoices[0]
                if self.variable == "last_invoice_amount":
                    return invoice.get("amount")
                elif self.variable == "last_invoice_paid":
                    return "Yes" if invoice.get("status") == "PAID" else "No"

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
