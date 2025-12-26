from graphviz import Digraph
from dataclasses import dataclass, field
from typing import Optional, Set

@dataclass
class State:
    """Состояние NFA"""
    id: int
    is_final: bool = False
    transitions: dict = field(default_factory=dict)  # char -> Set[State]
    epsilon_transitions: Set['State'] = field(default_factory=set)

@dataclass
class NFA:
    """Недетерминированный конечный автомат"""
    start: State
    accept: State
    
    @classmethod
    def from_character(cls, c: str) -> 'NFA':
        """Базовый случай: один символ"""
        start = State(id=0)
        accept = State(id=1, is_final=True)
        
        if c == 'ε':
            start.epsilon_transitions.add(accept)
        else:
            start.transitions.setdefault(c, set()).add(accept)
            
        return cls(start, accept)
    
    @classmethod
    def union(cls, nfa1: 'NFA', nfa2: 'NFA') -> 'NFA':
        """Объединение (a|b)"""
        start = State(id=-1)  # Временный ID
        accept = State(id=-2, is_final=True)
        
        # Старые принимающие состояния больше не принимающие
        nfa1.accept.is_final = False
        nfa2.accept.is_final = False
        
        # ε-переходы из нового старта
        start.epsilon_transitions.add(nfa1.start)
        start.epsilon_transitions.add(nfa2.start)
        
        # ε-переходы в новое принимающее состояние
        nfa1.accept.epsilon_transitions.add(accept)
        nfa2.accept.epsilon_transitions.add(accept)
        
        return cls(start, accept)
    
    @classmethod
    def concatenate(cls, nfa1: 'NFA', nfa2: 'NFA') -> 'NFA':
        """Конкатенация (ab)"""
        # Соединяем принимающее состояние первого с начальным второго
        nfa1.accept.epsilon_transitions.add(nfa2.start)
        nfa1.accept.is_final = False
        
        return cls(nfa1.start, nfa2.accept)
    
    @classmethod
    def kleene_star(cls, nfa: 'NFA') -> 'NFA':
        """Звезда Клини (a*)"""
        start = State(id=-1)
        accept = State(id=-2, is_final=True)
        
        nfa.accept.is_final = False
        
        # ε-переходы для звезды
        start.epsilon_transitions.add(nfa.start)  # Вход в выражение
        start.epsilon_transitions.add(accept)     # Пропуск (0 повторений)
        
        nfa.accept.epsilon_transitions.add(nfa.start)  # Петля
        nfa.accept.epsilon_transitions.add(accept)     # Выход
        
        return cls(start, accept)
    
    def visualize(self, filename='nfa'):
        """Визуализация NFA через Graphviz"""
        dot = Digraph(comment='NFA from Thompson Construction')
        dot.attr(rankdir='LR')
        
        # Собираем все состояния
        visited = set()
        stack = [self.start]
        state_counter = 0
        
        while stack:
            state = stack.pop()
            if state in visited:
                continue
            visited.add(state)
            
            # Присваиваем уникальные ID для отображения
            if not hasattr(state, 'display_id'):
                state.display_id = state_counter
                state_counter += 1
            
            # Форма узла
            shape = 'doublecircle' if state.is_final else 'circle'
            if state == self.start:
                # Добавляем невидимый узел для стрелки к старту
                dot.node(f'start_{state.display_id}', '', shape='none', width='0', height='0')
                dot.edge(f'start_{state.display_id}', f's{state.display_id}')
            
            dot.node(f's{state.display_id}', str(state.display_id), shape=shape)
            
            # Обычные переходы
            for char, targets in state.transitions.items():
                for target in targets:
                    if not hasattr(target, 'display_id'):
                        target.display_id = state_counter
                        state_counter += 1
                    dot.edge(f's{state.display_id}', f's{target.display_id}', label=char)
                    stack.append(target)
            
            # ε-переходы
            for target in state.epsilon_transitions:
                if not hasattr(target, 'display_id'):
                    target.display_id = state_counter
                    state_counter += 1
                dot.edge(f's{state.display_id}', f's{target.display_id}', label='ε', style='dashed')
                stack.append(target)
        
        dot.render(filename, view=True, format='png')
        print(f"NFA сохранен в {filename}.png")
        return dot

def regex_to_nfa_thompson(regex: str) -> NFA:
    """
    Преобразует регулярное выражение в NFA.
    Поддерживает: символы, конкатенацию, |, *
    Приоритет операций: * > конкатенация > |
    """
    
    def parse_expression(tokens, idx):
        """Парсит выражение без |"""
        nfa = None
        
        while idx < len(tokens) and tokens[idx] != ')' and tokens[idx] != '|':
            token = tokens[idx]
            
            if token == '(':
                # Рекурсивный парсинг подвыражения
                sub_nfa, idx = parse_expression(tokens, idx + 1)
                idx += 1  # Пропускаем ')'
            elif token == '*':
                # Применяем звезду Клини к предыдущему NFA
                nfa = NFA.kleene_star(nfa)
                idx += 1
                continue
            else:
                # Базовый символ
                sub_nfa = NFA.from_character(token)
                idx += 1
            
            # Конкатенация
            if nfa is None:
                nfa = sub_nfa
            else:
                nfa = NFA.concatenate(nfa, sub_nfa)
        
        return nfa, idx
    
    def parse_or(tokens, idx=0):
        """Парсит выражение с |"""
        nfas = []
        
        while idx < len(tokens):
            if tokens[idx] == '|':
                idx += 1
                continue
            
            nfa, idx = parse_expression(tokens, idx)
            nfas.append(nfa)
            
            if idx < len(tokens) and tokens[idx] == '|':
                idx += 1
        
        # Объединяем все NFA через |
        if len(nfas) == 1:
            return nfas[0]
        
        result = nfas[0]
        for nfa in nfas[1:]:
            result = NFA.union(result, nfa)
        
        return result
    
    # Токенизация регулярного выражения
    tokens = []
    i = 0
    while i < len(regex):
        c = regex[i]
        
        if c in '()|*':
            tokens.append(c)
            i += 1
        elif c == '\\':  # Экранирование
            if i + 1 < len(regex):
                tokens.append(regex[i + 1])
                i += 2
        else:
            # Обработка конкатенации: между символами и '('
            if tokens and tokens[-1] not in '(|':
                # Неявная конкатенация
                tokens.append('.')
            tokens.append(c)
            i += 1
    
    # Заменяем '.' на явную конкатенацию
    new_tokens = []
    for i, token in enumerate(tokens):
        if token == '.':
            continue
        if i > 0 and token not in ')|*' and tokens[i-1] not in '(|.':
            new_tokens.append('.')
        new_tokens.append(token)
    
    print(f"Токены: {new_tokens}")
    return parse_or(new_tokens)

# ================== ПРИМЕР ИСПОЛЬЗОВАНИЯ ==================

if __name__ == "__main__":
    # Пример 1: Простое выражение (a|b)*a
    print("Пример 1: (a|b)*a")
    regex = "(a|b)*a"
    nfa = regex_to_nfa_thompson(regex)
    
    # Переименуем состояния для красоты
    def rename_states(state, counter, visited):
        if state in visited:
            return counter
        visited.add(state)
        state.id = counter
        counter += 1
        
        for targets in state.transitions.values():
            for target in targets:
                counter = rename_states(target, counter, visited)
        
        for target in state.epsilon_transitions:
            counter = rename_states(target, counter, visited)
        
        return counter
    
    rename_states(nfa.start, 0, set())
    
    # Визуализация
    nfa.visualize("thompson_nfa")
    
    # Пример 2: Более сложное выражение
    print("\nПример 2: (ab|c)*d")
    regex2 = "(ab|c)*d"
    nfa2 = regex_to_nfa_thompson(regex2)
    rename_states(nfa2.start, 0, set())
    nfa2.visualize("thompson_nfa2")
    
    # Проверка работы NFA (упрощенный эмулятор)
    def simulate_nfa(nfa, input_string):
        """Эмуляция NFA через ε-замыкание"""
        def epsilon_closure(states):
            closure = set(states)
            stack = list(states)
            
            while stack:
                state = stack.pop()
                for next_state in state.epsilon_transitions:
                    if next_state not in closure:
                        closure.add(next_state)
                        stack.append(next_state)
            
            return closure
        
        current_states = epsilon_closure({nfa.start})
        
        for char in input_string:
            next_states = set()
            for state in current_states:
                if char in state.transitions:
                    next_states.update(state.transitions[char])
            
            current_states = epsilon_closure(next_states)
            if not current_states:
                return False
        
        return any(state.is_final for state in current_states)
    
    # Тестирование
    test_cases = ["a", "ba", "aba", "bbbba", "b", "ab"]
    print("\nТестирование NFA для (a|b)*a:")
    for test in test_cases:
        result = simulate_nfa(nfa, test)
        print(f"  '{test}': {'Принято' if result else 'Отклонено'}")