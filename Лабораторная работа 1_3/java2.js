import java.util.ArrayList;

public class Main {
    public static void main(String[] args) {
        // Создание списка (ArrayList)
        ArrayList<Integer> list = new ArrayList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);

        // Добавление элемента в список
        list.add(6);

        // Вывод элементов списка
        System.out.print("Список: ");
        for (int num : list) {
            System.out.print(num + " ");
        }
        System.out.println();
    }
}
