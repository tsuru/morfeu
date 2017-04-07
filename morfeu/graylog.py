import os
import logging
import arrow
from glogcli import graylog_api
from glogcli.utils import LOCAL_TIMEZONE
from morfeu.settings import TIME_RANGE_IN_HOURS

LOG = logging.getLogger(__name__)

class GraylogClient(object):
    def __init__(self, app):
        self.app = app

        scheme = "https"
        port = 443
        host = os.getenv("GRAYLOG_HOST")
        username = os.getenv("GRAYLOG_USER")
        password = os.getenv("GRAYLOG_PASSWORD")
        stream = os.getenv("GRAYLOG_STREAM")
        self.client = graylog_api.GraylogAPI(host=host, port=port, username=username, password=password, default_stream=stream, scheme=scheme)

    def search(self):
        query = self.__build_query()
        if not query:
            return []
        search_query = graylog_api.SearchQuery(search_range=self.__build_range(), query=self.__build_query(), limit=1, fields="")
        return self.client.search(search_query).messages

    def __build_query(self):
        hosts = self.app.cname + [self.app.ip]
        hosts = filter(None, hosts)
        if len(hosts) == 0:
            LOG.info("app {} has no host configured".format(self.app.name))
            return None
        hosts = ['"{}"'.format(host) for host in hosts]
        return "host:({})".format(" OR ".join(hosts))

    def __build_range(self):
        time_range = TIME_RANGE_IN_HOURS * 60 * 60
        search_to = arrow.now(LOCAL_TIMEZONE)
        search_from = search_to.replace(seconds=-time_range)
        return graylog_api.SearchRange(from_time=search_from, to_time=search_to)

