def shell_sort(arr):
    n = len(arr)
    gap = n // 2  # начальный размер шага

    # Увеличиваем gap до 1, уменьшая его в два раза
    while gap > 0:
        for i in range(gap, n):
            temp = arr[i]
            j = i
            # Выполняем insertion sort для элементов, находящихся на расстоянии gap
            while j >= gap and arr[j - gap] > temp:
                arr[j] = arr[j - gap]
                j -= gap
            arr[j] = temp
        gap //= 2

# Пример использования
array = [64, 34, 25, 12, 22, 11, 90]
shell_sort(array)
print("Отсортированный массив:", array)
