import matplotlib.pyplot as plt
import random
import math
from typing import List, Tuple, Optional
import time

class Point:
    """Класс для представления точки в 2D пространстве"""
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y)
    
    def __eq__(self, other: 'Point') -> bool:
        return math.isclose(self.x, other.x) and math.isclose(self.y, other.y)
    
    def __lt__(self, other: 'Point') -> bool:
        """Для сортировки по полярному углу"""
        return False  # Не используется напрямую
    
    def __repr__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"
    
    def distance_sq(self, other: 'Point') -> float:
        """Квадрат расстояния между точками"""
        dx = self.x - other.x
        dy = self.y - other.y
        return dx * dx + dy * dy

class GrahamScan:
    """
    Реализация алгоритма Грэхема для построения выпуклой оболочки
    
    Алгоритм состоит из шагов:
    1. Найти точку с минимальной y-координатой (стартовая)
    2. Отсортировать все точки по полярному углу относительно стартовой
    3. Построить выпуклую оболочку, убирая точки, создающие правый поворот
    """
    
    @staticmethod
    def cross_product(o: Point, a: Point, b: Point) -> float:
        """
        Векторное произведение (cross product) векторов OA и OB
        Возвращает:
          > 0: левый поворот (counter-clockwise)
          = 0: точки коллинеарны
          < 0: правый поворот (clockwise)
        """
        return (a.x - o.x) * (b.y - o.y) - (a.y - o.y) * (b.x - o.x)
    
    @staticmethod
    def find_pivot(points: List[Point]) -> Point:
        """
        Находит точку с минимальной y-координатой (и минимальной x при равенстве)
        Эта точка гарантированно входит в выпуклую оболочку
        """
        pivot = points[0]
        for p in points[1:]:
            if p.y < pivot.y or (math.isclose(p.y, pivot.y) and p.x < pivot.x):
                pivot = p
        return pivot
    
    @staticmethod
    def polar_angle(pivot: Point, p: Point) -> Tuple[float, float]:
        """
        Вычисляет полярный угол и расстояние для сортировки
        Возвращает кортеж (угол, квадрат расстояния)
        """
        dx = p.x - pivot.x
        dy = p.y - pivot.y
        angle = math.atan2(dy, dx)
        # Нормализуем угол в диапазон [0, 2π)
        if angle < 0:
            angle += 2 * math.pi
        distance = dx * dx + dy * dy
        return (angle, distance)
    
    @staticmethod
    def sort_by_polar_angle(pivot: Point, points: List[Point]) -> List[Point]:
        """
        Сортирует точки по полярному углу относительно pivot
        При равных углах ближние точки идут раньше
        """
        # Удаляем pivot из списка
        points = [p for p in points if p != pivot]
        
        # Сортируем по углу, затем по расстоянию
        points.sort(key=lambda p: GrahamScan.polar_angle(pivot, p))
        
        return points
    
    @staticmethod
    def remove_collinear(pivot: Point, points: List[Point]) -> List[Point]:
        """
        Удаляет коллинеарные точки, оставляя только самые дальние
        """
        if not points:
            return points
        
        result = [points[0]]
        for i in range(1, len(points)):
            # Пропускаем точки, совпадающие с pivot
            if points[i] == pivot:
                continue
            
            # Пропускаем точки, совпадающие с предыдущими
            if points[i] == result[-1]:
                continue
            
            # Проверяем коллинеарность
            cross = GrahamScan.cross_product(pivot, result[-1], points[i])
            if math.isclose(cross, 0):
                # Оставляем более дальнюю точку
                d1 = pivot.distance_sq(result[-1])
                d2 = pivot.distance_sq(points[i])
                if d2 > d1:
                    result[-1] = points[i]
            else:
                result.append(points[i])
        
        return result
    
    @staticmethod
    def convex_hull(points: List[Point]) -> List[Point]:
        """
        Основная функция: строит выпуклую оболочку по алгоритму Грэхема
        
        Args:
            points: список точек
            
        Returns:
            Список точек выпуклой оболочки в порядке обхода против часовой стрелки
        """
        if len(points) < 3:
            return points.copy()  # Выпуклая оболочка - все точки
        
        # Шаг 1: Находим опорную точку (pivot)
        pivot = GrahamScan.find_pivot(points)
        
        # Шаг 2: Сортируем по полярному углу
        sorted_points = GrahamScan.sort_by_polar_angle(pivot, points)
        
        # Удаляем коллинеарные точки
        sorted_points = GrahamScan.remove_collinear(pivot, sorted_points)
        
        # Если после удаления коллинеарных точек осталось мало точек
        if len(sorted_points) < 2:
            return [pivot] + sorted_points
        
        # Шаг 3: Строим выпуклую оболочку
        stack = [pivot, sorted_points[0]]
        
        for i in range(1, len(sorted_points)):
            while len(stack) >= 2:
                # Проверяем направление поворота
                cross = GrahamScan.cross_product(stack[-2], stack[-1], sorted_points[i])
                
                if cross > 0:  # Левый поворот - оставляем
                    break
                elif cross < 0:  # Правый поворот - удаляем последнюю точку
                    stack.pop()
                else:  # Коллинеарны - оставляем более дальнюю
                    d1 = stack[-2].distance_sq(stack[-1])
                    d2 = stack[-2].distance_sq(sorted_points[i])
                    if d2 > d1:
                        stack.pop()
                    else:
                        break
            
            stack.append(sorted_points[i])
        
        return stack
    
    @staticmethod
    def convex_hull_with_steps(points: List[Point]) -> Tuple[List[Point], List[List[Point]]]:
        """
        Версия с сохранением промежуточных шагов для визуализации
        """
        steps = []
        
        if len(points) < 3:
            steps.append(points.copy())
            return points.copy(), steps
        
        # Шаг 1: Находим pivot
        pivot = GrahamScan.find_pivot(points)
        steps.append([pivot])
        
        # Шаг 2: Сортировка
        sorted_points = GrahamScan.sort_by_polar_angle(pivot, points)
        steps.append([pivot] + sorted_points)
        
        # Шаг 3: Построение с сохранением промежуточных состояний
        stack = [pivot, sorted_points[0]]
        steps.append(stack.copy())
        
        for i in range(1, len(sorted_points)):
            while len(stack) >= 2:
                cross = GrahamScan.cross_product(stack[-2], stack[-1], sorted_points[i])
                
                if cross > 0:
                    break
                elif cross < 0:
                    stack.pop()
                    steps.append(stack.copy())
                else:
                    d1 = stack[-2].distance_sq(stack[-1])
                    d2 = stack[-2].distance_sq(sorted_points[i])
                    if d2 > d1:
                        stack.pop()
                        steps.append(stack.copy())
                    else:
                        break
            
            stack.append(sorted_points[i])
            steps.append(stack.copy())
        
        return stack, steps


def generate_random_points(n: int, seed: Optional[int] = None) -> List[Point]:
    """Генерация случайных точек"""
    if seed is not None:
        random.seed(seed)
    
    points = []
    for _ in range(n):
        x = random.uniform(0, 100)
        y = random.uniform(0, 100)
        points.append(Point(x, y))
    
    return points


def generate_points_on_circle(n: int, radius: float = 50) -> List[Point]:
    """Генерация точек на окружности (все точки в выпуклой оболочке)"""
    points = []
    for i in range(n):
        angle = 2 * math.pi * i / n
        x = radius * math.cos(angle) + 50
        y = radius * math.sin(angle) + 50
        points.append(Point(x, y))
    
    # Добавляем немного шума
    for p in points:
        p.x += random.uniform(-5, 5)
        p.y += random.uniform(-5, 5)
    
    return points


def generate_collinear_points(n: int) -> List[Point]:
    """Генерация коллинеарных точек"""
    points = []
    for i in range(n):
        x = i * 10
        y = 2 * x + 3  # y = 2x + 3
        points.append(Point(x, y))
    
    # Добавляем несколько неколлинеарных точек
    points.append(Point(30, 10))
    points.append(Point(70, 90))
    
    return points


def plot_convex_hull(points: List[Point], hull: List[Point], 
                     title: str = "Алгоритм Грэхема", show: bool = True):
    """
    Визуализация точек и выпуклой оболочки
    """
    plt.figure(figsize=(10, 8))
    
    # Рисуем все точки
    x_vals = [p.x for p in points]
    y_vals = [p.y for p in points]
    plt.scatter(x_vals, y_vals, c='blue', alpha=0.6, label='Все точки')
    
    # Выделяем опорную точку (pivot)
    if hull:
        pivot = hull[0]
        plt.scatter([pivot.x], [pivot.y], c='red', s=200, 
                   marker='*', label='Опорная точка', zorder=5)
    
    # Рисуем выпуклую оболочку
    if hull:
        hull_x = [p.x for p in hull] + [hull[0].x]
        hull_y = [p.y for p in hull] + [hull[0].y]
        plt.plot(hull_x, hull_y, 'r-', linewidth=2, label='Выпуклая оболочка')
        
        # Закрашиваем область
        plt.fill(hull_x, hull_y, 'red', alpha=0.1)
    
    # Настройки графика
    plt.title(title, fontsize=16)
    plt.xlabel('X', fontsize=14)
    plt.ylabel('Y', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.axis('equal')
    
    if show:
        plt.show()
    
    return plt


def plot_animation_steps(points: List[Point], steps: List[List[Point]]):
    """
    Анимированное отображение шагов алгоритма
    """
    from matplotlib.animation import FuncAnimation
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Все точки
    x_vals = [p.x for p in points]
    y_vals = [p.y for p in points]
    ax.scatter(x_vals, y_vals, c='blue', alpha=0.3)
    
    # Начальные элементы
    hull_line, = ax.plot([], [], 'r-', linewidth=2)
    current_point = ax.scatter([], [], c='green', s=100, zorder=5)
    
    def init():
        hull_line.set_data([], [])
        current_point.set_offsets([])
        return hull_line, current_point
    
    def update(frame):
        step = steps[frame]
        
        if len(step) > 1:
            hull_x = [p.x for p in step] + [step[0].x]
            hull_y = [p.y for p in step] + [step[0].y]
            hull_line.set_data(hull_x, hull_y)
        else:
            hull_line.set_data([], [])
        
        # Текущая обрабатываемая точка
        if frame < len(steps) - 1 and len(steps[frame + 1]) > len(step):
            new_point = steps[frame + 1][-1]
            current_point.set_offsets([[new_point.x, new_point.y]])
        else:
            current_point.set_offsets([])
        
        ax.set_title(f'Шаг {frame + 1}/{len(steps)}', fontsize=16)
        
        return hull_line, current_point
    
    anim = FuncAnimation(fig, update, frames=len(steps),
                        init_func=init, blit=True, interval=500)
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(True, alpha=0.3)
    plt.axis('equal')
    plt.show()
    
    return anim


def benchmark_graham_scan():
    """
    Бенчмарк производительности алгоритма
    """
    print("=== Бенчмарк алгоритма Грэхема ===")
    
    sizes = [100, 500, 1000, 5000, 10000]
    
    for size in sizes:
        # Генерируем точки
        points = generate_random_points(size, seed=42)
        
        # Замер времени
        start_time = time.time()
        hull = GrahamScan.convex_hull(points)
        end_time = time.time()
        
        print(f"Точек: {size:6d} -> Выпуклая оболочка: {len(hull):4d} точек "
              f"Время: {(end_time - start_time) * 1000:6.2f} мс")


def test_edge_cases():
    """
    Тестирование граничных случаев
    """
    print("\n=== Тестирование граничных случаев ===")
    
    # 1. Всего 1 точка
    points = [Point(10, 20)]
    hull = GrahamScan.convex_hull(points)
    print(f"1 точка: {points} -> hull: {hull}")
    
    # 2. 2 точки
    points = [Point(10, 20), Point(30, 40)]
    hull = GrahamScan.convex_hull(points)
    print(f"2 точки: {points} -> hull: {hull}")
    
    # 3. 3 точки (уже выпуклая оболочка)
    points = [Point(0, 0), Point(10, 0), Point(5, 10)]
    hull = GrahamScan.convex_hull(points)
    print(f"3 точки (треугольник): hull: {hull}")
    
    # 4. Все точки коллинеарны
    points = [Point(0, 0), Point(5, 5), Point(10, 10), Point(15, 15)]
    hull = GrahamScan.convex_hull(points)
    print(f"Коллинеарные точки: hull: {hull}")
    
    # 5. Точки образуют прямоугольник
    points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10),
              Point(5, 5), Point(2, 3), Point(8, 7)]  # Внутренние точки
    hull = GrahamScan.convex_hull(points)
    print(f"Прямоугольник + внутренние точки: hull имеет {len(hull)} вершин")


def interactive_demo():
    """
    Интерактивная демонстрация алгоритма
    """
    print("\n=== Интерактивная демонстрация ===")
    
    while True:
        print("\nВыберите тип данных:")
        print("1. Случайные точки")
        print("2. Точки на окружности")
        print("3. Коллинеарные точки + шум")
        print("4. Ввести свои точки")
        print("0. Выход")
        
        choice = input("Ваш выбор: ").strip()
        
        if choice == '0':
            break
        
        if choice == '1':
            n = int(input("Количество точек: "))
            points = generate_random_points(n)
        elif choice == '2':
            n = int(input("Количество точек: "))
            points = generate_points_on_circle(n)
        elif choice == '3':
            n = int(input("Количество точек: "))
            points = generate_collinear_points(n)
        elif choice == '4':
            points = []
            print("Введите точки в формате 'x y' (пустая строка для завершения):")
            while True:
                line = input().strip()
                if not line:
                    break
                try:
                    x, y = map(float, line.split())
                    points.append(Point(x, y))
                except:
                    print("Ошибка формата, используйте 'x y'")
        else:
            print("Неверный выбор")
            continue
        
        if not points:
            print("Нет точек для обработки")
            continue
        
        print(f"\nОбрабатывается {len(points)} точек")
        
        # Запускаем алгоритм
        hull, steps = GrahamScan.convex_hull_with_steps(points)
        
        print(f"Выпуклая оболочка содержит {len(hull)} точек:")
        for i, p in enumerate(hull):
            print(f"  {i+1}: {p}")
        
        # Визуализация
        plot_convex_hull(points, hull, f"Выпуклая оболочка ({len(hull)} вершин)")
        
        # Анимация шагов
        animate = input("Показать анимацию шагов? (y/n): ").strip().lower()
        if animate == 'y':
            plot_animation_steps(points, steps)


if __name__ == "__main__":
    print("=== Алгоритм Грэхема (Graham Scan) для построения выпуклой оболочки ===")
    
    # Демонстрационный пример
    print("\n--- Демонстрационный пример ---")
    
    # Генерируем случайные точки
    points = generate_random_points(50, seed=42)
    
    # Строим выпуклую оболочку
    hull = GrahamScan.convex_hull(points)
    
    print(f"Всего точек: {len(points)}")
    print(f"Точек в выпуклой оболочке: {len(hull)}")
    print(f"Выпуклая оболочка: {hull}")
    
    # Визуализация
    plot_convex_hull(points, hull, "Graham Scan - Демонстрация")
    
    # Бенчмарк
    benchmark_graham_scan()
    
    # Тестирование граничных случаев
    test_edge_cases()
    
    # Интерактивная демонстрация
    # interactive_demo()