import networkx as nx
import matplotlib.pyplot as plt
from collections import deque
import heapq
import math
from typing import List, Tuple, Dict, Optional, Set
import time

class Edge:
    """Класс для представления ребра в сети"""
    def __init__(self, u: int, v: int, capacity: float):
        self.u = u  # Начальная вершина
        self.v = v  # Конечная вершина
        self.capacity = capacity  # Пропускная способность
        self.flow = 0.0  # Текущий поток
    
    def __repr__(self) -> str:
        return f"Edge({self.u}→{self.v}: {self.flow}/{self.capacity})"
    
    def residual_capacity(self, forward: bool = True) -> float:
        """Остаточная пропускная способность"""
        if forward:
            return self.capacity - self.flow
        else:
            return self.flow
    
    def add_flow(self, flow: float, forward: bool = True) -> None:
        """Добавляет поток к ребру"""
        if forward:
            self.flow += flow
        else:
            self.flow -= flow


class FlowNetwork:
    """Представление сети для алгоритма Форда-Фалкерсона"""
    
    def __init__(self, n: int):
        """
        Args:
            n: количество вершин (0..n-1)
        """
        self.n = n
        self.adj: List[List[Edge]] = [[] for _ in range(n)]
        self.edges: List[Edge] = []
        
        # Для визуализации
        self.pos = None  # Позиции вершин для отрисовки
    
    def add_edge(self, u: int, v: int, capacity: float) -> None:
        """Добавляет направленное ребро u → v"""
        edge = Edge(u, v, capacity)
        self.adj[u].append(edge)
        self.edges.append(edge)
    
    def add_bidirectional_edge(self, u: int, v: int, capacity: float) -> None:
        """Добавляет два направленных ребра (u→v и v→u)"""
        self.add_edge(u, v, capacity)
        self.add_edge(v, u, 0)  # Обратное ребро для алгоритма
    
    def get_residual_graph(self) -> 'FlowNetwork':
        """Создает остаточную сеть"""
        residual = FlowNetwork(self.n)
        
        for edge in self.edges:
            # Прямое ребро (если есть остаточная capacity)
            if edge.flow < edge.capacity:
                residual.add_edge(edge.u, edge.v, edge.capacity - edge.flow)
            
            # Обратное ребро (если есть поток)
            if edge.flow > 0:
                residual.add_edge(edge.v, edge.u, edge.flow)
        
        return residual
    
    def max_flow_bfs(self, source: int, sink: int) -> float:
        """
        Алгоритм Форда-Фалкерсона с BFS (Эдмондс-Карп)
        
        Args:
            source: исток
            sink: сток
            
        Returns:
            Максимальный поток
        """
        max_flow = 0.0
        
        while True:
            # Шаг 1: Ищем увеличивающий путь в остаточной сети с помощью BFS
            parent = [-1] * self.n
            parent_edge = [None] * self.n
            
            queue = deque([source])
            parent[source] = source
            
            found = False
            while queue and not found:
                u = queue.popleft()
                
                for edge in self.adj[u]:
                    residual = edge.capacity - edge.flow
                    if residual > 0 and parent[edge.v] == -1:
                        parent[edge.v] = u
                        parent_edge[edge.v] = edge
                        
                        if edge.v == sink:
                            found = True
                            break
                        
                        queue.append(edge.v)
            
            # Если путь не найден - завершаем
            if not found:
                break
            
            # Шаг 2: Находим минимальную остаточную пропускную способность на пути
            path_flow = float('inf')
            v = sink
            
            while v != source:
                u = parent[v]
                edge = parent_edge[v]
                residual = edge.capacity - edge.flow
                path_flow = min(path_flow, residual)
                v = u
            
            # Шаг 3: Увеличиваем поток вдоль пути
            v = sink
            while v != source:
                u = parent[v]
                edge = parent_edge[v]
                edge.flow += path_flow
                v = u
            
            max_flow += path_flow
        
        return max_flow
    
    def max_flow_dfs(self, source: int, sink: int) -> float:
        """
        Алгоритм Форда-Фалкерсона с DFS
        
        Args:
            source: исток
            sink: сток
            
        Returns:
            Максимальный поток
        """
        max_flow = 0.0
        
        def dfs(u: int, min_capacity: float, visited: List[bool]) -> float:
            """Рекурсивный DFS для поиска увеличивающего пути"""
            if u == sink:
                return min_capacity
            
            visited[u] = True
            
            for edge in self.adj[u]:
                residual = edge.capacity - edge.flow
                if residual > 0 and not visited[edge.v]:
                    flow = dfs(edge.v, min(min_capacity, residual), visited)
                    if flow > 0:
                        edge.flow += flow
                        return flow
            
            return 0.0
        
        while True:
            visited = [False] * self.n
            flow = dfs(source, float('inf'), visited)
            
            if flow == 0:
                break
            
            max_flow += flow
        
        return max_flow
    
    def max_flow_dijkstra(self, source: int, sink: int) -> float:
        """
        Алгоритм Диница (улучшенная версия Форда-Фалкерсона)
        с использованием BFS для построения слоистой сети
        """
        max_flow = 0.0
        
        while True:
            # Шаг 1: Строим слоистую сеть (BFS)
            level = [-1] * self.n
            level[source] = 0
            
            queue = deque([source])
            while queue:
                u = queue.popleft()
                for edge in self.adj[u]:
                    if edge.capacity - edge.flow > 0 and level[edge.v] == -1:
                        level[edge.v] = level[u] + 1
                        queue.append(edge.v)
            
            # Если сток недостижим
            if level[sink] == -1:
                break
            
            # Шаг 2: Блокирующий поток (DFS с ограничением глубины)
            ptr = [0] * self.n  # указатели для оптимизации
            
            def dfs_dinic(u: int, flow: float) -> float:
                if u == sink:
                    return flow
                
                for i in range(ptr[u], len(self.adj[u])):
                    edge = self.adj[u][i]
                    if level[edge.v] == level[u] + 1 and edge.capacity - edge.flow > 0:
                        pushed = dfs_dinic(edge.v, min(flow, edge.capacity - edge.flow))
                        if pushed > 0:
                            edge.flow += pushed
                            return pushed
                    ptr[u] += 1
                
                return 0
            
            while True:
                flow = dfs_dinic(source, float('inf'))
                if flow == 0:
                    break
                max_flow += flow
        
        return max_flow
    
    def find_min_cut(self, source: int) -> Tuple[Set[int], Set[int]]:
        """
        Находит минимальный разрез после вычисления максимального потока
        
        Args:
            source: исток
            
        Returns:
            (S, T) - разбиение вершин на две доли
        """
        visited = [False] * self.n
        
        # BFS в остаточной сети
        queue = deque([source])
        visited[source] = True
        
        while queue:
            u = queue.popleft()
            for edge in self.adj[u]:
                if edge.capacity - edge.flow > 0 and not visited[edge.v]:
                    visited[edge.v] = True
                    queue.append(edge.v)
        
        # Разбиваем вершины
        S = {i for i in range(self.n) if visited[i]}
        T = {i for i in range(self.n) if not visited[i]}
        
        return S, T
    
    def visualize(self, title: str = "Сеть потока", show_flow: bool = True):
        """
        Визуализация сети с помощью networkx
        """
        G = nx.DiGraph()
        
        # Добавляем вершины
        for i in range(self.n):
            G.add_node(i)
        
        # Добавляем ребра
        edge_labels = {}
        for edge in self.edges:
            if edge.capacity > 0:  # Пропускаем нулевые обратные ребра
                G.add_edge(edge.u, edge.v)
                
                if show_flow:
                    label = f"{edge.flow:.1f}/{edge.capacity:.1f}"
                    if edge.flow > 0:
                        # Выделяем ребра с ненулевым потоком
                        edge_labels[(edge.u, edge.v)] = label
        
        # Расположение вершин
        if self.pos is None:
            self.pos = nx.spring_layout(G, seed=42)
        
        # Рисуем граф
        plt.figure(figsize=(12, 8))
        
        # Вершины
        nx.draw_networkx_nodes(G, self.pos, node_color='lightblue', 
                              node_size=500, alpha=0.8)
        
        # Ребра
        nx.draw_networkx_edges(G, self.pos, edge_color='gray', 
                              arrows=True, arrowsize=20, width=2)
        
        # Метки вершин
        nx.draw_networkx_labels(G, self.pos, font_size=12, font_weight='bold')
        
        # Метки ребер
        nx.draw_networkx_edge_labels(G, self.pos, edge_labels=edge_labels,
                                    font_color='red', font_size=10)
        
        plt.title(title, fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        plt.show()


def create_example_network() -> FlowNetwork:
    """Создает пример сети из классического примера"""
    network = FlowNetwork(6)
    
    # Вершины: 0 - источник, 5 - сток
    network.add_bidirectional_edge(0, 1, 16)
    network.add_bidirectional_edge(0, 2, 13)
    network.add_bidirectional_edge(1, 2, 10)
    network.add_bidirectional_edge(1, 3, 12)
    network.add_bidirectional_edge(2, 1, 4)
    network.add_bidirectional_edge(2, 4, 14)
    network.add_bidirectional_edge(3, 2, 9)
    network.add_bidirectional_edge(3, 5, 20)
    network.add_bidirectional_edge(4, 3, 7)
    network.add_bidirectional_edge(4, 5, 4)
    
    return network


def create_bipartite_matching() -> FlowNetwork:
    """
    Создает сеть для задачи о максимальном паросочетании
    в двудольном графе
    """
    # Пример: 3 работника, 3 задания
    # Вершины 0-2: работники, 3-5: задания
    # Источник: 6, Сток: 7
    network = FlowNetwork(8)
    
    source = 6
    sink = 7
    
    # Работники
    workers = [0, 1, 2]
    jobs = [3, 4, 5]
    
    # Связи работников с заданиями
    edges = [
        (0, 3), (0, 4),  # Работник 0 может делать задания 3 и 4
        (1, 3), (1, 5),  # Работник 1 может делать задания 3 и 5
        (2, 4), (2, 5),  # Работник 2 может делать задания 4 и 5
    ]
    
    # Ребра от источника к работникам
    for w in workers:
        network.add_bidirectional_edge(source, w, 1)
    
    # Ребра от работников к заданиям
    for u, v in edges:
        network.add_bidirectional_edge(u, v, 1)
    
    # Ребра от заданий к стоку
    for j in jobs:
        network.add_bidirectional_edge(j, sink, 1)
    
    return network, workers, jobs, source, sink


def create_transport_problem() -> FlowNetwork:
    """
    Создает сеть для транспортной задачи
    (заводы → склады → магазины)
    """
    network = FlowNetwork(10)
    
    # Вершины
    factories = [0, 1, 2]  # Заводы
    warehouses = [3, 4, 5]  # Склады
    stores = [6, 7, 8]  # Магазины
    source = 9  # Источник
    sink = 10   # Сток
    
    # Пропускные способности
    factory_capacities = [100, 150, 120]  # Производство заводов
    warehouse_limits = [80, 100, 90]      # Вместимость складов
    store_demands = [60, 70, 80]          # Спрос магазинов
    
    # Добавляем вершины стока
    network.n = 11
    
    # Ребра источник → заводы
    for i, factory in enumerate(factories):
        network.add_bidirectional_edge(source, factory, factory_capacities[i])
    
    # Ребра заводы → склады
    factory_warehouse_edges = [
        (0, 3, 50), (0, 4, 60),  # Завод 0 → склады
        (1, 3, 40), (1, 4, 70), (1, 5, 40),  # Завод 1 → склады
        (2, 4, 30), (2, 5, 90),  # Завод 2 → склады
    ]
    
    for u, v, cap in factory_warehouse_edges:
        network.add_bidirectional_edge(u, v, cap)
    
    # Ребра склады → магазины
    warehouse_store_edges = [
        (3, 6, 40), (3, 7, 30),  # Склад 3 → магазины
        (4, 6, 20), (4, 7, 50), (4, 8, 30),  # Склад 4 → магазины
        (5, 7, 40), (5, 8, 50),  # Склад 5 → магазины
    ]
    
    for u, v, cap in warehouse_store_edges:
        network.add_bidirectional_edge(u, v, cap)
    
    # Ребра магазины → сток
    for i, store in enumerate(stores):
        network.add_bidirectional_edge(store, sink, store_demands[i])
    
    return network, source, sink


def benchmark_algorithms():
    """Сравнение производительности разных алгоритмов"""
    print("=== Бенчмарк алгоритмов поиска максимального потока ===")
    
    # Создаем сеть разного размера
    sizes = [10, 20, 50, 100]
    
    for size in sizes:
        # Создаем случайную сеть
        network = FlowNetwork(size)
        
        # Добавляем случайные ребра
        import random
        edge_count = size * 3
        
        for _ in range(edge_count):
            u = random.randint(0, size-2)
            v = random.randint(u+1, size-1)
            capacity = random.randint(1, 100)
            network.add_bidirectional_edge(u, v, capacity)
        
        source = 0
        sink = size - 1
        
        # Тестируем разные алгоритмы
        algorithms = [
            ("BFS (Эдмондс-Карп)", network.max_flow_bfs),
            ("DFS", network.max_flow_dfs),
            ("Диница", network.max_flow_dijkstra),
        ]
        
        print(f"\nСеть: {size} вершин, {edge_count} ребер")
        
        for name, algorithm in algorithms:
            # Копируем сеть для каждого алгоритма
            test_network = FlowNetwork(size)
            test_network.adj = [[edge for edge in edges] for edges in network.adj]
            test_network.edges = [edge for edge in network.edges]
            
            start_time = time.time()
            max_flow = algorithm(test_network, source, sink)
            end_time = time.time()
            
            print(f"  {name:20s}: поток = {max_flow:8.2f}, "
                  f"время = {(end_time - start_time)*1000:6.2f} мс")


def solve_max_flow_problem():
    """Решение задачи максимального потока с визуализацией"""
    print("\n=== Пример 1: Классическая сеть ===")
    
    # Создаем сеть
    network = create_example_network()
    
    # Визуализируем исходную сеть
    print("Исходная сеть:")
    for edge in network.edges:
        if edge.capacity > 0:  # Показываем только ненулевые ребра
            print(f"  {edge.u} → {edge.v}: capacity = {edge.capacity}")
    
    network.visualize("Исходная сеть", show_flow=False)
    
    # Вычисляем максимальный поток
    source = 0
    sink = 5
    
    max_flow = network.max_flow_bfs(source, sink)
    print(f"\nМаксимальный поток из {source} в {sink}: {max_flow}")
    
    # Показываем поток на каждом ребре
    print("\nПотоки на ребрах:")
    for edge in network.edges:
        if edge.flow > 0 or edge.capacity > 0:
            print(f"  {edge.u} → {edge.v}: {edge.flow:.1f}/{edge.capacity:.1f}")
    
    # Находим минимальный разрез
    S, T = network.find_min_cut(source)
    print(f"\nМинимальный разрез:")
    print(f"  S = {sorted(S)}")
    print(f"  T = {sorted(T)}")
    
    # Показываем ребра разреза
    cut_edges = []
    for edge in network.edges:
        if edge.u in S and edge.v in T and edge.capacity > 0:
            cut_edges.append(edge)
    
    print("  Ребра разреза:")
    for edge in cut_edges:
        print(f"    {edge.u} → {edge.v}: capacity = {edge.capacity}")
    
    # Визуализируем результат
    network.visualize(f"Максимальный поток = {max_flow}")


def solve_bipartite_matching():
    """Решение задачи о максимальном паросочетании"""
    print("\n=== Пример 2: Максимальное паросочетание в двудольном графе ===")
    
    network, workers, jobs, source, sink = create_bipartite_matching()
    
    print("Работники:", workers)
    print("Задания:", jobs)
    
    # Вычисляем максимальный поток
    max_flow = network.max_flow_bfs(source, sink)
    print(f"\nМаксимальное паросочетание (размер): {int(max_flow)}")
    
    # Находим соответствия
    print("\nНайденные соответствия:")
    matches = []
    for edge in network.edges:
        if edge.u in workers and edge.v in jobs and edge.flow > 0:
            matches.append((edge.u, edge.v))
            print(f"  Работник {edge.u} → Задание {edge.v}")
    
    # Визуализация
    G = nx.DiGraph()
    
    # Добавляем вершины с цветами
    for i in range(network.n):
        if i == source:
            G.add_node(i, color='green', label='Источник')
        elif i == sink:
            G.add_node(i, color='red', label='Сток')
        elif i in workers:
            G.add_node(i, color='lightblue', label=f'W{i}')
        elif i in jobs:
            G.add_node(i, color='lightgreen', label=f'J{i-3}')
    
    # Добавляем ребра
    for edge in network.edges:
        if edge.capacity > 0:
            G.add_edge(edge.u, edge.v, capacity=edge.capacity, flow=edge.flow,
                      color='red' if edge.flow > 0 else 'gray')
    
    # Рисуем
    plt.figure(figsize=(10, 8))
    
    pos = nx.bipartite_layout(G, workers + [source, sink])
    
    # Раскраска вершин
    colors = []
    for i in range(network.n):
        if i == source:
            colors.append('green')
        elif i == sink:
            colors.append('red')
        elif i in workers:
            colors.append('lightblue')
        else:
            colors.append('lightgreen')
    
    nx.draw_networkx_nodes(G, pos, node_color=colors, node_size=500)
    
    # Ребра
    edge_colors = []
    edge_widths = []
    for u, v, data in G.edges(data=True):
        if data.get('flow', 0) > 0:
            edge_colors.append('red')
            edge_widths.append(3)
        else:
            edge_colors.append('gray')
            edge_widths.append(1)
    
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths,
                          arrows=True, arrowsize=20)
    
    # Метки
    labels = {i: G.nodes[i].get('label', str(i)) for i in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=12)
    
    plt.title(f"Максимальное паросочетание (размер = {int(max_flow)})", fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def solve_transport_problem():
    """Решение транспортной задачи"""
    print("\n=== Пример 3: Транспортная задача ===")
    
    network, source, sink = create_transport_problem()
    
    print("Транспортная сеть:")
    print("  Заводы: 0, 1, 2")
    print("  Склады: 3, 4, 5")
    print("  Магазины: 6, 7, 8")
    print(f"  Источник: {source}, Сток: {sink}")
    
    # Вычисляем максимальный поток
    max_flow = network.max_flow_bfs(source, sink)
    print(f"\nМаксимальный поток (объем поставок): {max_flow}")
    
    # Анализируем потоки
    print("\nПотоки по маршрутам:")
    
    # Заводы → Склады
    print("Заводы → Склады:")
    for edge in network.edges:
        if edge.u in [0, 1, 2] and edge.v in [3, 4, 5] and edge.flow > 0:
            print(f"  Завод {edge.u} → Склад {edge.v-3}: {edge.flow:.1f}")
    
    # Склады → Магазины
    print("\nСклады → Магазины:")
    for edge in network.edges:
        if edge.u in [3, 4, 5] and edge.v in [6, 7, 8] and edge.flow > 0:
            print(f"  Склад {edge.u-3} → Магазин {edge.v-6}: {edge.flow:.1f}")


def interactive_solver():
    """Интерактивный решатель задач потока"""
    print("\n=== Интерактивный режим ===")
    
    while True:
        print("\nВыберите задачу:")
        print("1. Классическая задача максимального потока")
        print("2. Максимальное паросочетание")
        print("3. Транспортная задача")
        print("4. Создать свою сеть")
        print("0. Выход")
        
        choice = input("Ваш выбор: ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            solve_max_flow_problem()
        elif choice == '2':
            solve_bipartite_matching()
        elif choice == '3':
            solve_transport_problem()
        elif choice == '4':
            custom_network_solver()
        else:
            print("Неверный выбор")


def custom_network_solver():
    """Решение пользовательской сети"""
    print("\n=== Создание пользовательской сети ===")
    
    n = int(input("Количество вершин: "))
    network = FlowNetwork(n)
    
    print(f"Вершины пронумерованы от 0 до {n-1}")
    source = int(input("Номер истока: "))
    sink = int(input("Номер стока: "))
    
    print("\nВведите ребра в формате 'u v capacity' (пустая строка для завершения):")
    while True:
        line = input().strip()
        if not line:
            break
        
        try:
            u, v, cap = map(float, line.split())
            network.add_bidirectional_edge(int(u), int(v), cap)
        except:
            print("Ошибка формата, используйте 'u v capacity'")
    
    # Вычисляем максимальный поток
    print("\nВыберите алгоритм:")
    print("1. BFS (Эдмондс-Карп)")
    print("2. DFS")
    print("3. Алгоритм Диница")
    
    algo_choice = input("Ваш выбор: ").strip()
    
    if algo_choice == '1':
        max_flow = network.max_flow_bfs(source, sink)
        algo_name = "BFS (Эдмондс-Карп)"
    elif algo_choice == '2':
        max_flow = network.max_flow_dfs(source, sink)
        algo_name = "DFS"
    elif algo_choice == '3':
        max_flow = network.max_flow_dijkstra(source, sink)
        algo_name = "Алгоритм Диница"
    else:
        print("Неверный выбор, использую BFS")
        max_flow = network.max_flow_bfs(source, sink)
        algo_name = "BFS"
    
    print(f"\n{algo_name}: максимальный поток = {max_flow}")
    
    # Показываем потоки
    print("\nПотоки на ребрах:")
    for edge in network.edges:
        if edge.flow > 0 or edge.capacity > 0:
            print(f"  {edge.u} → {edge.v}: {edge.flow:.1f}/{edge.capacity:.1f}")
    
    # Визуализация
    visualize = input("\nВизуализировать сеть? (y/n): ").strip().lower()
    if visualize == 'y':
        network.visualize(f"Максимальный поток = {max_flow}")


if __name__ == "__main__":
    print("=== Алгоритм Форда-Фалкерсона для поиска максимального потока ===")
    
    # Демонстрация на классическом примере
    solve_max_flow_problem()
    
    # Демонстрация приложений
    solve_bipartite_matching()
    solve_transport_problem()
    
    # Бенчмарк алгоритмов
    benchmark_algorithms()
    
    # Интерактивный режим
    # interactive_solver()
    
    print("\n=== Завершено ===")