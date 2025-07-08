import unittest
import random

from ..helper import randomize_list


class TestRandomizeList(unittest.TestCase):
    def test_no_consecutive_items(self):
        lst = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
        randomized = randomize_list(lst)
        for i in range(len(randomized) - 1):
            self.assertNotEqual(randomized[i], randomized[i + 1], f"Consecutive items found at indices {i} and {i + 1}")

    def test_randomized_output(self):
        lst = [1, 2, 3, 4, 5]
        randomized = randomize_list(lst)
        self.assertCountEqual(lst, randomized, "The shuffled list does not contain the same elements as the original list")

    def test_empty_list(self):
        lst = []
        randomized = randomize_list(lst)
        self.assertEqual(randomized, [], "The shuffled empty list should also be empty")

    def test_single_element_list(self):
        lst = [1]
        randomized = randomize_list(lst)
        self.assertEqual(randomized, [1], "The shuffled list with one element should be the same as the original list")

    def test_list_with_identical_elements(self):
        lst = [1, 1, 1, 1, 1]
        randomized = randomize_list(lst)
        # Since all elements are identical, check if the output list has the same length and elements
        self.assertEqual(len(lst), len(randomized), "The shuffled list does not have the same length as the original list")
        self.assertTrue(all(x == 1 for x in randomized), "The shuffled list does not contain identical elements as expected")


    def test_larger_list(self):
        lst = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        randomized = randomize_list(lst)
        self.assertCountEqual(lst, randomized, "The shuffled list does not contain the same elements as the original list")
        for i in range(len(randomized) - 1):
            self.assertNotEqual(randomized[i], randomized[i + 1], f"Consecutive items found at indices {i} and {i + 1}")

if __name__ == '__main__':
    unittest.main()
