# -*- coding: cp1251 -*-
def insertion_sort(arr):
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        # Перемещаем элементы, которые больше ключа, на одну позицию вперед
        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = key

# Пример использования
array = [64, 34, 25, 12, 22, 11, 90]
insertion_sort(array)
print("Отсортированный массив:", array)
