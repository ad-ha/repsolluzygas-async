import logging
from datetime import timedelta

LOGGER = logging.getLogger(__name__)

DOMAIN = "repsolluzygas"
LOGIN_URL = "https://login.repsol.es/accounts.login"
BASE_API_URL = "https://areacliente.repsol.es/api/proxy/"
CONTRACTS_URL = f"{BASE_API_URL}houses"
HOUSES_URL = f"{BASE_API_URL}houses/{{}}"
INVOICES_URL = f"{BASE_API_URL}houses/{{}}/products/{{}}/invoices?limit=10"
COSTS_URL = f"{BASE_API_URL}houses/{{}}/products/{{}}/consumption/accumulated"
NEXT_INVOICE_URL = (
    f"{BASE_API_URL}houses/{{}}/products/{{}}/consumption/invoice-estimate"
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
    "gmid": "gmid.ver4.AtLtj-S6Bg.5nGvNQiXUMMFW5Z7o3A2mIP4kjnCrm-CtwscvU8NC2FhNb6dxX09HfdUzL3pI26o.SHj7Fh8B8OK5xpZyFyZUX6mtQeRTaEhz_FtBwVbr_-5l6b8u6iBOOR6aoh7B-2kdAVrB3ro8ysuq1sEGjriOfQ.sc3",
    "ucid": "fXMDPs47yZukqcRaCm6LKQ",
    "hasGmid": "ver4",
    "gig_bootstrap_3_jm2BKK8jIBHi9nXHP8OsQ-HNgJKWxgd1o6kbNqsWvhUy0hhD1eeCpHC-qCrrWe8D": "login_ver4",
}

# Login data for async_login
LOGIN_DATA = {
    "targetEnv": "jssdk",
    "includeUserInfo": "true",
    "include": "profile,data,preferences,",
    "lang": "en",
    "sdk": "js_latest",
    "APIKey": "3_jm2BKK8jIBHi9nXHP8OsQ-HNgJKWxgd1o6kbNqsWvhUy0hhD1eeCpHC-qCrrWe8D",
    "format": "json",
}
