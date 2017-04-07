import unittest
from mock import patch, MagicMock
from morfeu.graylog import GraylogClient
from glogcli import graylog_api
from morfeu.tsuru.app import TsuruApp
from morfeu.tsuru.client import TsuruClient


class MorfeuGraylogTestCase(unittest.TestCase):
    @patch.object(TsuruClient, "get_app")
    @patch.object(graylog_api.GraylogAPI, "search")
    def test_search_app_with_cname_and_ip(self, search, get_app):
        get_app.return_value = {"name": "myapp", "ip": "myapp.mycloud.com", "cname": ["cname1.mycloud.com", "cname2.mycloud.com"]}
        search.return_value = MagicMock()
        GraylogClient(TsuruApp()).search()
        self.assertEqual(search.call_args[0][0].query, 'host:("cname1.mycloud.com" OR "cname2.mycloud.com" OR "myapp.mycloud.com")')


    @patch.object(TsuruClient, "get_app")
    @patch.object(graylog_api.GraylogAPI, "search")
    def test_search_app_without_cname(self, search, get_app):
        get_app.return_value = {"name": "myapp", "ip": "myapp.mycloud.com"}
        search.return_value = MagicMock()
        GraylogClient(TsuruApp()).search()
        self.assertEqual(search.call_args[0][0].query, 'host:("myapp.mycloud.com")')


    @patch.object(TsuruClient, "get_app")
    @patch.object(graylog_api.GraylogAPI, "search")
    def test_search_app_without_ip_or_cname(self, search, get_app):
        get_app.return_value = {"name": "myapp"}
        search.return_value = MagicMock()
        GraylogClient(TsuruApp()).search()
        self.assertEqual(search.call_count, 0)


    @patch.object(TsuruClient, "get_app")
    @patch.object(graylog_api.GraylogAPI, "search")
    def test_search_results(self, search, get_app):
        get_app.return_value = {"name": "myapp", "ip": "myapp.mycloud.com"}
        search.return_value = MagicMock()
        search.return_value.messages = ["message 1"]
        self.assertEqual(GraylogClient(TsuruApp()).search(), ["message 1"])


if __name__ == '__main__':
    unittest.main()
