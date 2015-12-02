import requests
import os
import logging
import redis
import dateutil.parser
import datetime
import pytz

from morfeu.tsuru.client import TsuruClient

HIPACHE_REDIS_HOST = os.getenv("HIPACHE_REDIS_HOST", "localhost")
HIPACHE_REDIS_PORT = int(os.getenv("HIPACHE_REDIS_PORT", "6379"))

ESEARCH_HOST = os.getenv("MORFEU_ESEARCH_HOST", "localhost")
TIMEOUT = int(os.getenv("MORFEU_TIMEOUT", "30"))
TIME_RANGE_IN_HOURS = os.getenv("TIME_RANGE_IN_HOURS", "1")

LOG = logging.getLogger(__name__)

tsuru_client = TsuruClient(timeout=TIMEOUT)


class TsuruApp(object):

    def __init__(self, name=None, dry=False, timeout=10):
        self.units = []
        self.dry = dry
        self.name = name
        self.timeout = timeout
        self.started = True
        self.ip = None
        self.pool = None
        self.hosts = []

        self.__load_info()

    def __unicode__(self):
        return u"{0}".format(self.name)

    def __load_info(self):
        app_info = tsuru_client.get_app(self.name)
        self.ip = app_info.get("ip")
        self.pool = app_info.get("pool")

        for unit in app_info.get("units"):
            self.hosts.append(unit["Address"]["Host"])
            if unit["Status"] == 'stopped':
                self.started = False

    def __first_deploy(self):
        ret = tsuru_client.list_deploys(app_name=self.name)
        if ret:
            first_deploy = ret[-1]
            return first_deploy
        else:
            return {}

    def stop(self):
        if not self.dry:
            if self.started:
                tsuru_client.sleep_app(app_name=self.name)
            else:
                LOG.info("App {} is already stopped".format(self.name))
        else:
            LOG.info("Faking stop to app {0}".format(self.name))

    def should_go_to_bed(self, time_range=TIME_RANGE_IN_HOURS):
        payload = {
            "query": {
                "filtered": {
                    "filter": {
                        "and": [
                            {"range": {"@timestamp": {"gt": "now-{}h".format(time_range)}}},
                            {"term": {"app.raw": self.name}}
                        ]
                    }
                }
            }
        }

        url = "http://{0}/.measure-tsuru-*/response_time/_search".format(ESEARCH_HOST)
        req = requests.post(url, json=payload, timeout=self.timeout)
        response = req.json()
        hits = response.get("hits", {})
        hits_ = hits.get("hits", [])
        LOG.info("Getting hits for \"{}\"".format(self.name))

        if hits_:
            return False
        else:
            # check the last deploy timestamp
            first_deploy = self.__first_deploy()
            if first_deploy:
                timestamp = dateutil.parser.parse(first_deploy.get("Timestamp", ""))
                today = datetime.datetime.now(pytz.utc)
                delta = today - timestamp
                delta_hours = delta.total_seconds() / 60 / 60

                if delta_hours <= int(time_range):
                    LOG.info("Ignoring \"{}\", created at \"{}\"".format(self.name, timestamp))
                    return False
                else:
                    return True
            else:
                return True

    def re_route(self, tsuru_app_proxy=None):

        if not self.dry:
            redis_client = redis.StrictRedis(
                host=HIPACHE_REDIS_HOST, port=HIPACHE_REDIS_PORT, socket_timeout=self.timeout)

            key = "frontend:{0}".format(self.ip)

            # trim
            redis_client.ltrim(key, 0, 0)

            # update route
            redis_client.rpush(key, "http://{0}".format(tsuru_app_proxy.ip))

            try:
                redis_client.close()
            except:
                pass

            LOG.info("App {0} re-routed to {1}".format(self.name, tsuru_app_proxy.ip))
        else:
            LOG.info("App {0} re-routed (fake) to {1}".format(self.name, tsuru_app_proxy.ip))
