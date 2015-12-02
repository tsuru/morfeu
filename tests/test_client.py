import unittest
import httpretty
from morfeu.tsuru.client import TsuruClient, TSURU_HOST


class MorfeuTsuruClientTestCase(unittest.TestCase):

    def setUp(self):
        self.tsuru_client = TsuruClient()

    def tearDown(self):
        self.tsuru_client = None

    @httpretty.activate
    def test_client_list_apps_with_success(self):

        expected_response = '[{"ip":"10.10.10.10","name":"app1","units":[{"ID":"app1/0","Status":"started", "ProcessName": "web"}]}]'
        httpretty.register_uri(httpretty.GET, self.tsuru_client.list_apps_url(),
                       body=expected_response,
                       content_type="application/json",
                       status=200)
        self.assertEqual(self.tsuru_client.list_apps(), [{u'app1': [u'app1/0']}])


if __name__ == '__main__':
    unittest.main()