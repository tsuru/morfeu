import os

from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_ENDPOINT", "mongodb://localhost:27017/")

client = MongoClient(MONGODB_URI)
db = client['morfeudb']

config = db["config"].find_one() or {}

ESEARCH_HOST = config.get("elastic_search_host", "localhost")
TIMEOUT = int(config.get("timeout", "30"))
TIME_RANGE_IN_HOURS = int(config.get("time_range_in_hours", "1"))

TSURU_TOKEN = os.getenv("TSURU_TOKEN", "token")
TSURU_HOST = os.getenv("TSURU_HOST", "http://localhost")
TSURU_APP_PROXY = config.get("app_proxy", "")
TSURU_APP_PROXY_URL = config.get("proxy_url", "")

POOLS = config.get("pools", "")
STATIC_PLATFORM_NAME = config.get("static_platform_name", "static")
SLEEP_TIME = int(config.get("sleep_time", "60"))
SKIP_APPS = config.get("skip_apps", '').split(',')

DOMAIN = config.get("domain", "")
