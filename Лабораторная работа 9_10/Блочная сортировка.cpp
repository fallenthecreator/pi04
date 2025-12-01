#include <iostream> 
#include <vector> 
#include <algorithm> // для std::sort 
 
// Функция для сортировки массива с помощью блочной сортировки 
void blockSort(std::vector<int>& arr, int blockSize) { 
    int n = arr.size(); 
 
    // Сортируем каждый блок отдельно 
    for (int i = 0; i < n; i += blockSize) { 
        int end = std::min(i + blockSize, n); 
        std::sort(arr.begin() + i, arr.begin() + end); 
    } 
 
    // Объединяем отсортированные блоки 
    // В данном простом примере, после сортировки отдельных блоков, 
    // можно дополнительно выполнить полное слияние или другую стратегию. 
    // Для простоты — просто повторная сортировка всего массива: 
    std::sort(arr.begin(), arr.end()); 
} 
 
int main() { 
    std::vector<int> arr = {9, 3, 7, 1, 8, 2, 6, 5, 4}; 
    int blockSize = 3; 
 
    std::cout << "Исходный массив: "; 
    for (int num : arr) std::cout << num << " "; 
    std::cout << std::endl; 
 
    blockSort(arr, blockSize); 
 
    std::cout << "Отсортированный массив: "; 
    for (int num : arr) std::cout << num << " "; 
    std::cout << std::endl; 
 
    return 0; 
} 
