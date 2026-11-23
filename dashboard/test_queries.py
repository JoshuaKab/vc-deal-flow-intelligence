import unittest
from unittest.mock import patch

from dashboard.queries import get_data_quality_metrics


class DataQualityQueryTests(unittest.TestCase):
    def test_quality_query_returns_zero_for_checks_without_issues(self):
        results = [(name, 0) for name in range(6)]
        columns = ["CHECK_NAME", "ISSUE_COUNT"]

        with patch("dashboard.queries.execute_query", return_value=(results, columns)) as execute:
            quality_df = get_data_quality_metrics()

        query = execute.call_args.args[0]
        self.assertEqual(query.count("COALESCE(COUNT_IF("), 5)
        self.assertEqual(quality_df["ISSUE_COUNT"].tolist(), [0] * 6)


if __name__ == "__main__":
    unittest.main()
