import tkinter as tk
from tkinter import ttk, messagebox


# ==============================
#   Структуры данных: BST
# ==============================

class TreeNode:
    """
    Класс узла двоичного дерева поиска (Binary Search Tree).
    Каждый узел хранит:
    - key: значение (целое число),
    - left: ссылка на левого потомка,
    - right: ссылка на правого потомка.
    """
    def __init__(self, key):
        self.key = key     # ключ (значение узла)
        self.left = None   # левый ребёнок
        self.right = None  # правый ребёнок


class BinarySearchTree:
    """
    Класс самого дерева BST.
    Содержит:
    - root: корень дерева,
    - методы для вставки, поиска, удаления и обходов.
    """
    def __init__(self):
        self.root = None  # изначально дерево пустое

    # ---------- ВСТАВКА ----------
    def insert(self, key):
        """
        Вставка нового ключа в BST.
        Если такой ключ уже есть, мы его не дублируем.
        """

        # Вспомогательная рекурсивная функция
        def _insert(node, key):
            # Если дошли до пустого места — создаём новый узел
            if node is None:
                return TreeNode(key)

            # Если новый ключ меньше текущего, идём влево
            if key < node.key:
                node.left = _insert(node.left, key)

            # Если новый ключ больше текущего, идём вправо
            elif key > node.key:
                node.right = _insert(node.right, key)

            # Если key == node.key, дублировать не будем — просто ничего не делаем
            return node

        # Запускаем вставку от корня
        self.root = _insert(self.root, key)

    # ---------- ПРОСТОЙ ПОИСК ----------
    def search(self, key):
        """
        Обычный поиск узла по ключу.
        Возвращает сам узел (TreeNode) или None, если не найден.
        """
        current = self.root  # начинаем с корня
        while current is not None:
            if key == current.key:
                # нашли ключ
                return current
            elif key < current.key:
                # если искомый ключ меньше — идём влево
                current = current.left
            else:
                # если больше — идём вправо
                current = current.right
        # если вышли из цикла, значит не нашли
        return None

    # ---------- ПОИСК С ПУТЁМ (для анимации и логов) ----------
    def search_with_path(self, key):
        """
        Поиск с сохранением пути (списка узлов, через которые мы прошли).
        Используется для:
        - анимации поиска,
        - логирования шагов внизу.
        """
        path = []           # сюда будем записывать каждый посещённый узел
        current = self.root
        while current is not None:
            path.append(current)  # добавляем текущий узел в путь

            if key == current.key:
                # нашли ключ — выходим
                break
            elif key < current.key:
                # идём влево
                current = current.left
            else:
                # идём вправо
                current = current.right

        # Возвращаем путь (даже если не нашли — путь до места, где поиск остановился)
        return path

    # ---------- УДАЛЕНИЕ ----------
    def delete(self, key):
        """
        Удаление узла по ключу из BST.
        Обрабатываем 3 случая:
        1) узел — лист,
        2) один ребёнок,
        3) два ребёнка (применяем стандартную замену на inorder-последователя).
        """

        # Вспомогательная рекурсивная функция удаления
        def _delete(node, key):
            # если узел пустой — возвращаем None
            if node is None:
                return None

            # Ищем узел для удаления
            if key < node.key:
                node.left = _delete(node.left, key)
            elif key > node.key:
                node.right = _delete(node.right, key)
            else:
                # Нашли узел для удаления

                # Случай 1: нет детей (лист)
                if node.left is None and node.right is None:
                    return None

                # Случай 2: только один ребёнок
                if node.left is None:
                    # только правый ребёнок
                    return node.right
                if node.right is None:
                    # только левый ребёнок
                    return node.left

                # Случай 3: два ребёнка
                # Ищем минимальный элемент в правом поддереве (inorder-последователь)
                min_larger_node = self._find_min(node.right)
                # Переписываем ключ на найденный
                node.key = min_larger_node.key
                # Удаляем узел с этим ключом в правом поддереве
                node.right = _delete(node.right, min_larger_node.key)

            # Возвращаем (возможно, изменённый) узел наверх
            return node

        # Запускаем удаление от корня
        self.root = _delete(self.root, key)

    def _find_min(self, node):
        """
        Находит узел с минимальным ключом в поддереве.
        Просто идём по левым ссылкам до конца.
        """
        current = node
        while current.left is not None:
            current = current.left
        return current

    # ---------- ОБХОДЫ ----------
    def inorder(self):
        """
        Симметричный обход (Inorder): Left - Root - Right.
        Возвращает список ключей.
        """
        result = []

        def _inorder(node):
            if node is None:
                return
            _inorder(node.left)
            result.append(node.key)
            _inorder(node.right)

        _inorder(self.root)
        return result

    def preorder(self):
        """
        Прямой обход (Preorder): Root - Left - Right.
        """
        result = []

        def _preorder(node):
            if node is None:
                return
            result.append(node.key)
            _preorder(node.left)
            _preorder(node.right)

        _preorder(self.root)
        return result

    def postorder(self):
        """
        Обратный обход (Postorder): Left - Right - Root.
        """
        result = []

        def _postorder(node):
            if node is None:
                return
            _postorder(node.left)
            _postorder(node.right)
            result.append(node.key)

        _postorder(self.root)
        return result

    # ---------- ВЫСОТА ДЕРЕВА ----------
    def height(self):
        """
        Возвращает высоту дерева, считая:
        - пустое дерево: -1,
        - дерево с одним узлом (только корень): 0.
        Высота нужна для аккуратной отрисовки уровней.
        """
        def _height(node):
            if node is None:
                return -1
            return 1 + max(_height(node.left), _height(node.right))

        return _height(self.root)


# ==============================
#   GUI: Визуализатор BST
# ==============================

class BSTVisualizer(tk.Tk):
    """
    Класс основного окна приложения.
    Наследуемся от tk.Tk, чтобы создать полноценное GUI-приложение.

    В этом классе:
    - создаём интерфейс (кнопки, поле ввода, холст, лог),
    - связываем кнопки с методами BST,
    - рисуем дерево,
    - делаем анимацию поиска.
    """
    def __init__(self):
        super().__init__()

        # Заголовок окна
        self.title("Binary Search Tree Visualizer")

        # Стартовый размер окна (можно менять вручную)
        self.geometry("900x600")

        # Само дерево BST
        self.bst = BinarySearchTree()

        # Ключ, который нужно подсветить на холсте
        self.highlight_key = None

        # Параметры для анимации поиска
        self.search_path_keys = None     # список ключей по пути поиска
        self.current_search_step = 0     # текущий шаг в анимации
        self.search_target_found = False # был ли ключ найден

        # Параметры для холста с деревом
        self.canvas_width = 850          # начальная ширина холста
        self.canvas_height = 400         # начальная высота холста
        self.node_radius = 18            # радиус кругов-узлов
        self.max_level_height = 80       # максимальное расстояние по вертикали между уровнями

        # Строим интерфейс
        self._build_ui()

    # ---------- Построение интерфейса ----------
    def _build_ui(self):
        """
        Создаёт все элементы интерфейса:
        - верхняя панель с кнопками и полем ввода,
        - холст для дерева,
        - нижний текстовый лог.
        """

        # ------ ВЕРХНЯЯ ПАНЕЛЬ (управление) ------
        control_frame = ttk.Frame(self)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Подпись "Key:"
        ttk.Label(control_frame, text="Key:").pack(side=tk.LEFT)

        # Поле для ввода ключа
        self.entry_key = ttk.Entry(control_frame, width=10)
        self.entry_key.pack(side=tk.LEFT, padx=5)

        # Кнопка вставки
        btn_insert = ttk.Button(control_frame, text="Insert", command=self.on_insert)
        btn_insert.pack(side=tk.LEFT, padx=5)

        # Кнопка удаления
        btn_delete = ttk.Button(control_frame, text="Delete", command=self.on_delete)
        btn_delete.pack(side=tk.LEFT, padx=5)

        # Кнопка поиска
        btn_search = ttk.Button(control_frame, text="Search", command=self.on_search)
        btn_search.pack(side=tk.LEFT, padx=5)

        # Кнопка показа обходов
        btn_traversals = ttk.Button(control_frame, text="Show Traversals", command=self.on_show_traversals)
        btn_traversals.pack(side=tk.LEFT, padx=5)

        # Кнопка очистки всего дерева
        btn_clear = ttk.Button(control_frame, text="Clear Tree", command=self.on_clear_tree)
        btn_clear.pack(side=tk.LEFT, padx=5)

        # Метка для краткого статуса (успех, ошибка и т.д.)
        self.status_label = ttk.Label(control_frame, text="Tree is empty.", foreground="gray")
        self.status_label.pack(side=tk.LEFT, padx=15)

        # ------ ХОЛСТ ДЛЯ ДЕРЕВА ------
        # Здесь рисуются круги (узлы) и линии (связи)
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white")
        self.canvas.pack(side=tk.TOP, padx=10, pady=10, fill=tk.BOTH, expand=True)

        # При изменении размера холста автоматически перерисовываем дерево
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # ------ НИЖНИЙ ЛОГ ------
        # Это обычная текстовая ячейка, не только для Traversals,
        # сюда мы выводим:
        # - шаги вставки,
        # - шаги удаления,
        # - шаги поиска,
        # - обходы дерева.

        traversals_frame = ttk.Frame(self, height=120)
        # Отключаем автоматическое подстраивание высоты под содержимое,
        # чтобы высота оставалась фиксированной
        traversals_frame.pack_propagate(False)
        traversals_frame.pack(side=tk.TOP, fill=tk.X, expand=False, padx=10, pady=(0, 10))

        # Подпись "Log:"
        ttk.Label(traversals_frame, text="Log:").pack(anchor=tk.W)

        # Само текстовое поле лога
        self.text_log = tk.Text(traversals_frame, height=5)
        self.text_log.pack(fill=tk.X, expand=False)

    # ---------- Вспомогательные методы для ввода и лога ----------
    def _get_key_from_entry(self):
        """
        Считывает значение из поля ввода и пытается привести его к int.
        Если поле пустое или это не число — показывает окно с ошибкой.
        """
        text = self.entry_key.get().strip()
        if not text:
            messagebox.showwarning("Input error", "Please enter a key (integer).")
            return None
        try:
            key = int(text)
            return key
        except ValueError:
            messagebox.showerror("Input error", f"'{text}' is not a valid integer.")
            return None

    def _log(self, lines):
        """
        Перезаписывает содержимое нижнего текстового поля.
        Если передана строка — выводим её.
        Если список строк — соединяем через перенос строки.
        """
        self.text_log.delete("1.0", tk.END)
        if isinstance(lines, str):
            self.text_log.insert(tk.END, lines)
        else:
            self.text_log.insert(tk.END, "\n".join(lines))

    def _describe_search_path(self, key, path_nodes, operation_name="search"):
        """
        Формирует текстовое описание шагов перемещения по дереву.

        Используется:
        - при вставке (поиск позиции для вставки),
        - при удалении (поиск узла для удаления),
        - при поиске (поиск ключа).

        Возвращает список строк (каждая строка — один шаг/комментарий).
        """
        lines = []

        if not path_nodes:
            lines.append("Дерево пустое, операция невозможна.")
            return lines

        lines.append(f"Операция: {operation_name}. Целевой ключ = {key}")

        # Перебираем узлы, через которые мы прошли
        for i, node in enumerate(path_nodes, start=1):
            if key == node.key:
                # Если ключ совпал — поиск останавливается
                lines.append(f"Шаг {i}: сравниваем с {node.key} — ключи равны, останавливаемся.")
            elif key < node.key:
                # Если искомый ключ меньше — идём влево
                lines.append(f"Шаг {i}: сравниваем с {node.key}: {key} < {node.key}, идём влево.")
            else:
                # Если больше — идём вправо
                lines.append(f"Шаг {i}: сравниваем с {node.key}: {key} > {node.key}, идём вправо.")

        # Итоговое описание результата
        if path_nodes[-1].key == key:
            lines.append(f"Результат поиска позиции: ключ {key} найден в узле {path_nodes[-1].key}.")
        else:
            lines.append(
                f"Результат поиска позиции: дошли до узла {path_nodes[-1].key}, "
                f"дальше ветви нет — ключ {key} отсутствует."
            )

        return lines

    # ---------- Обработчики кнопок: ВСТАВКА ----------
    def on_insert(self):
        """
        Обработчик нажатия кнопки Insert.
        1. Берём ключ из поля ввода.
        2. Логируем шаги, как мы ищем позицию для вставки.
        3. Вставляем ключ в дерево.
        4. Перерисовываем дерево.
        """
        key = self._get_key_from_entry()
        if key is None:
            return

        # Сбрасываем подсветку и анимацию, чтобы они не мешались
        self.highlight_key = None
        self.search_path_keys = None

        lines = []

        # Если дерево пустое — просто создаём корень
        if self.bst.root is None:
            self.bst.insert(key)
            self.status_label.config(text=f"Inserted key {key} as root.", foreground="green")
            lines.append(f"Вставка {key}: дерево было пустым, новый корень = {key}.")
        else:
            # Вставка не в пустое дерево:
            # сначала ищем позицию для вставки и логируем шаги
            path_nodes = self.bst.search_with_path(key)

            # Если последний узел в пути уже содержит этот ключ — дубликат
            if path_nodes and path_nodes[-1].key == key:
                self.status_label.config(text=f"Key {key} already exists. Duplicate ignored.", foreground="orange")
                lines = self._describe_search_path(key, path_nodes, operation_name="insert (поиск позиции)")
                lines.append("Вставка не выполняется, так как такой ключ уже существует.")
            else:
                # Ключ ещё не существует — покажем путь и объясним, где он будет вставлен
                parent = path_nodes[-1] if path_nodes else None
                lines = self._describe_search_path(key, path_nodes, operation_name="insert (поиск позиции)")
                if parent is not None:
                    if key < parent.key:
                        lines.append(
                            f"Так как {key} < {parent.key} и левый ребёнок пуст, "
                            f"вставляем {key} слева от {parent.key}."
                        )
                    else:
                        lines.append(
                            f"Так как {key} > {parent.key} и правый ребёнок пуст, "
                            f"вставляем {key} справа от {parent.key}."
                        )

                # Теперь реально вставляем ключ в дерево
                self.bst.insert(key)
                self.status_label.config(text=f"Inserted key {key}.", foreground="green")

        # Пишем все шаги в лог
        self._log(lines)
        # Перерисовываем дерево
        self.redraw_tree()

    # ---------- Обработчики кнопок: УДАЛЕНИЕ ----------
    def on_delete(self):
        """
        Обработчик кнопки Delete.
        1. Берём ключ.
        2. Находим узел, логируем путь.
        3. Объясняем, как "восполняется" место удалённого узла.
        4. Удаляем и перерисовываем.
        """
        key = self._get_key_from_entry()
        if key is None:
            return

        # Сброс подсветки и анимации
        self.highlight_key = None
        self.search_path_keys = None

        lines = []

        # Если дерево пустое — удалять нечего
        if self.bst.root is None:
            self.status_label.config(text="Tree is empty. Nothing to delete.", foreground="red")
            lines.append("Удаление невозможно: дерево пустое.")
            self._log(lines)
            self.redraw_tree()
            return

        # Ищем путь до ключа
        path_nodes = self.bst.search_with_path(key)

        # Если путь пуст или последний узел в пути не содержит ключ — его нет в дереве
        if not path_nodes or path_nodes[-1].key != key:
            self.status_label.config(text=f"Key {key} not found. Nothing to delete.", foreground="red")
            lines = self._describe_search_path(key, path_nodes, operation_name="delete (поиск удаляемого)")
            self._log(lines)
            self.redraw_tree()
            return

        # Узел, который будем удалять
        node = path_nodes[-1]
        lines = self._describe_search_path(key, path_nodes, operation_name="delete (поиск удаляемого)")

        # Смотрим, есть ли у него дети
        has_left = node.left is not None
        has_right = node.right is not None

        # Объясняем, что произойдёт при удалении (восполнение места)
        if not has_left and not has_right:
            # Лист
            lines.append(
                f"Узел {node.key} — лист. Просто удаляем его, ссылка родителя на этот узел станет пустой."
            )
        elif has_left and not has_right:
            # Только левый ребёнок
            lines.append(
                f"У узла {node.key} есть только левый ребёнок {node.left.key}. "
                f"Родитель начнёт ссылаться напрямую на {node.left.key} вместо {node.key}."
            )
        elif not has_left and has_right:
            # Только правый ребёнок
            lines.append(
                f"У узла {node.key} есть только правый ребёнок {node.right.key}. "
                f"Родитель начнёт ссылаться напрямую на {node.right.key} вместо {node.key}."
            )
        else:
            # Два ребёнка
            succ = node.right
            while succ.left is not None:
                succ = succ.left
            lines.append(
                f"У узла {node.key} два ребёнка ({node.left.key} и {node.right.key}). "
                f"Ищем inorder-последователя — минимальный элемент в правом поддереве: {succ.key}."
            )
            lines.append(
                f"Заменяем ключ {node.key} на {succ.key}, затем рекурсивно удаляем узел {succ.key} "
                f"в правом поддереве. Так «восполняется» место удалённого узла, "
                f"и свойство BST сохраняется."
            )

        # Реально удаляем ключ из дерева
        self.bst.delete(key)
        self.status_label.config(text=f"Deleted key {key}.", foreground="green")

        # Логируем объяснение
        self._log(lines)
        # Перерисовываем дерево
        self.redraw_tree()

    # ---------- Обработчики кнопок: ПОИСК ----------
    def on_search(self):
        """
        Обработчик кнопки Search.
        1. Берём ключ.
        2. С помощью search_with_path получаем путь.
        3. Логируем шаги (сравнение, переход влево/вправо).
        4. Запускаем анимацию подсветки пути.
        """
        key = self._get_key_from_entry()
        if key is None:
            return

        path_nodes = self.bst.search_with_path(key)

        # Если путь пуст — дерево пустое
        if not path_nodes:
            self.highlight_key = None
            self.search_path_keys = None
            self.status_label.config(text="Tree is empty. Nothing to search.", foreground="red")
            self._log(["Поиск невозможен: дерево пустое."])
            self.redraw_tree()
            return

        # Для анимации сохраняем список ключей по пути
        self.search_path_keys = [node.key for node in path_nodes]
        self.current_search_step = 0
        self.search_target_found = (path_nodes[-1].key == key)

        # Обновляем статус
        if self.search_target_found:
            self.status_label.config(
                text=f"Searching for {key}: {len(self.search_path_keys)} step(s). Target found.",
                foreground="blue"
            )
        else:
            self.status_label.config(
                text=f"Searching for {key}: {len(self.search_path_keys)} step(s). Target NOT found.",
                foreground="red"
            )

        # Описание шагов поиска для лога
        lines = self._describe_search_path(key, path_nodes, operation_name="search")
        self._log(lines)

        # Запускаем анимацию поиска
        self._animate_search_step()

    def _animate_search_step(self):
        """
        Реализует анимацию поиска:
        - по одному шагу подсвечивает каждый узел на пути,
        - между шагами делаем задержку через self.after(),
        - в конце либо оставляем подсвеченным найденный узел,
          либо убираем подсветку, если ключ не найден.
        """
        if self.search_path_keys is None:
            # Нет активной анимации
            return

        if self.current_search_step < len(self.search_path_keys):
            # Подсвечиваем очередной узел
            self.highlight_key = self.search_path_keys[self.current_search_step]
            self.redraw_tree()

            # Переходим к следующему шагу
            self.current_search_step += 1

            # Задержка 500 мс перед следующей подсветкой
            self.after(500, self._animate_search_step)
        else:
            # Анимация закончилась
            if self.search_target_found:
                # Если ключ был найден, оставляем подсветку на последнем узле пути
                self.highlight_key = self.search_path_keys[-1]
            else:
                # Если не найден — убираем подсветку
                self.highlight_key = None

            # Перерисовываем дерево, чтобы обновить подсветку
            self.redraw_tree()

            # Сбрасываем информацию об анимации
            self.search_path_keys = None

    # ---------- Обработчики кнопок: ОБХОДЫ ----------
    def on_show_traversals(self):
        """
        Обработчик кнопки Show Traversals.
        Просто выводим в лог три обхода:
        - Inorder,
        - Preorder,
        - Postorder.
        """
        inorder = self.bst.inorder()
        preorder = self.bst.preorder()
        postorder = self.bst.postorder()

        lines = [
            "Обходы дерева:",
            "Inorder (LNR):   " + " ".join(map(str, inorder)),
            "Preorder (NLR):  " + " ".join(map(str, preorder)),
            "Postorder (LRN): " + " ".join(map(str, postorder)),
        ]
        self._log(lines)

    # ---------- Обработчики кнопок: ОЧИСТКА ----------
    def on_clear_tree(self):
        """
        Обработчик кнопки Clear Tree.
        Полностью очищает дерево, холст и лог.
        """
        self.bst = BinarySearchTree()   # создаём новое пустое дерево
        self.highlight_key = None
        self.search_path_keys = None
        self.canvas.delete("all")       # очищаем рисунок
        self.text_log.delete("1.0", tk.END)  # очищаем лог
        self.status_label.config(text="Tree is empty.", foreground="gray")

    # ---------- Обработка изменения размера холста ----------
    def on_canvas_resize(self, event):
        """
        Срабатывает, когда пользователь меняет размер окна,
        и, соответственно, меняется размер холста.
        Мы сохраняем новые размеры и перерисовываем дерево,
        чтобы оно красиво растягивалось.
        """
        self.canvas_width = event.width
        self.canvas_height = event.height
        self.redraw_tree()

    # ---------- ОТРИСОВКА ДЕРЕВА ----------
    def redraw_tree(self):
        """
        Основной метод отрисовки дерева на холсте.
        1. Очищаем холст.
        2. Если дерево пустое — пишем текст.
        3. Иначе рассчитываем координаты узлов и рисуем их.
        """
        # Сначала очищаем всё
        self.canvas.delete("all")

        # Если дерево пустое — просто показываем надпись
        if self.bst.root is None:
            self.canvas.create_text(
                self.canvas_width // 2,
                self.canvas_height // 2,
                text="Tree is empty.",
                fill="gray",
                font=("Arial", 16)
            )
            return

        # Получаем высоту дерева (сколько уровней)
        tree_height = self.bst.height()  # 0, 1, 2, ...

        # Рассчитываем расстояние между уровнями (по вертикали)
        if tree_height <= 0:
            # Дерево из одного узла или что-то очень маленькое
            level_height = 0
        else:
            # Полезная высота: высота холста минус небольшие отступы
            usable_height = max(80, self.canvas_height - 80)
            # Выбираем минимальное из:
            #   - максимальное расстояние между уровнями (max_level_height),
            #   - равномерное распределение по высоте холста
            level_height = min(self.max_level_height, usable_height / tree_height)

        # Словарь: узел -> (x, y), где будем рисовать
        positions = {}

        # Сначала вычисляем координаты всех узлов
        self._compute_positions(
            node=self.bst.root,
            depth=0,
            x_min=0,
            x_max=self.canvas_width,
            level_height=level_height,
            positions=positions
        )

        # Затем рисуем линии (рёбра) между узлами
        self._draw_edges(self.bst.root, positions)

        # И после этого рисуем сами узлы (круги + текст)
        self._draw_nodes(self.bst.root, positions)

    def _compute_positions(self, node, depth, x_min, x_max, level_height, positions):
        """
        Рекурсивно вычисляет координаты (x, y) для каждого узла дерева.

        Идея:
        - x = середина интервала [x_min, x_max],
        - y = отступ сверху + depth * level_height,
        где depth — глубина узла (0 для корня, 1 для его детей и т.д.).
        """
        if node is None:
            return

        # x — середина доступного интервала по горизонтали
        x = (x_min + x_max) // 2

        # Если высота между уровнями 0 — ставим дерево примерно по центру
        if level_height == 0:
            y = self.canvas_height // 2
        else:
            # Иначе отступ сверху 40 пикселей + depth * level_height
            y = 40 + int(depth * level_height)

        # Запоминаем координаты для этого узла
        positions[node] = (x, y)

        # Левое поддерево получает левую часть интервала [x_min, x)
        self._compute_positions(node.left, depth + 1, x_min, x, level_height, positions)
        # Правое поддерево получает правую часть интервала (x, x_max]
        self._compute_positions(node.right, depth + 1, x, x_max, level_height, positions)

    def _draw_edges(self, node, positions):
        """
        Рисует линии (рёбра) между узлом и его детьми.
        """
        if node is None:
            return

        x, y = positions[node]

        # Если есть левый ребёнок — соединяем линией
        if node.left is not None:
            x_left, y_left = positions[node.left]
            self.canvas.create_line(x, y, x_left, y_left)
            self._draw_edges(node.left, positions)

        # Если есть правый ребёнок — соединяем линией
        if node.right is not None:
            x_right, y_right = positions[node.right]
            self.canvas.create_line(x, y, x_right, y_right)
            self._draw_edges(node.right, positions)

    def _draw_nodes(self, node, positions):
        """
        Рисует сами узлы:
        - круг,
        - текст внутри (ключ),
        - подсветку, если этот узел сейчас выделен (поиск).
        """
        if node is None:
            return

        x, y = positions[node]
        r = self.node_radius

        # Определяем цвета в зависимости от того, подсвечен узел или нет
        if self.highlight_key is not None and node.key == self.highlight_key:
            # Узел подсвечен (например, в ходе поиска)
            fill_color = "yellow"
            outline_color = "red"
            text_color = "black"
        else:
            # Обычный узел
            fill_color = "lightblue"
            outline_color = "black"
            text_color = "black"

        # Рисуем круг (овал) — сам узел
        self.canvas.create_oval(
            x - r, y - r,
            x + r, y + r,
            fill=fill_color,
            outline=outline_color,
            width=2
        )

        # Рисуем текст (ключ) в центре круга
        self.canvas.create_text(
            x, y,
            text=str(node.key),
            font=("Arial", 10),
            fill=text_color
        )

        # Рекурсивно рисуем левое и правое поддерево
        self._draw_nodes(node.left, positions)
        self._draw_nodes(node.right, positions)


# ==============================
#   Точка входа
# ==============================

if __name__ == "__main__":
    # Если файл запускается напрямую (а не импортируется),
    # создаём объект приложения и запускаем главный цикл Tkinter.
    app = BSTVisualizer()
    app.mainloop()
