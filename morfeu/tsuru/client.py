import requests
import os
import logging

LOG = logging.getLogger(__name__)

TSURU_TOKEN = os.getenv("TSURU_TOKEN", "token")
TSURU_HOST = os.getenv("TSURU_HOST", "http://localhost")

class TsuruClient(object):

    def __init__(self, timeout=10):
        self.timeout = timeout
        self.headers = {'Authorization': "bearer {0}".format(TSURU_TOKEN)}

    def __get(self, url=None, params={}):
        r = requests.get(url, params=params, headers=self.headers, timeout=self.timeout)
        return r.json()

    def __post(self, url=None, payload={}, is_json=True):
        r = requests.post(url, data=payload, headers=self.headers, timeout=self.timeout)
        if is_json:
            return r.json()
        else:
            return r

    def list_apps_url(self):
        return "{0}/apps".format(TSURU_HOST)

    def list_apps(self, type=None, domain=None):
        """
        :returns [{"units": [{"ProcessName" : "web"}]}]
        """
        LOG.info("Getting apps of type \"{}\" and domain \"{}\"".format(type, domain))
        url = self.list_apps_url()
        app_list = []
        apps = self.__get(url=url)
        for app in apps:
            if domain:
                if not domain in app.get("ip", ""):
                    continue

            units = app.get('units', [])
            units_list = []
            for unit in units:
                if unit.get("ProcessName", "") == "web":
                    units_list.append(unit["ID"])
                else:
                    pass

            if units_list:
                app_list.append({app["name"] : units_list })

        return app_list

    def get_app(self, app_name=None):
        if app_name:
            url = "{0}/apps/{1}".format(TSURU_HOST, app_name)
            return self.__get(url=url)
        else:
            return {}

    def list_deploys(self, app_name=None):
        LOG.info("Getting deploys for \"{}\"".format(app_name))
        if app_name:
            url = "{0}/deploys?app={1}".format(TSURU_HOST, app_name)
            return self.__get(url=url)
        else:
            return []

    def stop_app(self, app_name=None, process_name="web"):
        if not app_name:
            return
        url = "{0}/apps/{1}/stop?process={2}".format(TSURU_HOST, app_name, process_name)
        req = self.__post(url=url, is_json=False)
        if req.status_code == 200:
            LOG.info("App {0} stopped... {1}".format(app_name, req.content))
