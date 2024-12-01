from python_sample import *
import unittest

class TestFunctions(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(add_numbers(1, 2), 3)
        self.assertEqual(add_numbers(2, 3), 5)
        self.assertEqual(add_numbers(3, 4), 7)

    def test_add_arr(self):
        arr1 = [1, 2, 3]
        arr2 = [4, 5, 6]
        self.assertEqual(add_arr(arr1, arr2), [5, 7, 9])

    def test_bubble_sort(self):
        arr = [5, 2, 8, 3, 1, 6, 4]
        self.assertEqual(bubble_sort(arr), [1, 2, 3, 4, 5, 6, 8])

    def test_bubble_sort_empty_list():
        assert bubble_sort([]) == []

    def test_bubble_sort_single_element_list():
        assert bubble_sort([1]) == [1]

    def test_bubble_sort_sorted_list():
        assert bubble_sort([1, 2, 3]) == [1, 2, 3]

    def test_bubble_sort_reverse_sorted_list():
        assert bubble_sort([3, 2, 1]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list():
        assert bubble_sort([3, 1, 2]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list_2():
        assert bubble_sort([1, 3, 2]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list_3():
        assert bubble_sort([2, 1, 3]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list_4():
        assert bubble_sort([2, 3, 1]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list_5():
        assert bubble_sort([3, 2, 1]) == [1, 2, 3]

    def test_bubble_sort_few_unsorted_list_6():
        assert bubble_sort([1, 2, 3, 4, 5, 6]) == [1, 2, 3, 4, 5, 6]

    def test_bubble_sort_few_unsorted_list_7():
        assert bubble_sort([6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6]

    def test_bubble_sort_few_unsorted_list_8():
        assert bubble_sort([4, 5, 6, 1, 2, 3]) == [1, 2, 3, 4, 5, 6]

    def test_bubble_sort_few_unsorted_list_9():
        assert bubble_sort([3, 2, 1, 4, 5, 6]) == [1, 2, 3, 4, 5, 6]

    def test_bubble_sort_few_unsorted_list_10():
        assert bubble_sort([6, 5, 4, 3, 2, 1, 7]) == [1, 2, 3, 4, 5, 6, 7]

    def test_bubble_sort_few_unsorted_list_11():
        assert bubble_sort([7, 6, 5, 4, 3, 2, 1]) == [1, 2, 3, 4, 5, 6, 7]

    def test_bubble_sort_few_unsorted_list_12():
        assert bubble_sort([4, 5, 6, 1, 2, 3, 8]) == [1, 2, 3, 4, 5, 6, 8]

    def test_bubble_sort_few_unsorted_list_13():
        assert bubble_sort([8, 7, 6, 5, 4, 3, 2]) == [1, 2, 3, 4, 5, 6, 7, 8]