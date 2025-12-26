import os
import sys
import tempfile
import heapq
from typing import List, Iterator, Optional

class ExternalMergeSort:
    """
    Внешняя сортировка слиянием для больших файлов
    
    Основные этапы:
    1. Разделение файла на части, которые помещаются в память
    2. Сортировка каждой части в памяти
    3. Слияние отсортированных частей
    """
    
    def __init__(self, memory_limit: int = 100 * 1024 * 1024):  # 100 MB по умолчанию
        """
        Инициализация внешней сортировки
        
        Args:
            memory_limit: лимит оперативной памяти в байтах
        """
        self.memory_limit = memory_limit
        self.temp_dir = tempfile.mkdtemp(prefix='external_sort_')
        print(f"Временная директория: {self.temp_dir}")
    
    def sort_file(self, input_file: str, output_file: str, 
                  key_func=None, delimiter='\n') -> None:
        """
        Основной метод сортировки файла
        
        Args:
            input_file: путь к входному файлу
            output_file: путь к выходному файлу
            key_func: функция для извлечения ключа сортировки
            delimiter: разделитель строк в файле
        """
        print(f"Начало сортировки файла: {input_file}")
        print(f"Размер файла: {os.path.getsize(input_file) / (1024*1024):.2f} MB")
        
        # Этап 1: Разделение и сортировка частей
        sorted_runs = self._create_initial_runs(input_file, key_func, delimiter)
        print(f"Создано {len(sorted_runs)} отсортированных частей")
        
        # Этап 2: Многофазное слияние
        self._multiway_merge(sorted_runs, output_file, key_func, delimiter)
        
        print(f"Сортировка завершена. Результат в: {output_file}")
    
    def _create_initial_runs(self, input_file: str, key_func, delimiter: str) -> List[str]:
        """
        Создание отсортированных частей (runs)
        
        Читает файл порциями, сортирует в памяти и сохраняет во временные файлы
        """
        sorted_runs = []
        run_count = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            while True:
                # Чтение порции данных, которая помещается в память
                lines = []
                current_size = 0
                
                while current_size < self.memory_limit:
                    line = f.readline()
                    if not line:
                        break
                    
                    # Для корректной обработки последней строки
                    if delimiter != '\n':
                        # Читаем до разделителя
                        while not line.endswith(delimiter):
                            next_line = f.readline()
                            if not next_line:
                                break
                            line += next_line
                    
                    lines.append(line)
                    current_size += sys.getsizeof(line)
                
                if not lines:
                    break
                
                # Сортировка в памяти
                if key_func:
                    lines.sort(key=key_func)
                else:
                    lines.sort()
                
                # Сохранение отсортированной части во временный файл
                temp_file = os.path.join(self.temp_dir, f'run_{run_count}.tmp')
                with open(temp_file, 'w', encoding='utf-8') as temp_f:
                    temp_f.writelines(lines)
                
                sorted_runs.append(temp_file)
                run_count += 1
                
                print(f"  Создана часть {run_count}: {len(lines)} строк, "
                      f"{os.path.getsize(temp_file) / 1024:.1f} KB")
        
        return sorted_runs
    
    def _multiway_merge(self, input_files: List[str], output_file: str, 
                       key_func, delimiter: str) -> None:
        """
        Многофазное слияние отсортированных файлов
        
        Использует кучу (heap) для эффективного слияния K файлов
        """
        if not input_files:
            return
        
        # Если файл только один, просто копируем его
        if len(input_files) == 1:
            with open(input_files[0], 'r', encoding='utf-8') as src, \
                 open(output_file, 'w', encoding='utf-8') as dst:
                dst.writelines(src)
            return
        
        # Открываем все файлы для чтения
        files = [open(f, 'r', encoding='utf-8') for f in input_files]
        
        # Инициализируем кучу с первыми элементами каждого файла
        heap = []
        
        for i, f in enumerate(files):
            line = self._read_line(f, delimiter)
            if line is not None:
                if key_func:
                    key = key_func(line)
                else:
                    key = line
                heapq.heappush(heap, (key, i, line))
        
        # Основной цикл слияния
        with open(output_file, 'w', encoding='utf-8') as out_f:
            while heap:
                # Извлекаем минимальный элемент
                key, file_idx, line = heapq.heappop(heap)
                out_f.write(line)
                
                # Читаем следующую строку из того же файла
                next_line = self._read_line(files[file_idx], delimiter)
                if next_line is not None:
                    if key_func:
                        next_key = key_func(next_line)
                    else:
                        next_key = next_line
                    heapq.heappush(heap, (next_key, file_idx, next_line))
        
        # Закрываем все файлы
        for f in files:
            f.close()
    
    def _read_line(self, file_obj, delimiter: str) -> Optional[str]:
        """
        Чтение строки с учетом заданного разделителя
        """
        if delimiter == '\n':
            line = file_obj.readline()
            return line if line else None
        
        # Для нестандартных разделителей
        result = []
        while True:
            char = file_obj.read(1)
            if not char:
                break
            
            result.append(char)
            if ''.join(result[-len(delimiter):]) == delimiter:
                return ''.join(result)
        
        return ''.join(result) if result else None
    
    def cleanup(self) -> None:
        """
        Очистка временных файлов
        """
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            print(f"Временная директория удалена: {self.temp_dir}")


def generate_large_file(filename: str, num_lines: int = 1000000) -> None:
    """
    Генерация большого файла для тестирования
    """
    import random
    import string
    
    print(f"Генерация тестового файла с {num_lines} строками...")
    
    with open(filename, 'w', encoding='utf-8') as f:
        for i in range(num_lines):
            # Генерируем случайную строку длиной 10-100 символов
            length = random.randint(10, 100)
            random_string = ''.join(
                random.choices(string.ascii_letters + string.digits + ' ', k=length)
            )
            f.write(f"{random_string}\n")
    
    print(f"Файл создан: {filename}")


def test_numeric_sort() -> None:
    """
    Тест сортировки числовых данных
    """
    print("\n=== Тест сортировки числовых данных ===")
    
    # Генерация тестового файла
    input_file = 'numbers_input.txt'
    output_file = 'numbers_sorted.txt'
    
    with open(input_file, 'w') as f:
        import random
        for _ in range(50000):
            f.write(f"{random.randint(1, 1000000)}\n")
    
    # Создание сортировщика с небольшим лимитом памяти (для демонстрации)
    sorter = ExternalMergeSort(memory_limit=10 * 1024 * 1024)  # 10 MB
    
    # Сортировка с ключом преобразования в число
    sorter.sort_file(
        input_file=input_file,
        output_file=output_file,
        key_func=lambda x: int(x.strip())
    )
    
    # Проверка результата
    with open(output_file, 'r') as f:
        lines = [int(line.strip()) for line in f.readlines()[:10]]
        print(f"Первые 10 чисел: {lines}")
        print("Проверка сортировки:", all(lines[i] <= lines[i+1] for i in range(len(lines)-1)))
    
    sorter.cleanup()


def test_string_sort() -> None:
    """
    Тест сортировки строковых данных
    """
    print("\n=== Тест сортировки строковых данных ===")
    
    input_file = 'strings_input.txt'
    output_file = 'strings_sorted.txt'
    
    # Генерация файла со случайными строками
    generate_large_file(input_file, 100000)
    
    # Сортировка
    sorter = ExternalMergeSort(memory_limit=5 * 1024 * 1024)  # 5 MB
    
    sorter.sort_file(
        input_file=input_file,
        output_file=output_file
    )
    
    # Быстрая проверка
    with open(output_file, 'r', encoding='utf-8') as f:
        lines = [f.readline().strip() for _ in range(5)]
        print(f"Первые 5 строк: {lines}")
        print("Проверка сортировки:", all(lines[i] <= lines[i+1] for i in range(len(lines)-1)))
    
    sorter.cleanup()


def test_csv_sort() -> None:
    """
    Тест сортировки CSV файла по определенной колонке
    """
    print("\n=== Тест сортировки CSV ===")
    
    input_file = 'data.csv'
    output_file = 'data_sorted.csv'
    
    # Генерация тестового CSV
    import random
    with open(input_file, 'w') as f:
        f.write("id,name,age,salary\n")
        for i in range(10000):
            name = f"User{random.randint(1, 10000)}"
            age = random.randint(20, 65)
            salary = random.randint(30000, 150000)
            f.write(f"{i+1},{name},{age},{salary}\n")
    
    # Сортировка по зарплате (4-я колонка)
    sorter = ExternalMergeSort(memory_limit=2 * 1024 * 1024)  # 2 MB
    
    def salary_key(line: str) -> int:
        # Пропускаем заголовок
        if line.startswith("id,"):
            return -1
        parts = line.strip().split(',')
        return int(parts[3]) if len(parts) >= 4 else 0
    
    sorter.sort_file(
        input_file=input_file,
        output_file=output_file,
        key_func=salary_key
    )
    
    # Показать статистику
    print("\nСтатистика отсортированного файла:")
    with open(output_file, 'r') as f:
        header = f.readline()
        print(f"Заголовок: {header.strip()}")
        
        # Показать несколько записей
        for _ in range(5):
            line = f.readline()
            if line:
                print(f"  Запись: {line.strip()}")
    
    sorter.cleanup()


def benchmark_sort() -> None:
    """
    Бенчмарк для разных размеров файлов
    """
    import time
    import psutil  # pip install psutil
    
    print("\n=== Бенчмарк производительности ===")
    
    sizes = [100000, 500000, 1000000]  # Количество строк
    memory_limits = [1 * 1024 * 1024, 10 * 1024 * 1024]  # 1 MB и 10 MB
    
    for size in sizes:
        for mem_limit in memory_limits:
            print(f"\nТест: {size} строк, лимит памяти: {mem_limit / (1024*1024):.1f} MB")
            
            # Генерация файла
            input_file = f'benchmark_{size}.txt'
            output_file = f'benchmark_{size}_sorted.txt'
            
            generate_large_file(input_file, size)
            
            # Замер памяти и времени
            process = psutil.Process()
            start_time = time.time()
            start_memory = process.memory_info().rss
            
            # Сортировка
            sorter = ExternalMergeSort(memory_limit=mem_limit)
            sorter.sort_file(input_file, output_file)
            sorter.cleanup()
            
            end_time = time.time()
            end_memory = process.memory_info().rss
            
            print(f"  Время: {end_time - start_time:.2f} сек")
            print(f"  Пиковая память: {(end_memory - start_memory) / (1024*1024):.2f} MB")
            
            # Удаление временных файлов
            os.remove(input_file)
            os.remove(output_file)


if __name__ == "__main__":
    print("=== Демонстрация External Merge Sort ===")
    
    # Меню выбора теста
    tests = {
        '1': ('Сортировка чисел', test_numeric_sort),
        '2': ('Сортировка строк', test_string_sort),
        '3': ('Сортировка CSV', test_csv_sort),
        '4': ('Бенчмарк', benchmark_sort),
    }
    
    print("\nВыберите тест:")
    for key, (name, _) in tests.items():
        print(f"  {key}. {name}")
    
    choice = input("\nВаш выбор (1-4, Enter для всех): ").strip()
    
    if choice == '':
        # Запуск всех тестов
        for _, (_, test_func) in tests.items():
            test_func()
    elif choice in tests:
        tests[choice][1]()
    else:
        print("Неверный выбор")
    
    print("\n=== Все тесты завершены ===")