import unittest
import duckdb
from demo import setup, run_query, QUERIES, DB
from server import dataset

class TestWaterMonitorDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        setup()

    def test_query_count(self):
        """All 8 analytical queries are defined."""
        self.assertEqual(len(QUERIES), 8)

    def test_table_counts(self):
        """All relational tables contain expected synthetic record counts."""
        con = duckdb.connect(str(DB), read_only=True)
        counts = {
            'LOCATION': 4,
            'WATER_BODY': 4,
            'SENSOR': 5,
            'MEASUREMENT': 100,
            'WEATHER_RECORD': 5,
            'LAND_USE_FACTOR': 5,
            'HISTORICAL_STATE': 6,
            'POLLUTION_EVENT': 5,
            'INSPECTION': 3,
        }
        for table, expected in counts.items():
            count = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
            self.assertEqual(count, expected, f"Table {table} expected {expected} rows, got {count}")
        con.close()

    def test_query1_pollution_after_rainfall(self):
        result = run_query(0)
        self.assertEqual(len(result['rows']), 2)
        self.assertIn('change_percent', result['columns'])
        self.assertIn('rainfall_mm', result['columns'])

    def test_query2_repeated_anomalies(self):
        result = run_query(1)
        self.assertEqual(len(result['rows']), 2)
        # Sensor 101 has 3 anomalies, Sensor 201 has 2
        self.assertEqual(result['rows'][0][0], 101)
        self.assertEqual(result['rows'][0][2], 3)
        self.assertEqual(result['rows'][1][0], 201)
        self.assertEqual(result['rows'][1][2], 2)

    def test_query3_average_measurements(self):
        result = run_query(2)
        self.assertEqual(len(result['rows']), 5)

    def test_query4_industrial_factors(self):
        result = run_query(3)
        self.assertEqual(len(result['rows']), 3)

    def test_query5_pollution_historical_states(self):
        result = run_query(4)
        self.assertEqual(len(result['rows']), 5)

    def test_query6_yoy_turbidity_trend(self):
        result = run_query(5)
        # 4 water bodies * 5 years = 20 rows
        self.assertEqual(len(result['rows']), 20)
        self.assertIn('yoy_change_percent', result['columns'])

    def test_query7_spatial_proximity(self):
        result = run_query(6)
        self.assertEqual(len(result['rows']), 3)
        self.assertIn('distance_km', result['columns'])
        # All returned distances should be within 2.0 km
        for row in result['rows']:
            dist = row[result['columns'].index('distance_km')]
            self.assertLessEqual(dist, 2.0)

    def test_query8_computed_anomaly_detection(self):
        result = run_query(7)
        self.assertEqual(len(result['rows']), 5)
        self.assertIn('computed_anomaly', result['columns'])
        for row in result['rows']:
            self.assertTrue(row[result['columns'].index('computed_anomaly')])

    def test_server_dataset_structure(self):
        """API dataset() extracts all required collections for the dashboard."""
        data = dataset()
        expected_keys = [
            'bodies', 'measurements', 'events', 'weather',
            'factors', 'states', 'inspections', 'sensors', 'queries'
        ]
        for key in expected_keys:
            self.assertIn(key, data)
            self.assertIsInstance(data[key], list)
        self.assertEqual(len(data['queries']), 8)

if __name__ == '__main__':
    unittest.main()
