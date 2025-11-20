#include <iostream>
#include <vector>

// ‘ункци€ ищет минимальный индекс ``i``, такой что fib(i) >= target
int fibonacciSearch(const std::vector<int>& arr, int target) {
	int n = arr.size();

	// √енерируем последовательность ‘ибоначчи до тех пор, пока fib(k) не станет больше или равно размеру массива
	int fibMMm2 = 0; // (m-2)-й элемент
	int fibMMm1 = 1; // (m-1)-й элемент
	int fibM = fibMMm2 + fibMMm1; // m-й элемент (самый последний)

	while (fibM < n) {
		fibMMm2 = fibMMm1;
		fibMMm1 = fibM;
		fibM = fibMMm2 + fibMMm1;
	}

	int offset = -1;

	while (fibM > 1) {
		int i = std::min(offset + fibMMm2, n - 1);

		if (arr[i] < target) {
			fibM = fibMMm1;
			fibMMm1 = fibMMm2;
			fibMMm2 = fibM - fibMMm1;
			offset = i;
		}
		else if (arr[i] > target) {
			fibM = fibMMm2;
			fibMMm1 = fibMMm1 - fibMMm2;
			fibMMm2 = fibM - fibMMm1;
		}
		else {
			return i; // найден
		}
	}

	// ѕроверка последнего элемента
	if (fibMMm1 && offset + 1 < n && arr[offset + 1] == target)
		return offset + 1;

	return -1; // не найден
}

int main() {
	std::vector<int> arr = { 10, 22, 35, 40, 45, 50, 80, 82, 85, 90, 100 };
	int target = 85;

	int index = fibonacciSearch(arr, target);
	if (index != -1) {
		std::cout << "Ёлемент " << target << " найден на позиции " << index << std::endl;
	}
	else {
		std::cout << "Ёлемент " << target << " не найден" << std::endl;
	}

	return 0;
}