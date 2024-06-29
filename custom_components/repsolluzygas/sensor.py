"""Platform for Repsol Luz y Gas sensor integration."""
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.entity import DeviceInfo
from . import DOMAIN, LOGGER, RepsolLuzYGasAPI
import re


async def async_setup_entry(hass, entry, async_add_entities):
    """Set up Repsol Luz y Gas sensors based on a config entry."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    api = hass.data[DOMAIN][entry.entry_id]["api"]

    if not hasattr(api, "async_get_contracts"):
        LOGGER.error("API object is not set correctly.")
        return

    contract_data = await api.async_get_contracts()
    if not contract_data:
        LOGGER.error("No contract data available.")
        return

    house_data = await api.async_get_houseDetails(contract_data["house_id"])
    if not house_data:
        LOGGER.error("No house data available.")
        return

    # List to hold all sensors
    sensors = []

    # Define sensor names, variables, units, and if it's a master sensor
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
        {
            "name": "Contract Status",
            "variable": "status",
            "device_class": None,
            "is_master": False,
        },
        {
            "name": "Power",
            "variable": "power",
            "device_class": SensorDeviceClass.POWER,
            "is_master": False,
        },
        {
            "name": "Tariff",
            "variable": "fee",
            "device_class": None,
            "is_master": False,
        },
        {
            "name": "Power Price Punta",
            "variable": "pricesPowerPunta",
            "device_class": SensorDeviceClass.MONETARY,
            "is_master": False,
        },
        {
            "name": "Power Price Valle",
            "variable": "pricesPowerValle",
            "device_class": SensorDeviceClass.MONETARY,
            "is_master": False,
        },
        {
            "name": "Energy Price",
            "variable": "pricesEnergyAmount",
            "device_class": SensorDeviceClass.MONETARY,
            "is_master": False,
        },
    ]

    for contract in house_data.get("contracts", []):
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
                    contract_id=contract["code"],
                    cups=contract["cups"],
                    contract_data=contract,
                )
            )

    for contract in house_data.get("contracts", []):
        if "sva" in contract:
            for sva_detail in contract["sva"]:
                sensors.append(
                    SVASensor(
                        coordinator=coordinator,
                        house_id=contract_data["house_id"],
                        name=sva_detail["name"],
                        code=sva_detail["code"],
                    )
                )

    for contract in contract_data["information"]:
        virtual_battery_data = await api.async_get_virtual_battery_history(
            contract_data["house_id"], contract["contract_id"]
        )
        if virtual_battery_data:
            virtual_battery_sensors = [
                {
                    "name": "Virtual Battery Amount Pending",
                    "variable": "pendingAmount",
                    "device_class": SensorDeviceClass.MONETARY,
                },
                {
                    "name": "Virtual Battery kWh Available",
                    "variable": "kwhAvailable",
                    "device_class": SensorDeviceClass.ENERGY,
                },
                {
                    "name": "Virtual Battery Amount Available",
                    "variable": "amountAvailable",
                    "device_class": SensorDeviceClass.MONETARY,
                },
                {
                    "name": "Virtual Battery Total Amount Redeemed",
                    "variable": "appliedAmount",
                    "device_class": SensorDeviceClass.MONETARY,
                },
                {
                    "name": "Virtual Battery Total kWh Redeemed",
                    "variable": "kwhRedeemed",
                    "device_class": SensorDeviceClass.ENERGY,
                },
                {
                    "name": "Virtual Battery Total kWh Charged",
                    "variable": "totalKWh",
                    "device_class": SensorDeviceClass.ENERGY,
                },
                {
                    "name": "Virtual Battery Excedents Price",
                    "variable": "excedentsPrice",
                    "device_class": SensorDeviceClass.MONETARY,
                },
            ]

            for sensor_def in virtual_battery_sensors:
                sensors.append(
                    VirtualBatterySensor(
                        coordinator=coordinator,
                        name=sensor_def["name"],
                        variable=sensor_def["variable"],
                        device_class=sensor_def["device_class"],
                        house_id=contract_data["house_id"],
                        contract_id=contract["contract_id"],
                    )
                )

            # Extract the latest discharge values for "Last Amount Redeemed" and "Last kWh Redeemed"
            last_redeemed = max(
                virtual_battery_data.get("discounts", {}).get("data", []),
                key=lambda x: x["billingDate"],
                default=None,
            )

            if last_redeemed:
                sensors.append(
                    VirtualBatterySensor(
                        coordinator=coordinator,
                        name="Last Amount Redeemed",
                        variable="amount",
                        device_class=SensorDeviceClass.MONETARY,
                        house_id=contract_data["house_id"],
                        contract_id=contract["contract_id"],
                        coupon_data=last_redeemed,
                    )
                )
                sensors.append(
                    VirtualBatterySensor(
                        coordinator=coordinator,
                        name="Last kWh Redeemed",
                        variable="kWh",
                        device_class=SensorDeviceClass.ENERGY,
                        house_id=contract_data["house_id"],
                        contract_id=contract["contract_id"],
                        coupon_data=last_redeemed,
                    )
                )

    async_add_entities(sensors, True)
    LOGGER.info(f"Added {len(sensors)} sensors")


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
        contract_data,
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
        self.contract_data = contract_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        # Accessing costs data
        if self.variable in [
            "amount",
            "consumption",
            "totalDays",
            "amountVariable",
            "amountFixed",
            "averageAmount",
        ]:
            return (
                self.coordinator.data.get(self.contract_id, {})
                .get("costs", {})
                .get(self.variable)
            )

        # Accessing the latest invoice data
        if self.variable in ["lastInvoiceAmount", "lastInvoicePaid"]:
            invoices = self.coordinator.data.get(self.contract_id, {}).get(
                "invoices", []
            )
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
            nextInvoice = self.coordinator.data.get(self.contract_id, {}).get(
                "nextInvoice", {}
            )
            if nextInvoice:
                if self.variable == "nextInvoiceAmount":
                    return nextInvoice.get("amount")
                elif self.variable == "nextInvoiceVariableAmount":
                    return nextInvoice.get("amountVariable")
                elif self.variable == "nextInvoiceFixedAmount":
                    return nextInvoice.get("amountFixed")

        # Accessing electricity contract data
        if self.contractType == "ELECTRICITY":
            if self.variable in ["status", "power", "fee"]:
                return self.contract_data.get(self.variable, "Unavailable")
            if self.variable == "pricesPower":
                return self.parse_power_prices(
                    self.contract_data.get("prices", {}).get("power", [])
                )
            if self.variable == "pricesEnergy":
                return self.parse_energy_prices(
                    self.contract_data.get("prices", {}).get("energy", [])
                )
            if self.variable == "pricesPowerPunta":
                return self.parse_power_prices(
                    self.contract_data.get("prices", {}).get("power", []), 0
                )
            if self.variable == "pricesPowerValle":
                return self.parse_power_prices(
                    self.contract_data.get("prices", {}).get("power", []), 1
                )
            if self.variable == "pricesEnergyAmount":
                return self.parse_energy_prices(
                    self.contract_data.get("prices", {}).get("energy", []), 0
                )

        return "Unavailable"

    def parse_power_prices(self, prices, index=None):
        """Parse power prices to extract only the amount."""
        parsed_prices = []
        for price in prices:
            match = re.search(r"(\d+,\d+)", price)
            if match:
                parsed_prices.append(match.group(1).replace(",", "."))
        if index is not None:
            return parsed_prices[index] if index < len(parsed_prices) else "Unavailable"
        return parsed_prices

    def parse_energy_prices(self, prices, index=None):
        """Parse energy prices to extract only the amount."""
        parsed_prices = []
        for price in prices:
            match = re.search(r"(\d+,\d+)", price)
            if match:
                parsed_prices.append(match.group(1).replace(",", "."))
        if index is not None:
            return parsed_prices[index] if index < len(parsed_prices) else "Unavailable"
        return parsed_prices

    def format_price(self, price):
        """Format price to 6 decimal places."""
        try:
            return f"{float(price):.6f}"
        except (ValueError, TypeError):
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
            "configuration_url": f"https://areacliente.repsol.es/productos-y-servicios",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement based on the device class."""
        if self._attr_device_class == SensorDeviceClass.ENERGY:
            return "kWh"
        elif self._attr_device_class == SensorDeviceClass.MONETARY:
            return "EUR"
        elif self._attr_device_class == SensorDeviceClass.POWER:
            return "kW"
        elif self._attr_device_class == SensorDeviceClass.DURATION:
            return "d"
        return None

    def update(self):
        """Update the sensor (handled by the Coordinator)."""
        pass


class VirtualBatterySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Virtual Battery Sensor."""

    def __init__(
        self,
        coordinator,
        name,
        variable,
        device_class,
        house_id,
        contract_id,
        coupon_data=None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_name = f"Repsol {house_id} {name}"
        self.variable = variable
        self._attr_device_class = device_class
        self.house_id = house_id
        self.contract_id = contract_id
        self.coupon_data = coupon_data

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data.get(self.contract_id, {}).get(
            "virtual_battery_history", {}
        )
        discounts = data.get("discounts", {})
        excedents = data.get("excedents", {})

        if self.coupon_data:
            return self.coupon_data.get(self.variable, "Unavailable")

        if self.variable == "pendingAmount":
            return next(
                (
                    c["pendingAmount"]
                    for c in discounts.get("contracts", [])
                    if c["productCode"] == self.contract_id
                ),
                "Unavailable",
            )

        if self.variable == "kwhAvailable":
            pending_amount = next(
                (
                    c["pendingAmount"]
                    for c in discounts.get("contracts", [])
                    if c["productCode"] == self.contract_id
                ),
                0,
            )
            conversion_price = next(
                (d["conversionPrice"] for d in excedents.get("data", [])), "Unavailable"
            )
            return (
                round(pending_amount / conversion_price, 2)
                if conversion_price
                else "Unavailable"
            )

        if self.variable == "amountAvailable":
            total_amount = excedents.get("totalAmount", 0)
            applied_amount = excedents.get("appliedAmount", 0)
            pending_amount = next(
                (
                    c["pendingAmount"]
                    for c in discounts.get("contracts", [])
                    if c["productCode"] == self.contract_id
                ),
                0,
            )
            return total_amount - applied_amount - pending_amount

        if self.variable == "appliedAmount":
            return excedents.get("appliedAmount", "Unavailable")

        if self.variable == "kwhRedeemed":
            applied_amount = excedents.get("appliedAmount", 0)
            conversion_price = next(
                (d["conversionPrice"] for d in excedents.get("data", [])), "Unavailable"
            )
            return (
                round(applied_amount / conversion_price, 2)
                if conversion_price
                else "Unavailable"
            )

        if self.variable == "totalKWh":
            return round(excedents.get("totalkWh", 0), 2)

        if self.variable == "excedentsPrice":
            return next(
                (d["conversionPrice"] for d in excedents.get("data", [])), "Unavailable"
            )

        return "Unavailable"

    @property
    def unique_id(self):
        """Return a unique ID."""
        if self.coupon_data:
            return f"{self.house_id}_{self.contract_id}_{self.variable}_vb"
        return f"{self.house_id}_{self.contract_id}_{self.variable}_vb"

    @property
    def device_info(self):
        """Return information about the device."""
        return {
            "identifiers": {
                (DOMAIN, f"virtual_battery_{self.house_id}_{self.contract_id}")
            },
            "name": f"Virtual Battery - {self.house_id}",
            "manufacturer": "Repsol Luz y Gas",
            "model": "Virtual Battery",
            "serial_number": f"{self.house_id}",
            "configuration_url": f"https://areacliente.repsol.es/productos-y-servicios",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement based on the device class."""
        if self._attr_device_class == SensorDeviceClass.ENERGY:
            return "kWh"
        elif self._attr_device_class == SensorDeviceClass.MONETARY:
            return "EUR"
        return None


class SVASensor(CoordinatorEntity, SensorEntity):
    """Sensor for displaying SVA details of a house."""

    def __init__(self, coordinator, house_id, name, code):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.house_id = house_id
        self._attr_name = f"{name}"
        self.code = code

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._attr_name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self.code

    @property
    def unique_id(self):
        """Return a unique ID for this sensor."""
        return f"{self.house_id}_{self.code}"

    @property
    def device_info(self):
        """Return device info to group sensors under a single device."""
        return {
            "identifiers": {(DOMAIN, self.house_id)},
            "name": f"SVA - {self.house_id}",
            "manufacturer": "Repsol Luz y Gas",
            "model": "SVAs",
            "serial_number": f"{self.house_id}",
            "configuration_url": f"https://areacliente.repsol.es/productos-y-servicios",
        }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement based on the device class."""
        return None
