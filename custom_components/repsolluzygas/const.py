import logging
from datetime import timedelta

LOGGER = logging.getLogger(__name__)

DOMAIN = "repsolluzygas"
LOGIN_URL = "https://gigya.repsolluzygas.com/accounts.login"
BASE_API_URL = "https://pro-wally-back.cloudapp.repsol.com/v2/"
CONTRACTS_URL = f"{BASE_API_URL}houses"
HOUSES_URL = f"{BASE_API_URL}houses/{{}}"
INVOICES_URL = f"{BASE_API_URL}houses/{{}}/products/{{}}/invoices?limit=1"
COSTS_URL = f"{BASE_API_URL}houses/{{}}/products/{{}}/consumption/accumulated"
NEXT_INVOICE_URL = (
    f"{BASE_API_URL}houses/{{}}/products/{{}}/consumption/invoice-estimate"
)
VIRTUAL_BATTERY_DETAILS_URL = (
    f"{BASE_API_URL}houses/{{}}/products/{{}}/virtual-battery/detail"
)
VIRTUAL_BATTERY_HISTORY_URL = (
    f"{BASE_API_URL}houses/{{}}/products/{{}}/virtual-battery/history"
)
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
    "Origin": "https://areacliente.repsol.es",
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
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "https://areacliente.repsolluzygas.com/mis-hogares",
    "Accept-Language": "en-US,en;q=0.9,es-ES;q=0.8,es;q=0.7,pt-PT;q=0.6,pt;q=0.5",
    "x-origin": "WEB",
    "Accept": "application/json, text/plain, */*",
}

# Cookies data for API access
COOKIES_CONST = {
    "gmid": "gmid.ver4.AcbHSBMhFw.1PO5AEWAU-E5wcBXeuZT_c_uz5VVE_t3ZPwM8tKdJgOFsVf0lDmNsBlpecXxwdf0.Zo36FXG0Nnu7Dxd6z0ZedVvVW6U-G9DQlNq1ofie-ez5wHw5SuID3P6jzqbLsuL7BIPqFup0n6D4LSsjS7YKPg.sc3",
    "ucid": "TiA7xpk2tJCJIn50B0CuzQ",
    "hasGmid": "ver4",
    "gig_bootstrap_3_2MAJfXPA8zGLzfv2TRlhKGs3d6WdNsLU8unCCIGFhXMo9Ry49fG9k-aWG4SQY9_B": "gigya_ver4",
}

# Login data for async_login
LOGIN_DATA = {
    "targetEnv": "jssdk",
    "includeUserInfo": "true",
    "lang": "en",
    "APIKey": "3_2MAJfXPA8zGLzfv2TRlhKGs3d6WdNsLU8unCCIGFhXMo9Ry49fG9k-aWG4SQY9_B",
    "format": "json",
}
