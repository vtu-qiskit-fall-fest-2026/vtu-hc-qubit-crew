
import unittest

from src.classical.baseline import FEATURES, load_data


class TestBaselineData(unittest.TestCase):
    def test_sample_data_has_expected_columns(self):
        df = load_data()
        self.assertTrue(set(FEATURES + ["label"]).issubset(df.columns))

    def test_sample_data_has_both_labels(self):
        df = load_data()
        self.assertEqual(set(df["label"].unique()), {0, 1})

    def test_features_are_binary(self):
        df = load_data()
        for feature in FEATURES:
            self.assertTrue(set(df[feature].unique()).issubset({0, 1}))


if __name__ == "__main__":
    unittest.main()
