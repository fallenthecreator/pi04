public class InsertionSort {
    public static void main(String[] args) {
        int[] arr = { 64, 34, 25, 12, 22, 11, 90};

        // Алгоритм сортировки вставками
        for (int i = 1; i < arr.length; i++) {
            int ключ = arr[i];
            int j = i - 1;

            // Перемещаем элементы, которые больше ключа, на одну позицию вперед
            while (j >= 0 && arr[j] > ключ) {
                arr[j + 1] = arr[j];
                j--;
            }
            arr[j + 1] = ключ;
        }

        // Вывод отсортированного массива
        System.out.println("Отсортированный массив:");
        for (int num : arr) {
            System.out.print(num + " ");
        }// Место для кода.
