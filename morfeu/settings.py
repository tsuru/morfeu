import os

from pymongo import MongoClient


client = MongoClient()
db = client['test-database']

config = db["config"].find_one()

HIPACHE_REDIS_HOST = config.get("hipache_redis_host", "localhost")
HIPACHE_REDIS_PORT = int(os.getenv("HIPACHE_REDIS_PORT", "6379"))

ESEARCH_HOST = os.getenv("MORFEU_ESEARCH_HOST", "localhost")
TIMEOUT = int(os.getenv("MORFEU_TIMEOUT", "30"))
TIME_RANGE_IN_HOURS = os.getenv("MORFEU_TIME_RANGE_IN_HOURS", "1")

TSURU_TOKEN = os.getenv("TSURU_TOKEN", "token")
TSURU_HOST = os.getenv("TSURU_HOST", "http://localhost")
TSURU_APP_PROXY = os.getenv("TSURU_APP_PROXY", "")
TSURU_APP_PROXY_URL = os.getenv("TSURU_APP_PROXY_URL", "")

POOL_WHITELIST = os.getenv("POOL_WHITELIST", "")
PLATFORM_BLACKLIST = os.getenv("PLATFORM_BLACKLIST", "static").split(',')
SLEEP_TIME = int(os.getenv("MORFEU_SLEEP_TIME", "60"))
APP_WHITELIST = os.getenv("APP_WHITELIST", '').split(',')

DOMAIN = os.getenv("DOMAIN", "")
