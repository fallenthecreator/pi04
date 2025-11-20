def sequential_search(arr, target):
    for index, element in enumerate(arr):
        if element == target:
            return index  # найденный индекс элемента
    return -1  # если элемент не найден

# ѕример использовани€
array = [10, 23, 45, 70, 11, 15]
target_value = 70

result = sequential_search(array, target_value)
if result != -1:
    print(f"Ёлемент {target_value} найден на позиции {result}")
else:
    print(f"Ёлемент {target_value} не найден в массиве")
