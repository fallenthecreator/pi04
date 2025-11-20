public class бинарный поиск {
    public static int binarySearch(int[] arr, int target) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high) {
            int mid = low + (high - low) / 2;
            if (arr[mid] == target) {
                return mid; // найден
            }
            else if (arr[mid] < target) {
                low = mid + 1; // ищем в правой части
            }
            else {
                high = mid - 1; // ищем в левой части
            }
        }
        return -1; // не найден
    }

    public static void main(String[] args) {
        int[] array = { 2, 5, 8, 12, 16, 23, 38, 56, 72, 91 };
        int target = 23;

        int result = binarySearch(array, target);
        if (result != -1) {
            System.out.println("Элемент " + target + " найден на позиции " + result);
        }
        else {
            System.out.println("Элемент " + target + " не найден");
        }
    }
}