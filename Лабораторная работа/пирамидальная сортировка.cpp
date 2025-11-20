#include <iostream>
#include <vector>
using namespace std;

void heapify(vector<int>& arr, int n, int i) {
    int largest = i;        // корень поддерева
    int left = 2 * i + 1;   // левый ребёнок
    int right = 2 * i + 2;  // правый ребёнок

    // если левый ребёнок больше корня
    if (left < n && arr[left] > arr[largest])
        largest = left;

    // если правый ребёнок больше текущего максимума
    if (right < n && arr[right] > arr[largest])
        largest = right;

    // если максимум не корень — меняем и продолжаем просеивание
    if (largest != i) {
        swap(arr[i], arr[largest]);
        heapify(arr, n, largest);
    }
}

void heapSort(vector<int>& arr) {
    int n = arr.size();

    // строим кучу
    for (int i = n / 2 - 1; i >= 0; i--)
        heapify(arr, n, i);

    // извлекаем элементы по одному
    for (int i = n - 1; i > 0; i--) {
        swap(arr[0], arr[i]);
        heapify(arr, i, 0);
    }
}

int main() {
    vector<int> nums = {12, 3, 5, 7, 19, 1};

    heapSort(nums);

    for (int x : nums)
        cout << x << " ";

    return 0;
}