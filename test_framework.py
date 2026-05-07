import unittest
import os
import csv
from logger import Logger
from collector import Collector

class TestAgingFramework(unittest.TestCase):
    def setUp(self):
        self.test_csv = "test_run.csv"
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def tearDown(self):
        if os.path.exists(self.test_csv):
            os.remove(self.test_csv)

    def test_logger_creation(self):
        logger = Logger(self.test_csv)
        self.assertTrue(os.path.exists(self.test_csv))
        with open(self.test_csv, 'r') as f:
            reader = csv.reader(f)
            headers = next(reader)
            self.assertEqual(headers[1], "MemFree")

    def test_collector_data(self):
        collector = Collector(log_file=self.test_csv)
        data = collector.collect_once()
        self.assertIn("MemFree", data)
        self.assertIn("Frag_Index_Order_0", data)
        self.assertTrue(os.path.exists(self.test_csv))

if __name__ == "__main__":
    unittest.main()
