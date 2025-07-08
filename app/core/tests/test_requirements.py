import random
import unittest
from unittest.mock import Mock, MagicMock, create_autospec

from django.db.models import QuerySet

from ..helper import (
    first_business_case,
    second_business_case,
    third_business_case,
    forth_business_case,
)


class TestBusinessCases(unittest.TestCase):
    def setUp(self):
        # Mock data for click_collection.objects.filter
        self.click_collection_mock = Mock()
        self.sorted_click_ids = [
            {'conversion_id': 17873, 'click_id': 268313, 'revenue': '1.483908'},
            {'conversion_id': 17592, 'click_id': 265344, 'revenue': '1.448209'},
            {'conversion_id': 18904, 'click_id': 278266, 'revenue': '1.410488'},
            {'conversion_id': 16648, 'click_id': 256095, 'revenue': '1.389303'}
        ]

        # Mock data for click_collection
        self.click_collection = MagicMock()
        self.click_collection.objects.filter.return_value.values.return_value.distinct.return_value = [
            {'click_id': 268313, 'banner_id': 101, 'campaign_id': 1},
            {'click_id': 265344, 'banner_id': 102, 'campaign_id': 1},
            {'click_id': 278266, 'banner_id': 103, 'campaign_id': 1},
            {'click_id': 256095, 'banner_id': 104, 'campaign_id': 1}
        ]

        # Mock data for distinct_click_ids
        self.distinct_click_ids = MagicMock()
        self.distinct_click_ids.values.return_value.annotate.return_value.order_by.return_value = [
            {'banner_id': 101, 'click_count': 10},
            {'banner_id': 102, 'click_count': 8},
            {'banner_id': 103, 'click_count': 6},
            {'banner_id': 104, 'click_count': 4},
            {'banner_id': 105, 'click_count': 2}
        ]

    def test_first_business_case(self):
        # Mock sorted click IDs
        sorted_click_ids = [{'click_id': i} for i in range(1, 20)]

        # Mock data for distinct_banner_ids
        self.click_collection_mock.objects.filter.return_value.values.return_value.distinct.return_value = [
            {'click_id': i, 'banner_id': f'banner_{i}', 'campaign_id': f'campaign_{i // 2}'} for i in range(1, 11)
        ]

        expected_output = [f'banner_{i}' for i in range(1, 11)]
        self.assertEqual(first_business_case(sorted_click_ids, self.click_collection_mock), expected_output)

    def test_second_business_case(self):
        # Mock sorted click IDs
        sorted_click_ids = [{'click_id': i} for i in range(1, 10)]

        # Mock data for distinct_banner_ids
        self.click_collection_mock.objects.filter.return_value.values.return_value.distinct.return_value = [
            {'click_id': i, 'banner_id': f'banner_{i}', 'campaign_id': f'campaign_{i // 2}'} for i in range(1, 6)
        ]

        # Expected output: top 5 banner IDs from 1 to 5
        expected_output = [f'banner_{i}' for i in range(1, 6)]
        self.assertEqual(second_business_case(sorted_click_ids, self.click_collection_mock), expected_output)

    def test_third_business_case(self):
        result = third_business_case(self.sorted_click_ids, self.click_collection, self.distinct_click_ids)
        print(result)
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result), len(set(result)))
        expected_banner_ids = {101, 102, 103, 104, 105}
        self.assertTrue(set(result).issubset(expected_banner_ids))

    def test_forth_business_case(self):
        # Mock random.sample to ensure predictable results
        random.sample = MagicMock(return_value=[106, 105])

        result = forth_business_case(self.distinct_click_ids)
        print(result)

        # Validate that the result contains exactly 5 unique banners
        self.assertEqual(len(result), 5)
        self.assertEqual(len(result), len(set(result)))

        # Check if the top 5 banners by click count are included
        expected_top_click_banners = {101, 102, 103, 104, 105}
        self.assertTrue(set(result[:5]).issubset(expected_top_click_banners))

        # If there are not enough unique banners, additional ones should come from the distinct_click_ids
        banner_all_ids = [click['banner_id'] for click in
                          self.distinct_click_ids.values.return_value.annotate.return_value.order_by.return_value]
        additional_banners = set(result) - expected_top_click_banners
        self.assertTrue(all(banner in banner_all_ids for banner in additional_banners))


if __name__ == '__main__':
    unittest.main()
