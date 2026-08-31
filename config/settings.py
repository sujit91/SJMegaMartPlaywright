import os

BASE_URL = os.getenv(
    "BASE_URL",
    "https://sujitjena90.github.io/SujitTestingAutomation/",
).rstrip("/") + "/"

DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "20000"))
HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"

DEMO_USER = os.getenv("DEMO_USER", "admin")
DEMO_PASSWORD = os.getenv("DEMO_PASSWORD", "admin")
