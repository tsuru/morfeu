import os

from pymongo import MongoClient

MONGODB_URI = os.getenv("DBAAS_MONGODB_ENDPOINT", "mongodb://localhost:27017/")

client = MongoClient(MONGODB_URI)
db = client['morfeu']

config = db["config"].find_one() or {}

HIPACHE_REDIS_HOST = config.get("hipache_redis_host", "localhost")
HIPACHE_REDIS_PORT = int(config.get("hipache_redis_port", "6379"))

ESEARCH_HOST = config.get("elastic_search_host", "localhost")
TIMEOUT = int(config.get("timeout", "30"))
TIME_RANGE_IN_HOURS = config.get("time_range_in_hours", "1")

TSURU_TOKEN = os.getenv("TSURU_TOKEN", "token")
TSURU_HOST = os.getenv("TSURU_HOST", "http://localhost")
TSURU_APP_PROXY = config.get("app_proxy", "")
TSURU_APP_PROXY_URL = config.get("proxy_url", "")

POOL_WHITELIST = config.get("pool_whitelist", "")
PLATFORM_BLACKLIST = config.get("platform_blacklist", "static").split(',')
SLEEP_TIME = int(config.get("sleep_time", "60"))
APP_WHITELIST = config.get("app_whitelist", '').split(',')

DOMAIN = config.get("domain", "")
