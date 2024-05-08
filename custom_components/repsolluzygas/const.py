import logging
from datetime import timedelta

LOGGER = logging.getLogger(__name__)

DOMAIN = "repsolluzygas"
LOGIN_URL = "https://gigya.repsolluzygas.com/accounts.login"
CONTRACTS_URL = "https://areacliente.repsolluzygas.com/api/v2/houses"
HOUSES_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}"
INVOICES_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}/products/{}/invoices?limit=1"
COSTS_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}/products/{}/consumption/accumulated"
NEXT_INVOICE_URL = "https://areacliente.repsolluzygas.com/api/v2/houses/{}/products/{}/consumption/invoice-estimate"
UPDATE_INTERVAL = timedelta(minutes=120)
# Common headers used across multiple requests
COMMON_HEADERS = {
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    "sec-ch-ua": "^\\^Google",
    "sec-ch-ua-mobile": "?0",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
    "Market": "ML",
}

# Specific headers for async_login
LOGIN_HEADERS = {
    **COMMON_HEADERS,
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "*/*",
    "Origin": "https://areacliente.repsolluzygas.com",
    "Sec-Fetch-Site": "same-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
}

# Specific headers for async_get_contracts
CONTRACTS_HEADERS = {
    **COMMON_HEADERS,
    "UID": "UID_PLACEHOLDER",  # This should be set dynamically
    "signature": "SIGNATURE_PLACEHOLDER",  # This should be set dynamically
    "signatureTimestamp": "TIMESTAMP_PLACEHOLDER",  # This should be set dynamically
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://areacliente.repsolluzygas.com/mis-hogares",
    "Accept-Language": "en-US,en;q=0.9",
    "x-origin": "WEB",
    "Accept": "application/json, text/plain, */*",
}
