import requests
import logging
from .exceptions import TsuruClientBadResponse
from morfeu.settings import TSURU_TOKEN, TIMEOUT, TSURU_HOST, POOL_WHITELIST

LOG = logging.getLogger(__name__)


class TsuruClientUrls(object):

    @classmethod
    def list_apps_url(cls, pool=""):
        return "{}/apps?pool={}".format(TSURU_HOST, pool)

    @classmethod
    def get_app_url(cls, app_name):
        return "{0}/apps/{1}".format(TSURU_HOST, app_name)

    @classmethod
    def get_list_deploy_url_by_app(cls, app_name):
        return "{0}/deploys?app={1}".format(TSURU_HOST, app_name)

    @classmethod
    def get_stop_url_by_app_and_process_name(cls, app_name=None, process_name=None):
        return "{0}/apps/{1}/stop?process={2}".format(TSURU_HOST, app_name, process_name)


class TsuruClient(object):

    def __init__(self):
        self.timeout = TIMEOUT
        self.headers = {'Authorization': "bearer {0}".format(TSURU_TOKEN)}

    def __get(self, url=None, params={}):
        r = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        if r.status_code == requests.codes.ok:
            return r.json()
        else:
            raise TsuruClientBadResponse("Bad Request {}".format(r.status_code))

    def __post(self, url=None, payload={}):
        r = requests.post(url, data=payload, headers=self.headers, timeout=self.timeout)
        if r.status_code != requests.codes.ok:
            raise TsuruClientBadResponse("Bad Request {}".format(r.status_code))

        return r

    def list_apps(self, type=None, domain=None):
        """
        :returns [{"units": [{"ProcessName" : "web"}]}]
        """
        LOG.info("Getting apps of type \"{}\" and domain \"{}\"".format(type, domain))
        url = TsuruClientUrls.list_apps_url(pool=POOL_WHITELIST)
        app_list = []

        try:
            apps = self.__get(url=url)
        except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
            LOG.error(e)
            return app_list

        for app in apps:
            if domain:
                if domain not in app.get("ip", ""):
                    continue

            units = app.get('units', [])
            units_list = []
            for unit in units:
                if unit.get("ProcessName", "") == "web":
                    units_list.append(unit["ID"])
                else:
                    pass

            if units_list:
                app_list.append({app["name"]: units_list})

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

    def list_deploys(self, app_name=None):
        LOG.info("Getting deploys for \"{}\"".format(app_name))
        if app_name:
            url = TsuruClientUrls.get_list_deploy_url_by_app(app_name)
            try:
                return self.__get(url=url)
            except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
                LOG.error(e)
                return []
        else:
            return []

    def sleep_app(self, app_name=None, process_name="web"):
        if not app_name:
            return
        url = TsuruClientUrls.get_stop_url_by_app_and_process_name(app_name=app_name,
                                                                   process_name=process_name)
        try:
            req = self.__post(url=url)
            LOG.info("App {0} stopped... {1}".format(app_name, req.content))
            return True
        except (TsuruClientBadResponse, requests.exceptions.Timeout) as e:
            LOG.error(e)
            return False
