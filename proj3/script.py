#!/usr/bin/env python3

# Что-бы запустить переходим в папку с проектом и вводим "python script.py photos"

"""
Этот скрипт:
1) Получает путь к папке с изображениями (.jpg/.jpeg/.png)
2) Обрабатывает каждое изображение:
   - переводит в серый цвет
   - извлекает границы (Canny)
   - извлекает углы (Shi-Tomasi)
   - строит гистограмму яркости
3) Сохраняет обработанные изображения
4) Создаёт SQL файл с полной таблицей и INSERT строками

Особенность: OpenCV плохо читает русские пути, поэтому
используется imdecode + tofile, которые поддерживают Unicode.
"""

import os
import sys
import json
from pathlib import Path

import cv2
import numpy as np
import matplotlib.pyplot as plt


# Поддерживаемые расширения изображений
VALID_EXTS = {".jpg", ".jpeg", ".png"}


def sql_escape(value: str) -> str:
    """Экранирует одинарные кавычки, чтобы SQL не ломался."""
    return value.replace("'", "''")


# ------------------------------------------------------
#  ПОМОЩНИКИ ДЛЯ ЧТЕНИЯ/ЗАПИСИ КАРТИНОК С ЮНИКОД-ПУТЯМИ
# ------------------------------------------------------

def imread_unicode(path: Path):
    """
    Читает изображение через numpy + imdecode, что позволяет
    работать с русскими, арабскими, китайскими путями.
    """
    path_str = str(path)
    # Прочитать файл как байты
    data = np.fromfile(path_str, dtype=np.uint8)
    if data.size == 0:
        return None
    # Декодировать байты как изображение OpenCV
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    return img


def imwrite_unicode(path: Path, img) -> bool:
    """
    Сохраняет изображение, используя imencode (сжимает картинку в память)
    + tofile, что поддерживает Unicode пути.
    """
    ext = path.suffix  # например .png
    success, buf = cv2.imencode(ext, img)
    if not success:
        return False
    buf.tofile(str(path))  # запись на диск
    return True


# ------------------------------------------------------
#        ПОИСК ИЗОБРАЖЕНИЙ В ПАПКЕ
# ------------------------------------------------------

def find_images(input_dir: Path):
    """
    Рекурсивно ищет все изображения с нужными расширениями.
    """
    images = []
    for p in input_dir.rglob("*"):
        if p.is_file() and p.suffix.lower() in VALID_EXTS:
            images.append(p)
    return images


# ------------------------------------------------------
#                ОБРАБОТКА ОДНОГО ИЗОБРАЖЕНИЯ
# ------------------------------------------------------

def process_image(path: Path, output_dirs: dict, base_output_dir: Path):
    """
    Выполняет полную обработку изображения:
    1. Чтение безопасным способом
    2. Перевод в grayscale
    3. Детекция границ (Canny)
    4. Детекция углов (Shi-Tomasi)
    5. Рассчёт гистограммы
    6. Сохранение всех результатов
    """

    # Читаем картинку безопасно
    img = imread_unicode(path)
    if img is None:
        print(f"[WARN] Не удалось прочитать файл: {path}")
        return None

    # Перевод в оттенки серого
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Размер исходной картинки
    height, width = gray.shape[:2]

    # Алгоритм Canny находищает "границы" (контуры)
    edges = cv2.Canny(gray, 100, 200)

    # Поиск углов методом Shi-Tomasi
    corners = cv2.goodFeaturesToTrack(
        gray,
        maxCorners=200,      # максимум 200 углов
        qualityLevel=0.01,   # минимальное качество угла
        minDistance=10       # минимальное расстояние между углами
    )

    # Создаём копию изображения для рисования найденных углов
    corners_img = img.copy()

    # Если углы нашлись — рисуем точки
    if corners is not None:
        corners = np.intp(corners)  # преобразуем к целым координатам
        for c in corners:
            x, y = c.ravel()
            cv2.circle(corners_img, (x, y), 4, (0, 0, 255), 1, lineType=cv2.LINE_AA)

    # Вычисление гистограммы яркости (0–255)
    hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten()

    # Преобразуем в список и затем в JSON, чтобы вставить в SQL
    hist_list = [int(v) for v in hist]
    hist_json = json.dumps(hist_list)

    # Подготавливаем пути для сохранения
    base_name = path.stem
    gray_path = output_dirs["grayscale"] / f"{base_name}_gray.png"
    edges_path = output_dirs["edges"] / f"{base_name}_edges.png"
    corners_path = output_dirs["corners"] / f"{base_name}_corners.png"
    hist_img_path = output_dirs["histograms"] / f"{base_name}_hist.png"

    # Сохраняем через Unicode-friendly функцию
    imwrite_unicode(gray_path, gray)
    imwrite_unicode(edges_path, edges)
    imwrite_unicode(corners_path, corners_img)

    # Сохраняем гистограмму через matplotlib (он поддерживает Unicode)
    plt.figure()
    plt.plot(hist)
    plt.title(f"Histogram for {base_name}")
    plt.xlabel("Intensity")
    plt.ylabel("Pixel count")
    plt.xlim([0, 256])
    plt.tight_layout()
    plt.savefig(str(hist_img_path))
    plt.close()

    # Приводим пути к относительным для вставки в SQL
    orig_path_str = str(path.resolve())
    rel_gray = os.path.relpath(gray_path, base_output_dir).replace(os.sep, "/")
    rel_edges = os.path.relpath(edges_path, base_output_dir).replace(os.sep, "/")
    rel_corners = os.path.relpath(corners_path, base_output_dir).replace(os.sep, "/")
    rel_hist_img = os.path.relpath(hist_img_path, base_output_dir).replace(os.sep, "/")

    # Возвращаем словарь с данными для записи в SQL
    return {
        "image_path": orig_path_str,
        "width": width,
        "height": height,
        "hist_json": hist_json,
        "grayscale_path": rel_gray,
        "edges_path": rel_edges,
        "corners_path": rel_corners,
        "histogram_image_path": rel_hist_img,
    }


# ------------------------------------------------------
#                 ГЕНЕРАЦИЯ SQL ФАЙЛА
# ------------------------------------------------------

def generate_sql(records, sql_path: Path):
    """
    Создаёт SQL файл:
    - команда DROP TABLE
    - команда CREATE TABLE
    - INSERT строки для каждого изображения
    """

    lines = []

    lines.append("-- SQL script generated by image processing script")
    lines.append("")
    lines.append("DROP TABLE IF EXISTS image_features;")
    lines.append("")
    lines.append("CREATE TABLE image_features (")
    lines.append("    id INTEGER PRIMARY KEY AUTOINCREMENT,")
    lines.append("    image_path TEXT NOT NULL,")
    lines.append("    width INTEGER NOT NULL,")
    lines.append("    height INTEGER NOT NULL,")
    lines.append("    histogram TEXT NOT NULL,")
    lines.append("    grayscale_path TEXT NOT NULL,")
    lines.append("    edges_path TEXT NOT NULL,")
    lines.append("    corners_path TEXT NOT NULL,")
    lines.append("    histogram_image_path TEXT NOT NULL")
    lines.append(");")
    lines.append("")

    # Если нет записей — предупреждаем
    if not records:
        lines.append("-- WARNING: no images were processed, so there are no INSERT statements.")
    else:
        for rec in records:
            # Экранируем строки
            image_path = sql_escape(rec["image_path"])
            hist_json = sql_escape(rec["hist_json"])
            grayscale = sql_escape(rec["grayscale_path"])
            edges = sql_escape(rec["edges_path"])
            corners = sql_escape(rec["corners_path"])
            histimg = sql_escape(rec["histogram_image_path"])

            # Формируем INSERT
            line = (
                "INSERT INTO image_features "
                "(image_path, width, height, histogram, "
                "grayscale_path, edges_path, corners_path, histogram_image_path) "
                f"VALUES ('{image_path}', {rec['width']}, {rec['height']}, "
                f"'{hist_json}', '{grayscale}', '{edges}', '{corners}', '{histimg}');"
            )
            lines.append(line)

    # Записываем SQL-файл
    sql_path.write_text("\n".join(lines), encoding="utf-8")


# ------------------------------------------------------
#                     ОСНОВНАЯ ФУНКЦИЯ
# ------------------------------------------------------

def main():
    """
    Основная точка входа:
    - Проверяет аргументы
    - Создаёт папки output
    - Ищет изображения
    - Обрабатывает каждое
    - Создаёт SQL файл
    """

    # Проверка, что передан 1 аргумент — папка
    if len(sys.argv) != 2:
        print("Usage: python script.py /path/to/folder")
        sys.exit(1)

    # Приводим путь к нормальной форме
    input_dir = Path(sys.argv[1]).expanduser().resolve()

    # Проверка существования
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"[ERROR] Provided path is not a directory: {input_dir}")
        sys.exit(1)

    # Создаём папку output внутри входящей папки
    output_dir = input_dir / "output"
    output_dir.mkdir(exist_ok=True)

    # Подпапки для результатов
    grayscale_dir = output_dir / "grayscale"
    edges_dir = output_dir / "edges"
    corners_dir = output_dir / "corners"
    histograms_dir = output_dir / "histograms"

    # Создаём подпапки если их нет
    for d in (grayscale_dir, edges_dir, corners_dir, histograms_dir):
        d.mkdir(exist_ok=True)

    # Словарь путей — удобно передавать в функцию
    output_dirs = {
        "grayscale": grayscale_dir,
        "edges": edges_dir,
        "corners": corners_dir,
        "histograms": histograms_dir,
    }

    print(f"[INFO] Input folder:  {input_dir}")
    print(f"[INFO] Output folder: {output_dir}")

    # Ищем все изображения
    image_files = find_images(input_dir)
    print(f"[INFO] Найдено изображений: {len(image_files)}")
    for p in image_files:
        print(f"    [IMG] {p}")

    # Если нет — создаём SQL без вставок
    if not image_files:
        print("[WARN] Изображения не найдены!")
        sql_path = output_dir / "image_features.sql"
        generate_sql([], sql_path)
        print(f"[INFO] Пустой SQL файл сохранён в: {sql_path}")
        sys.exit(0)

    # Обрабатываем изображения
    records = []
    for img_path in image_files:
        print(f"[INFO] Обработка: {img_path}")
        rec = process_image(img_path, output_dirs, output_dir)
        if rec:
            records.append(rec)

    # Создаём SQL
    sql_path = output_dir / "image_features.sql"
    generate_sql(records, sql_path)

    print(f"[INFO] Готово. Обработано изображений: {len(records)}")
    print(f"[INFO] SQL файл сохранён в: {sql_path}")


# Точка входа
if __name__ == "__main__":
    main()
