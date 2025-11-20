#include <iostream>
using namespace std;

int main() {
    // Создание массива из 5 целых чисел
    int arr[5] = {1, 2, 3, 4, 5};

    // Вывод элементов массива
    cout << "Массив: ";
    for (int i = 0; i < 5; i++) {
        cout << arr[i] << " ";
    }
    cout << endl;

    return 0;
}