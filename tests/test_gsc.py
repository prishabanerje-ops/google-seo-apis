import csv
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import gsc


class TestQuerySearchAnalytics(unittest.TestCase):
    def _make_service(self, rows):
        mock_execute = MagicMock(return_value={"rows": rows})
        mock_query = MagicMock()
        mock_query.return_value.execute = mock_execute
        mock_service = MagicMock()
        mock_service.searchanalytics.return_value.query = mock_query
        return mock_service

    def test_returns_rows_list(self):
        rows = [{"keys": ["health insurance"], "clicks": 100,
                 "impressions": 1000, "ctr": 0.1, "position": 3.2}]
        service = self._make_service(rows)
        result = gsc.query_search_analytics(service, "sc-domain:example.com", 30, "query", 10)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["keys"][0], "health insurance")

    def test_empty_response_returns_empty_list(self):
        mock_execute = MagicMock(return_value={})
        mock_query = MagicMock()
        mock_query.return_value.execute = mock_execute
        mock_service = MagicMock()
        mock_service.searchanalytics.return_value.query = mock_query
        result = gsc.query_search_analytics(mock_service, "sc-domain:example.com", 30, "query", 10)
        self.assertEqual(result, [])

    def test_calls_api_with_correct_dimension(self):
        service = self._make_service([])
        gsc.query_search_analytics(service, "sc-domain:example.com", 7, "page", 5)
        call_kwargs = service.searchanalytics.return_value.query.call_args[1]
        body = call_kwargs["body"]
        self.assertEqual(body["dimensions"], ["page"])
        self.assertEqual(body["rowLimit"], 5)


class TestListProperties(unittest.TestCase):
    def test_returns_site_urls(self):
        mock_execute = MagicMock(return_value={
            "siteEntry": [
                {"siteUrl": "sc-domain:example.com", "permissionLevel": "siteOwner"},
                {"siteUrl": "https://blog.example.com/", "permissionLevel": "siteOwner"},
            ]
        })
        mock_service = MagicMock()
        mock_service.sites.return_value.list.return_value.execute = mock_execute
        result = gsc.list_properties(mock_service)
        self.assertEqual(result, ["sc-domain:example.com", "https://blog.example.com/"])

    def test_returns_empty_list_when_no_sites(self):
        mock_execute = MagicMock(return_value={})
        mock_service = MagicMock()
        mock_service.sites.return_value.list.return_value.execute = mock_execute
        self.assertEqual(gsc.list_properties(mock_service), [])


class TestWriteCsv(unittest.TestCase):
    def test_writes_correct_headers_and_rows(self):
        rows = [{"keys": ["test query"], "clicks": 50,
                 "impressions": 500, "ctr": 0.1, "position": 5.0}]
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            tmp_path = f.name
        gsc.write_csv(rows, tmp_path, "query")
        with open(tmp_path) as f:
            reader = csv.DictReader(f)
            data = list(reader)
        os.unlink(tmp_path)
        self.assertEqual(data[0]["query"], "test query")
        self.assertEqual(data[0]["clicks"], "50")
        self.assertEqual(data[0]["impressions"], "500")


if __name__ == '__main__':
    unittest.main()
