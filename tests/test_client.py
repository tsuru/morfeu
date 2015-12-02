import json
import unittest
import httpretty
from morfeu.tsuru.client import TsuruClient, TsuruClientUrls


class MorfeuTsuruClientTestCase(unittest.TestCase):

    def setUp(self):
        self.tsuru_client = TsuruClient()

    def tearDown(self):
        self.tsuru_client = None

    # ## LIST APPS ## #

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

    # ## END LIST APPS ## #

    # ## GET APP ## #

    @httpretty.activate
    def test_get_app_successfully(self):

        app_name = 'morfeu'
        expected_response = json.dumps([{
            u'ip': u'morfeu.cloud.globoi.com',
            u'name': u'morfeu',
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=200)
        self.assertEqual(self.tsuru_client.get_app(app_name), json.loads(expected_response))

    @httpretty.activate
    def test_get_app_with_failure(self):

        app_name = 'morfeu'
        expected_response = json.dumps([{
            u'ip': u'morfeu.cloud.globoi.com',
            u'name': u'morfeu',
        }])
        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app_name),
                               body=expected_response,
                               content_type="application/json",
                               status=500)
        self.assertEqual(self.tsuru_client.get_app(app_name), json.loads("{}"))

    # ## END GET APP ## #
if __name__ == '__main__':
    unittest.main()
