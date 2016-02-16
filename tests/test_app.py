import json
import httpretty
import unittest
import re

from morfeu.tsuru.app import TsuruApp
from morfeu.tsuru.client import TsuruClientUrls
from morfeu.settings import ESEARCH_HOST, TSURU_APP_PROXY_URL


class AppTestCase(unittest.TestCase):

    def mock_app(self, app):
        expected_response = json.dumps({
            "name": app,
            "ip": "{}.tsuru.io".format(app),
            "platform": "php",
            "units": [
                {"Address": {"Host": "10.10.10.10"}, "ID": "app1/0", "Status": "stopped"},
            ],
            "pool": "mypool",
        })

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app),
                               body=expected_response, content_type="application/json", status=200)

    @httpretty.activate
    def test_should_go_to_bed_when_app_isnt_new_and_has_no_hits(self):
        url = "http://{0}/.measure-tsuru-*/response_time/_search".format(ESEARCH_HOST)
        httpretty.register_uri(httpretty.POST, url,
                               body="{}", content_type="application/json", status=200)

        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        self.assertTrue(app.should_go_to_bed())

    @httpretty.activate
    def test_should_not_go_to_bed_when_app_is_new_and_has_no_hits(self):
        url = "http://{0}/.measure-tsuru-*/response_time/_search".format(ESEARCH_HOST)
        httpretty.register_uri(httpretty.POST, url,
                               body="{}", content_type="application/json", status=200)

        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        self.assertTrue(app.should_go_to_bed())

    @httpretty.activate
    def test_should_not_go_to_bed_when_app_isnt_new_and_has_hits(self):
        url = "http://{0}/.measure-tsuru-*/response_time/_search".format(ESEARCH_HOST)
        httpretty.register_uri(httpretty.POST, url,
                               body='{"hits": {"hits": [1, 2, 3]}}',
                               content_type="application/json",
                               status=200)

        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        self.assertFalse(app.should_go_to_bed())

    @httpretty.activate
    def test_unicode(self):
        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        self.assertEqual(unicode(app), "myapp")

    @httpretty.activate
    def test_stop_app(self):
        url = TsuruClientUrls.get_stop_url("myapp", "web")
        httpretty.register_uri(httpretty.POST, url, content_type="application/json", status=200)

        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        app.stop()

        path = re.search('^http://[^/]+(.*)$', url).group(1)
        self.assertEqual(httpretty.last_request().path, path)

    @httpretty.activate
    def test_sleep_app(self):
        url = TsuruClientUrls.get_sleep_url("myapp", "web", TSURU_APP_PROXY_URL)
        httpretty.register_uri(httpretty.POST, url, content_type="application/json", status=200)

        self.mock_app("myapp")

        app = TsuruApp(name="myapp")
        app.sleep()

        path = re.search('^http://[^/]+(.*)$', url).group(1)
        self.assertEqual(httpretty.last_request().path, path)

if __name__ == '__main__':
    unittest.main()
