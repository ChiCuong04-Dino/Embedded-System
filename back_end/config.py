import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / '.env.local')

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")
ADAFRUIT_IO_USERNAME = os.getenv("ADAFRUIT_IO_USERNAME")
ADAFRUIT_IO_KEY = os.getenv("ADAFRUIT_IO_KEY")

# Adafruit IO URLs
POLLING_URL = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/feeds/es-ass.display-data"
CONTROL_URL = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/groups/es-ass/feeds/control-device/data"