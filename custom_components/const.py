import logging
from datetime import timedelta

LOGGER = logging.getLogger(__name__)

DOMAIN = "repsolluzygas"
LOGIN_URL = "https://gigya.repsolluzygas.com/accounts.login"
CONTRACTS_URL = "https://areacliente.repsolluzygas.com/api/v2/houses"
INVOICES_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}/products/{}/invoices?limit=1"
COSTS_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}/products/{}/consumption/accumulated"
UPDATE_INTERVAL = timedelta(minutes=120)
