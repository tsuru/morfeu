import requests
import logging

from morfeu.tsuru.client import TsuruClient
from morfeu.settings import TIME_RANGE_IN_HOURS, ESEARCH_HOST, TIMEOUT

LOG = logging.getLogger(__name__)

tsuru_client = TsuruClient()


class TsuruApp(object):

    def __init__(self, name=None, dry=False):
        self.units = []
        self.dry = dry
        self.name = name
        self.timeout = TIMEOUT
        self.started = True
        self.ip = None
        self.pool = None

        self.__load_info()

    def __unicode__(self):
        return u"{0}".format(self.name)

    def __load_info(self):
        app_info = tsuru_client.get_app(self.name)
        self.ip = app_info.get("ip")
        self.pool = app_info.get("pool")

        for unit in app_info.get("units"):
            if unit["Status"] == 'stopped':
                self.started = False

    def sleep(self):
        if not self.dry:
            if self.started:
                tsuru_client.sleep_app(app_name=self.name)
            else:
                LOG.info("App {} is already asleep".format(self.name))
        else:
            LOG.info("Faking sleep to app {0}".format(self.name))

    def stop(self):
        if not self.dry:
            if self.started:
                tsuru_client.stop_app(app_name=self.name)
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
            return True
