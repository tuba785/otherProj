import os
import tkinter as tk
from tkinter import messagebox
from heapq import nsmallest

# Функция для вычисления расстояния Левенштейна
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1   # вставка
            deletions = current_row[j] + 1         # удаление
            substitutions = previous_row[j] + (c1 != c2)  # замена
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

# Загрузка слов из файла
def load_words(filename):
    with open(filename, encoding='utf-8') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

# Поиск 5 самых похожих слов по расстоянию Левенштейна
def find_similar(word, word_list, n=5):
    distances = [(levenshtein(word, w), w) for w in word_list]
    closest = nsmallest(n, distances, key=lambda x: x[0])
    return [w for dist, w in closest]

# Обработка события при нажатии кнопки
def on_search():
    query = entry.get().strip()
    if not query:
        messagebox.showinfo("Информация", "Введите название лекарства.")
        return

    if query in words:
        result_var.set(f"Лекарство найдено: {query}")
    else:
        similar = find_similar(query, words)
        result_var.set("Похожие лекарства:\n" + "\n".join(similar))

# Главная часть программы
# Определяем директорию, где находится этот скрипт
script_dir = os.path.dirname(os.path.abspath(__file__))
# Составляем полный путь к файлу lek.txt
file_path = os.path.join(script_dir, "lek.txt")

# Загружаем слова, используя полный путь
words = load_words(file_path)

root = tk.Tk()
root.title("Поиск лекарства")

tk.Label(root, text="Введите название лекарства:").pack(padx=10, pady=5)

entry = tk.Entry(root, width=40)
entry.pack(padx=10, pady=5)

btn_search = tk.Button(root, text="Поиск", command=on_search)
btn_search.pack(padx=10, pady=5)

result_var = tk.StringVar()
result_label = tk.Label(root, textvariable=result_var, justify="left")
result_label.pack(padx=10, pady=10)

root.mainloop()
