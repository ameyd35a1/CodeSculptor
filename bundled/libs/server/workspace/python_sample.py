def add_numbers(num1, num2):
    return num1 + num2

def bubble_sort(arr):
    n = len(arr)
    for i in range(n-1):
        for j in range(0, n-i-1):
            if arr[j] > arr[j+1]:
                arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr

def add_arr(arr1, arr2):
    return [i + j for i, j in zip(arr1, arr2)]

