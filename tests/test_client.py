import json
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

    def __expected_unit(self, name="app1", platform="python", process_name="web", unit_status="started"):
        expected_response = json.dumps([{
            "name": name,
            "platform": platform,
            "units": [{"ID": "app1/0", "Status": unit_status, "ProcessName": process_name}],
            "cname": ["cname1"],
            "ip": "myapp.mycloud.com"
        }])
        return expected_response

    def mock_list_apps(self, pool="", process_name="web", platform="python",
                       status=200, unit_status="started"):
        expected_response = self.__expected_unit(process_name=process_name,
                                                 platform=platform,
                                                 unit_status=unit_status)

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.list_apps_url(pool=pool),
                               body=expected_response, content_type="application/json", status=status)

    @httpretty.activate
    def test_list_apps_by_process_name(self):
        self.mock_list_apps(process_name="worker")
        self.assertEqual(self.tsuru_client.list_apps(), [])
        self.assertEqual(self.tsuru_client.list_apps(process_name="worker"),
                         [{"app1": {"cname": ["cname1"], "ip": "myapp.mycloud.com"}}])

    @httpretty.activate
    def test_list_apps_by_domain(self):
        self.mock_list_apps()
        self.assertEqual(self.tsuru_client.list_apps(domain="11"), [])
        self.assertEqual(self.tsuru_client.list_apps(domain="mycloud.com"),
                         [{"app1": {"cname": ["cname1"], "ip": "myapp.mycloud.com"}}])

    @httpretty.activate
    def test_list_always_include_static_apps(self):
        self.mock_list_apps(platform="static")
        self.assertEqual(self.tsuru_client.list_apps(process_name="worker"),
                         [{"app1": {"cname": ["cname1"], "ip": "myapp.mycloud.com"}}])

    @httpretty.activate
    def test_list_apps_by_pool(self):
        self.mock_list_apps(pool="green")
        self.assertEqual(self.tsuru_client.list_apps(),
                         [{"app1": {"cname": ["cname1"], "ip": "myapp.mycloud.com"}}])

    @httpretty.activate
    def test_list_apps_no_web_apps(self):
        self.mock_list_apps(process_name="worker")
        self.assertEqual(self.tsuru_client.list_apps(), [])

    @httpretty.activate
    def test_list_apps_only_running_apps(self):
        self.mock_list_apps(unit_status="stopped")
        self.assertEqual(self.tsuru_client.list_apps(), [])

    @httpretty.activate
    def test_list_apps_with_failure(self):
        self.mock_list_apps(process_name="web", status=500)
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
        expected_response = self.__expected_unit(name=app_name)
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertEqual(self.tsuru_client.get_app(app_name=app_name), json.loads(expected_response))

    @httpretty.activate
    def test_get_app_with_failure(self):
        app_name = 'morfeu'
        expected_response = self.__expected_unit(name=app_name)
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
    def test_sleep_app_with_success(self):
        app_name = 'morfeu'
        process_name = "web"
        proxy_url = 'http://fake:123'

        expected_response = json.dumps("")
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_sleep_url(app_name, process_name, proxy_url),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertTrue(self.tsuru_client.sleep_app(app_name=app_name,
                                                    process_name=process_name,
                                                    proxy_url=proxy_url))

    @httpretty.activate
    def test_sleep_app_with_failure(self):
        app_name = 'morfeu'
        process_name = "web"
        proxy_url = 'http://fake:123'

        expected_response = json.dumps("")
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_sleep_url(app_name, process_name, proxy_url),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertFalse(self.tsuru_client.sleep_app(app_name=app_name,
                                                     process_name=process_name,
                                                     proxy_url=proxy_url))

    @httpretty.activate
    def test_sleep_app_without_app_name(self):
        self.assertFalse(self.tsuru_client.sleep_app())

    @httpretty.activate
    def test_sleep_app_with_timeout(self):
        def raiseTimeout(request, uri, headers):
            raise requests.Timeout('Connection timed out.')

        app_name = 'morfeu'
        process_name = "web"
        proxy_url = 'http://fake:123'
        httpretty.register_uri(httpretty.POST,
                               TsuruClientUrls.get_sleep_url(app_name, process_name, proxy_url),
                               body=raiseTimeout,
                               content_type="application/json",
                               status=500)
        self.assertFalse(self.tsuru_client.sleep_app(app_name=app_name,
                                                     process_name=process_name,
                                                     proxy_url=proxy_url))

if __name__ == '__main__':
    unittest.main()
