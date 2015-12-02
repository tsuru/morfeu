import json
import httpretty
import unittest
import mock

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


if __name__ == '__main__':
    unittest.main()
