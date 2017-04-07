import requests
import logging
from .exceptions import TsuruClientBadResponse
from morfeu.settings import TSURU_TOKEN, TIMEOUT, TSURU_HOST, POOLS, STATIC_PLATFORM_NAME, TSURU_APP_PROXY_URL

LOG = logging.getLogger(__name__)


class TsuruClientUrls(object):

    @classmethod
    def list_apps_url(cls, pool="", status=""):
        return "{}/apps?pool={}&status={}".format(TSURU_HOST, pool, status)

    @classmethod
    def get_app_url(cls, app_name):
        return "{0}/apps/{1}".format(TSURU_HOST, app_name)

    @classmethod
    def get_stop_url(cls, app_name=None, process_name=None):
        return "{0}/apps/{1}/stop?process={2}".format(TSURU_HOST, app_name, process_name)

    @classmethod
    def get_sleep_url(cls, app_name=None, process_name=None, proxy_url=None):
        return "{0}/apps/{1}/sleep?proxy={3}&process={2}".format(TSURU_HOST,
                                                                 app_name,
                                                                 process_name,
                                                                 proxy_url)


class TsuruClient(object):

    def __init__(self):
        self.timeout = TIMEOUT
        self.headers = {'Authorization': "bearer {0}".format(TSURU_TOKEN)}

    def __get(self, url, params=None):
        r = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise TsuruClientBadResponse("Bad Request {}".format(r.status_code))

    def __post(self, url, payload=None):
        r = requests.post(url, data=payload, headers=self.headers, timeout=self.timeout)
        if r.status_code != requests.codes.ok:
            raise TsuruClientBadResponse("Bad Request {}".format(r.status_code))

        return r

    def list_apps(self, process_name="web", domain=None):
        """
        :returns [{"myapp": {"cname": ["cname1", "cname1"]}, "ip": "ip1"}]
        """
        LOG.info("Getting apps with process \"{}\" and domain \"{}\"".format(process_name, domain))
        url = TsuruClientUrls.list_apps_url(pool=POOLS, status="started")
        app_list = []

        try:
            apps = self.__get(url=url)
        except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
            LOG.error(e)
            return app_list

        for app in apps:
            if domain and domain not in app.get("ip", ""):
                continue

            platform = app.get("platform")
            units = app.get("units", [])
            for unit in units:
                if unit.get("Status") == "started" and \
                        (unit.get("ProcessName") == process_name or
                            platform == STATIC_PLATFORM_NAME):
                    app_list.append({app["name"]: {
                        "cname": app["cname"],
                        "ip": app["ip"]
                    }})
                    break

        return app_list

    def get_app(self, app_name=None):
        if app_name:
            url = TsuruClientUrls.get_app_url(app_name)
            try:
                return self.__get(url=url)
            except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
                LOG.error(e)
                return {}
        else:
            return {}

    def stop_app(self, app_name=None, process_name="web"):
        if not app_name:
            return False

        url = TsuruClientUrls.get_stop_url(app_name=app_name, process_name=process_name)
        try:
            req = self.__post(url=url)
            LOG.info("App {0} stopped... {1}".format(app_name, req.content))
            return True
        except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
            LOG.error(e)
            return False

    def sleep_app(self, app_name=None, process_name="web", proxy_url=TSURU_APP_PROXY_URL):
        if not app_name:
            return False

        url = TsuruClientUrls.get_sleep_url(app_name=app_name,
                                            process_name=process_name,
                                            proxy_url=proxy_url)
        try:
            req = self.__post(url=url)
            LOG.info("App {0} asleep... {1}".format(app_name, req.content))
            return True
        except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
            LOG.error(e)
            return False
