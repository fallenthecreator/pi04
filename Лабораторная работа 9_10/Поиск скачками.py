import math 
 
def jump_search(arr, x): 
    n = len(arr) 
    step = int(math.sqrt(n)) 
    prev = 0 
 
    # Сделать прыжки вперед, пока не найдем блок, где x может находиться 
    while prev < n and arr[min(step, n) - 1] < x: 
        prev = step 
        step += int(math.sqrt(n)) 
        if prev >= n: 
            return -1  # Не найден 
 
    # Линейный поиск внутри найденного блока 
    while prev < min(step, n): 
        if arr[prev] == x: 
            return prev  # Индекс найден 
        prev += 1 
 
    return -1  # Не найдено 
 
# Пример использования: 
arr = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19] 
x = 13 
 
index = jump_search(arr, x) 
if index != -1: 
    print(f"Элемент {x} найден на позиции {index}") 
else: 

    print(f"Элемент {x} не найден в массиве")
