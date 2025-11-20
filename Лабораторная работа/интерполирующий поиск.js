public class InterpolationSearch {

    public static int interpolationSearch(int[] arr, int target) {
        int low = 0;
        int high = arr.length - 1;

        while (low <= high && target >= arr[low] && target <= arr[high]) {
            // вычисляем позицию с интерполяцией
            int pos = low + (int)((double)(target - arr[low]) 
                                  * (high - low) 
                                  / (arr[high] - arr[low]));

            if (arr[pos] == target)
                return pos;

            if (arr[pos] < target)
                low = pos + 1;
            else
                high = pos - 1;
        }

        return -1; // не найден
    }

    public static void main(String[] args) {
        int[] data = {10, 20, 30, 40, 50, 60, 70};
        int target = 40;

        int index = interpolationSearch(data, target);
        System.out.println("Index: " + index);
    }
}