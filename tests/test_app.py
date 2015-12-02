import json
import datetime
import httpretty
import unittest
import mock
import pytz

from morfeu.tsuru.app import TsuruApp
from morfeu.tsuru.client import TsuruClientUrls


class AppTestCase(unittest.TestCase):

    def mock_app(self, app):
        expected_response = json.dumps({
            "name": app,
            "ip": "{}.tsuru.io".format(app),
            "platform": "php",
            "units": [
                {"Address": {"Host": "10.10.10.10"}, "ID": "app1/0", "Status": "started"},
            ],
            "pool": "mypool",
        })

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_app_url(app),
                               body=expected_response, content_type="application/json", status=200)

    @httpretty.activate
    @mock.patch("redis.StrictRedis")
    def test_re_route(self, redis_mock):
        redis_conn_mock = mock.Mock()
        redis_mock.return_value = redis_conn_mock

        self.mock_app("caffeine")
        self.mock_app("myapp")
        proxy_app = TsuruApp(name="caffeine")

        app_name = "myapp"
        app = TsuruApp(name=app_name)
        app.re_route(tsuru_app_proxy=proxy_app)

        redis_mock.assert_called_with(socket_timeout=10, host='localhost', port=6379)
        redis_conn_mock.ltrim.assert_called_with('frontend:myapp.tsuru.io', 0, 0)
        redis_conn_mock.rpush.assert_called_with('frontend:myapp.tsuru.io', 'http://caffeine.tsuru.io')
        redis_conn_mock.close.assert_called_with()

    def mock_deploy(self, app, date="2015-01-01T15:40:04.931-02:00"):
	expected_response = json.dumps([
	  {
	    "ID": "54c92d91a46ec0e78501d86b",
	    "App": "test",
	    "Timestamp": date,
	    "Duration": 18709653486,
	    "Commit": "54c92d91a46ec0e78501d86b54c92d91a46ec0e78501d86b",
	    "Error": "",
	    "Image": "tsuru/app-test:v3",
	    "User": "admin@example.com",
	    "Origin": "git",
	    "CanRollback": True
	  }
	])

        httpretty.register_uri(httpretty.GET, TsuruClientUrls.get_list_deploy_url_by_app(app),
                               body=expected_response, content_type="application/json", status=200)

    @httpretty.activate
    def test_should_go_to_bed_when_app_isnt_new_and_has_no_hits(self):
        url = "http://localhost/.measure-tsuru-*/response_time/_search"
        httpretty.register_uri(httpretty.POST, url,
                               body="{}", content_type="application/json", status=200)

        self.mock_app("myapp")
        self.mock_deploy("myapp")

        app = TsuruApp(name="myapp")
        self.assertTrue(app.should_go_to_bed())

    @httpretty.activate
    def test_should_not_go_to_bed_when_app_is_new_and_has_no_hits(self):
        url = "http://localhost/.measure-tsuru-*/response_time/_search"
        httpretty.register_uri(httpretty.POST, url,
                               body="{}", content_type="application/json", status=200)

        self.mock_app("myapp")
	fmt = '%Y-%m-%d %H:%M:%S %Z%z'
        self.mock_deploy("myapp", date=datetime.datetime.now(pytz.utc).strftime(fmt))

        app = TsuruApp(name="myapp")
        self.assertFalse(app.should_go_to_bed())

    @httpretty.activate
    def test_should_not_go_to_bed_when_app_isnt_new_and_has_hits(self):
        url = "http://localhost/.measure-tsuru-*/response_time/_search"
        httpretty.register_uri(httpretty.POST, url,
                               body='{"hits": {"hits": [1, 2, 3]}}',
                               content_type="application/json",
                               status=200)

        self.mock_app("myapp")
        self.mock_deploy("myapp")

        app = TsuruApp(name="myapp")
        self.assertFalse(app.should_go_to_bed())


if __name__ == '__main__':
    unittest.main()
