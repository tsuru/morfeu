import json
import os
import unittest
import httpretty
import requests
from morfeu.tsuru.client import TsuruClient, TsuruClientUrls


class MorfeuTsuruClientTestCase(unittest.TestCase):

    def setUp(self):
        self.tsuru_client = TsuruClient()

    def tearDown(self):
        self.tsuru_client = None

    def raiseTimeout(request, uri, headers):
        raise requests.Timeout('Connection timed out.')

    @httpretty.activate
    def test_list_apps_with_success(self):
        expected_response = json.dumps([{
            "ip": "10.10.10.10",
            "name": "app1",
            "units": [{"ID": "app1/0", "Status": "started", "ProcessName": "web"}]
        }])

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(),
                               body=expected_response, content_type="application/json", status=200)

        self.assertEqual(self.tsuru_client.list_apps(), [{u'app1': [u'app1/0']}])

    @httpretty.activate
    def test_list_apps_by_domain(self):
        expected_response = json.dumps([{
            "ip": "10.10.10.10",
            "name": "app1",
            "units": [{"ID": "app1/0", "Status": "started", "ProcessName": "web"}]
        }])

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(),
                               body=expected_response, content_type="application/json", status=200)

        self.assertEqual(self.tsuru_client.list_apps(domain="11"), [])

    @httpretty.activate
    def test_list_apps_by_pool(self):
        os.environ["POOL_WHITELIST"] = "green"
        expected_response = json.dumps([{
            "ip": "10.10.10.10",
            "name": "app1",
            "units": [{"ID": "app1/0", "Status": "started", "ProcessName": "web"}]
        }])

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(pool="green"),
                               body=expected_response, content_type="application/json", status=200)

        self.assertEqual(self.tsuru_client.list_apps(), [{u'app1': [u'app1/0']}])

    @httpretty.activate
    def test_list_apps_no_web_apps(self):
        expected_response = json.dumps([{
            "ip": "10.10.10.10",
            "name": "app1",
            "units": [{"ID": "app1/0", "Status": "started", "ProcessName": "worker"}]
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertEqual(self.tsuru_client.list_apps(), [])

    @httpretty.activate
    def test_list_apps_with_failure(self):

        expected_response = json.dumps([{
            "ip": "10.10.10.10",
            "name": "app1",
            "units": [{"ID": "app1/0", "Status": "started", "ProcessName": "web"}]
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.list_apps(), [])

    @httpretty.activate
    def test_list_apps_with_timeout(self):

        def raiseTimeout(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        httpretty.register_uri(method=httpretty.GET,
                               uri=TsuruClientUrls.list_apps_url(),
                               body=raiseTimeout,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.list_apps(), [])

    @httpretty.activate
    def test_get_app_with_success(self):
        app_name = 'morfeu'
        expected_response = json.dumps([{
            u'ip': u'morfeu.cloud.io',
            u'name': u'morfeu',
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertEqual(self.tsuru_client.get_app(app_name=app_name), json.loads(expected_response))

    @httpretty.activate
    def test_get_app_with_failure(self):
        app_name = 'morfeu'
        expected_response = json.dumps([{
            u'ip': u'morfeu.cloud.io',
            u'name': u'morfeu',
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.get_app(app_name=app_name), json.loads("{}"))

    @httpretty.activate
    def test_get_app_with_timeout(self):
        def raiseTimeout(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        app_name = 'morfeu'
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=raiseTimeout,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.get_app(app_name=app_name), json.loads("{}"))

    @httpretty.activate
    def test_get_app_without_app_name(self):
        self.assertEqual(self.tsuru_client.get_app(), json.loads("{}"))

    @httpretty.activate
    def test_list_deploys_with_success(self):
        app_name = 'morfeu'
        expected_response = json.dumps([{
            "App": "morfeu"
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_list_deploy_url_by_app(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertEqual(self.tsuru_client.list_deploys(app_name=app_name), json.loads(expected_response))

    @httpretty.activate
    def test_list_deploys_with_failure(self):
        app_name = 'morfeu'
        expected_response = json.dumps([{
            "App": "morfeu"
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_list_deploy_url_by_app(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.list_deploys(app_name=app_name), json.loads("[]"))

    @httpretty.activate
    def test_list_deploys_without_app_name(self):
        self.assertEqual(self.tsuru_client.list_deploys(), json.loads("[]"))

    @httpretty.activate
    def test_list_deploys_with_timeout(self):

        def raiseTimeout(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        app_name = 'morfeu'
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_list_deploy_url_by_app(app_name),
                               body=raiseTimeout,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.list_deploys(app_name=app_name), json.loads("[]"))

    @httpretty.activate
    def test_sleep_app_with_success(self):
        app_name = 'morfeu'
        process_name = "web"
        expected_response = json.dumps("")
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_stop_url_by_app_and_process_name(app_name,
                                                                                    process_name),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertTrue(self.tsuru_client.sleep_app(app_name=app_name, process_name="web"))

    @httpretty.activate
    def test_sleep_app_with_failure(self):
        app_name = 'morfeu'
        process_name = "web"
        expected_response = json.dumps("")
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_stop_url_by_app_and_process_name(app_name,
                                                                                    process_name),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertFalse(self.tsuru_client.sleep_app(app_name=app_name, process_name="web"))

    @httpretty.activate
    def test_sleep_app_with_timeout(self):

        def raiseTimeout(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        app_name = 'morfeu'
        process_name = "web"
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_stop_url_by_app_and_process_name(app_name,
                                                                                    process_name),
                               body=raiseTimeout,
                               content_type="application/json",
                               status=500)
        self.assertFalse(self.tsuru_client.sleep_app(app_name=app_name, process_name="web"))

if __name__ == '__main__':
    unittest.main()
