import logging

from morfeu.tsuru.client import TsuruClient
from morfeu.settings import TIME_RANGE_IN_HOURS, TIMEOUT
from morfeu.graylog import GraylogClient

LOG = logging.getLogger(__name__)

tsuru_client = TsuruClient()


class TsuruApp(object):

    def __init__(self, name=None, dry=False):
        self.dry = dry
        self.name = name
        self.timeout = TIMEOUT

        self.__load_info()

    def __unicode__(self):
        return u"{0}".format(self.name)

    def __load_info(self):
        app_info = tsuru_client.get_app(self.name)
        self.ip = app_info.get("ip", "")
        self.pool = app_info.get("pool", "")
        self.cname = app_info.get("cname", [])

    def sleep(self):
        if self.dry:
            LOG.info("Faking sleep to app {0}".format(self.name))
        else:
            tsuru_client.sleep_app(app_name=self.name)

    def stop(self):
        if self.dry:
            LOG.info("Faking stop to app {0}".format(self.name))
        else:
            tsuru_client.stop_app(app_name=self.name)

    def should_go_to_bed(self, time_range=TIME_RANGE_IN_HOURS):
        results = GraylogClient(self).search()
        return len(results) == 0
