import csv
import os
import tempfile
import unittest

from models.prediction_tool import analyze_and_predict


class PredictionToolTests(unittest.TestCase):
    def test_csv_parser_keeps_first_data_row(self):
        handle = tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            newline="",
            encoding="utf-8",
            delete=False,
        )
        try:
            writer = csv.writer(handle)
            writer.writerow(["time", "value"])
            for index in range(20):
                writer.writerow([index, 10 + index * 0.5])
            handle.close()

            result = analyze_and_predict(handle.name, steps=4)

            self.assertNotIn("error", result)
            self.assertEqual(result["summary_stats"]["historical_points"], 20)
            self.assertEqual(len(result["chart_data"]["forecast_data"]), 4)
        finally:
            if not handle.closed:
                handle.close()
            os.remove(handle.name)


if __name__ == "__main__":
    unittest.main()
