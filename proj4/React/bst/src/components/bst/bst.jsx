// ======================================================================
//  Полный визуализатор Binary Search Tree (BST) с анимацией поиска,
//  вставкой, удалением и детальной текстовой инфопанелью.
//
//  ВСЕГО В КОДЕ ОЧЕНЬ МНОГО КОММЕНТАРИЕВ, чтобы начинающий человек
//  смог спокойно разобраться в структурах, компонентах, состоянии React,
//  алгоритмах и принципах визуализации.
// ======================================================================

import React, { useState, useEffect } from "react";
import "./bst.css";

// ======================================================================
//                     БАЗОВЫЕ СТРУКТУРЫ ДАННЫХ BST
// ======================================================================

// Для того, чтобы каждому узлу дерева в интерфейсе выдавать уникальный ID,
// будем просто увеличивать счётчик.
let nodeIdCounter = 0;

// Функция создания нового узла
function createNode(key) {
  return {
    id: ++nodeIdCounter, // уникальный id для React-анимаций
    key, // значение узла
    left: null,
    right: null,
  };
}

// ======================================================================
//                        ВСТАВКА В ДЕРЕВО (Insert)
// ======================================================================

// Эта функция вставляет значение в BST иммутабельно (не мутирует объект).
// Это важно, потому что React должен видеть изменение и перерисовывать дерево.
function insertNode(node, key) {
  if (node === null) return createNode(key); // создаём новый узел

  // Стандартная логика вставки в BST:
  // если ключ меньше – идём влево, больше – вправо
  if (key < node.key) return { ...node, left: insertNode(node.left, key) };
  if (key > node.key) return { ...node, right: insertNode(node.right, key) };

  return node; // дубликаты игнорируются
}

// ======================================================================
//                        УДАЛЕНИЕ ИЗ ДЕРЕВА (Delete)
// ======================================================================

// Находим минимальный узел в правом поддереве – inorder-последователь
function findMin(node) {
  while (node.left) node = node.left;
  return node;
}

// Иммутабельное удаление узла
function deleteNode(node, key) {
  if (node === null) return null;

  if (key < node.key) {
    return { ...node, left: deleteNode(node.left, key) };
  }
  if (key > node.key) {
    return { ...node, right: deleteNode(node.right, key) };
  }

  // ====== здесь ключ найден ======
  // 1. Нет детей — просто удаляем
  if (!node.left && !node.right) return null;

  // 2. Один ребёнок
  if (!node.left) return node.right;
  if (!node.right) return node.left;

  // 3. Два ребёнка — ищем inorder successor
  const succ = findMin(node.right);
  const newRight = deleteNode(node.right, succ.key);

  return { ...node, key: succ.key, right: newRight };
}

// ======================================================================
//                   ПОИСК С ВОЗВРАТОМ ПУТИ (Search Path)
// ======================================================================

// Возвращает массив узлов, по которым прошёл поиск.
// Path = [root, next, next, ..., last]
function searchPath(node, key) {
  const path = [];
  let cur = node;

  while (cur) {
    path.push(cur);
    if (key === cur.key) break;
    if (key < cur.key) cur = cur.left;
    else cur = cur.right;
  }

  return path;
}

// ======================================================================
//                       ОБХОДЫ ДЕРЕВА (Traversals)
// ======================================================================

function inorder(node, acc = []) {
  if (!node) return acc;
  inorder(node.left, acc);
  acc.push(node.key);
  inorder(node.right, acc);
  return acc;
}

function preorder(node, acc = []) {
  if (!node) return acc;
  acc.push(node.key);
  preorder(node.left, acc);
  preorder(node.right, acc);
  return acc;
}

function postorder(node, acc = []) {
  if (!node) return acc;
  postorder(node.left, acc);
  postorder(node.right, acc);
  acc.push(node.key);
  return acc;
}

// Высота дерева (нужна для вертикального распределения узлов)
function height(node) {
  if (!node) return -1;
  return 1 + Math.max(height(node.left), height(node.right));
}

// ======================================================================
//           ВЫЧИСЛЕНИЕ КООРДИНАТ УЗЛОВ ДЛЯ SVG-ВИЗУАЛИЗАЦИИ
// ======================================================================

// Эта функция возвращает:
// nodes = [{id, key, x, y, node}, ...]
// edges = [{from, to, x1, y1, x2, y2}, ...]
function computePositions(root, width, heightPx) {
  if (!root) return { nodes: [], edges: [] };

  const positions = new Map();
  const edges = [];

  const h = height(root);
  const usableHeight = Math.max(120, heightPx - 80);
  const levelHeight = Math.min(120, usableHeight / Math.max(1, h || 1));

  // DFS обход
  function dfs(node, depth, xMin, xMax) {
    if (!node) return null;

    // середина промежутка
    const x = (xMin + xMax) / 2;
    const y = 40 + depth * levelHeight;

    positions.set(node.id, { x, y, key: node.key, node });

    // левый ребёнок
    if (node.left) {
      const child = dfs(node.left, depth + 1, xMin, x);
      edges.push({
        from: node.id,
        to: node.left.id,
        x1: x,
        y1: y,
        x2: child.x,
        y2: child.y,
      });
    }

    // правый ребёнок
    if (node.right) {
      const child = dfs(node.right, depth + 1, x, xMax);
      edges.push({
        from: node.id,
        to: node.right.id,
        x1: x,
        y1: y,
        x2: child.x,
        y2: child.y,
      });
    }

    return { x, y };
  }

  dfs(root, 0, 40, width - 40);

  const nodes = Array.from(positions.entries()).map(([id, pos]) => ({
    id,
    x: pos.x,
    y: pos.y,
    key: pos.key,
    node: pos.node,
  }));

  return { nodes, edges };
}

// ======================================================================
//                     ГЛАВНЫЙ КОМПОНЕНТ: BSTVisualizer
// ======================================================================

export default function BSTVisualizer() {
  // ------------------ состояние дерева ------------------
  const [root, setRoot] = useState(null); // само дерево
  const [inputValue, setInputValue] = useState(""); // значение input
  const [infoText, setInfoText] = useState(
    "Дерево пустое. Добавьте первый элемент."
  );
  const [highlightKey, setHighlightKey] = useState(null); // какой узел подсвечивается

  // ------------------ состояние анимации поиска ------------------
  const [searchPathKeys, setSearchPathKeys] = useState(null);
  const [searchStep, setSearchStep] = useState(0);
  const [searchFound, setSearchFound] = useState(false);
  const [searchTarget, setSearchTarget] = useState(null);
  const [isAnimatingSearch, setIsAnimatingSearch] = useState(false);

  // размеры SVG-холста под fullscreen
  const width = 1300;
  const heightPx = 500;

  // вычисляем позиции узлов для отрисовки
  const { nodes, edges } = computePositions(root, width, heightPx);

  // ======================================================================
  //                          АНИМАЦИЯ ПОИСКА
  // ======================================================================

  useEffect(() => {
    if (!isAnimatingSearch || !searchPathKeys) return;

    if (searchStep >= searchPathKeys.length) {
      if (searchFound) setHighlightKey(searchTarget);
      else setHighlightKey(null);

      setIsAnimatingSearch(false);
      return;
    }

    // подсвечиваем очередной узел
    setHighlightKey(searchPathKeys[searchStep]);

    const timer = setTimeout(() => {
      setSearchStep((s) => s + 1);
    }, 550);

    return () => clearTimeout(timer);
  }, [
    isAnimatingSearch,
    searchPathKeys,
    searchStep,
    searchFound,
    searchTarget,
  ]);

  // ======================================================================
  //        ФУНКЦИЯ: описание пути поиска (вставка, удаление, поиск)
  // ======================================================================

  function describeSearchPath(key, path, opName = "search") {
    if (!path.length) return ["Дерево пустое, операция невозможна."];

    const lines = [`Операция: ${opName}. Целевой ключ = ${key}`];

    path.forEach((node, i) => {
      const step = i + 1;

      if (key === node.key)
        lines.push(
          `Шаг ${step}: сравниваем с ${node.key} — ключи равны, останавливаемся.`
        );
      else if (key < node.key)
        lines.push(
          `Шаг ${step}: сравниваем с ${node.key}: ${key} < ${node.key}, идём влево.`
        );
      else
        lines.push(
          `Шаг ${step}: сравниваем с ${node.key}: ${key} > ${node.key}, идём вправо.`
        );
    });

    const last = path[path.length - 1];
    if (last.key === key) lines.push(`Результат: ключ ${key} найден.`);
    else
      lines.push(
        `Результат: дошли до ${last.key}, дальше пути нет, ключ отсутствует.`
      );

    return lines;
  }

  // ======================================================================
  //                       ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
  // ======================================================================

  function parseKey() {
    const t = inputValue.trim();
    if (!t) {
      setInfoText("Введите целое число в поле KEY.");
      return null;
    }
    const n = Number(t);
    if (!Number.isInteger(n)) {
      setInfoText(`'${t}' не является целым числом`);
      return null;
    }
    return n;
  }

  // ======================================================================
  //                                INSERT
  // ======================================================================

  function handleInsert() {
    const key = parseKey();
    if (key === null) return;

    setIsAnimatingSearch(false);
    setHighlightKey(null);
    setSearchPathKeys(null);

    if (!root) {
      setRoot(createNode(key));
      setInfoText(`Вставка ${key}: дерево было пустым, новый корень = ${key}.`);
      return;
    }

    const path = searchPath(root, key);

    if (path[path.length - 1].key === key) {
      const lines = describeSearchPath(key, path, "insert");
      lines.push("Вставка отменена: такой ключ уже существует.");
      setInfoText(lines.join("\n"));
      return;
    }

    const parent = path[path.length - 1];
    const lines = describeSearchPath(key, path, "insert");

    if (key < parent.key)
      lines.push(`Ключ ${key} < ${parent.key}: вставляем слева.`);
    else lines.push(`Ключ ${key} > ${parent.key}: вставляем справа.`);

    setRoot(insertNode(root, key));
    setInfoText(lines.join("\n"));
  }

  // ======================================================================
  //                                DELETE
  // ======================================================================

  function handleDelete() {
    const key = parseKey();
    if (key === null) return;

    setIsAnimatingSearch(false);
    setHighlightKey(null);
    setSearchPathKeys(null);

    if (!root) {
      setInfoText("Удаление невозможно: дерево пустое.");
      return;
    }

    const path = searchPath(root, key);

    if (path[path.length - 1].key !== key) {
      const lines = describeSearchPath(key, path, "delete");
      setInfoText(lines.join("\n"));
      return;
    }

    const node = path[path.length - 1];
    const lines = describeSearchPath(key, path, "delete");

    if (!node.left && !node.right) lines.push("Узел — лист. Просто удаляем.");
    else if (node.left && !node.right)
      lines.push("Узел имеет только ЛЕВОГО ребёнка. Поднимаем его вверх.");
    else if (!node.left && node.right)
      lines.push("Узел имеет только ПРАВОГО ребёнка. Поднимаем его вверх.");
    else {
      let succ = node.right;
      while (succ.left) succ = succ.left;
      lines.push(
        `Узел имеет ДВА ребёнка. Ищем inorder-последователя: ${succ.key}.`
      );
      lines.push("Заменяем значение, затем удаляем последователь.");
    }

    setRoot(deleteNode(root, key));
    setInfoText(lines.join("\n"));
  }

  // ======================================================================
  //                                SEARCH
  // ======================================================================

  function handleSearch() {
    const key = parseKey();
    if (key === null) return;

    if (!root) {
      setInfoText("Дерево пустое: поиск невозможен.");
      setHighlightKey(null);
      return;
    }

    const path = searchPath(root, key);
    const lines = describeSearchPath(key, path, "search");
    setInfoText(lines.join("\n"));

    const keysPath = path.map((n) => n.key);
    setSearchPathKeys(keysPath);
    setSearchStep(0);
    setSearchFound(path[path.length - 1].key === key);
    setSearchTarget(key);
    setIsAnimatingSearch(true);
  }

  // ======================================================================
  //                        ПОКАЗАТЬ ОБХОДЫ ДЕРЕВА
  // ======================================================================

  function handleShowTraversals() {
    const lines = [
      "Обходы дерева:",
      `Inorder  (LNR): ${inorder(root).join(" ")}`,
      `Preorder (NLR): ${preorder(root).join(" ")}`,
      `Postord (LRN): ${postorder(root).join(" ")}`,
    ];
    setInfoText(lines.join("\n"));
  }

  // ======================================================================
  //                                  CLEAR
  // ======================================================================

  function handleClear() {
    setRoot(null);
    setSearchPathKeys(null);
    setHighlightKey(null);
    setIsAnimatingSearch(false);
    setInfoText("Дерево очищено. Добавьте новый элемент.");
  }

  // ======================================================================
  //                               UI / JSX
  // ======================================================================

  return (
    <div className="bst-wrapper">
      <section className="bst-panel">
        {/* ---- Панель ввода ---- */}
        <div className="bst-controls">
          <div className="bst-input-group">
            <label className="bst-label">KEY</label>
            <input
              className="bst-input"
              type="number"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Например, 10"
            />
          </div>

          {/* Кнопки управления */}
          <div className="bst-buttons">
            <button className="bst-btn primary" onClick={handleInsert}>
              Insert
            </button>
            <button className="bst-btn" onClick={handleDelete}>
              Delete
            </button>
            <button className="bst-btn" onClick={handleSearch}>
              Search
            </button>
            <button className="bst-btn" onClick={handleShowTraversals}>
              Show Traversals
            </button>
            <button className="bst-btn ghost" onClick={handleClear}>
              Clear
            </button>
          </div>
        </div>

        {/* -------------------- Разметка: дерево + инфопанель -------------------- */}

        <div className="bst-layout">
          {/* ====== Карточка дерева ====== */}
          <div className="bst-canvas-card">
            <div className="bst-card-header">
              <span className="bst-card-title">Tree</span>
              {nodes.length > 0 && (
                <span className="bst-card-subtitle">
                  nodes: {nodes.length}, height: {Math.max(0, height(root))}
                </span>
              )}
            </div>

            <div className="bst-canvas-wrapper">
              <svg
                className="bst-svg"
                viewBox={`0 0 ${width} ${heightPx}`}
                preserveAspectRatio="xMidYMid meet"
              >
                {/* Рёбра */}
                {edges.map((edge) => (
                  <line
                    key={`${edge.from}-${edge.to}`}
                    x1={edge.x1}
                    y1={edge.y1}
                    x2={edge.x2}
                    y2={edge.y2}
                    className="bst-edge"
                  />
                ))}

                {/* Узлы */}
                {nodes.map((n) => {
                  const isH = highlightKey === n.key;
                  return (
                    <g
                      key={n.id}
                      className={`bst-node-group ${isH ? "highlighted" : ""}`}
                      transform={`translate(${n.x},${n.y})`}
                    >
                      <circle className="bst-node-circle" r="20" />
                      <text className="bst-node-text" dy="5">
                        {n.key}
                      </text>
                    </g>
                  );
                })}

                {/* Пустое дерево */}
                {!nodes.length && (
                  <text
                    x={width / 2}
                    y={heightPx / 2}
                    className="bst-empty-text"
                    textAnchor="middle"
                  >
                    Tree is empty
                  </text>
                )}
              </svg>
            </div>
          </div>

          {/* ====== Информационная панель ====== */}
          <div className="bst-info-card">
            <div className="bst-card-header">
              <span className="bst-card-title">Info</span>
            </div>

            {/* Вся текстовая информация */}
            <pre className="bst-info-text">{infoText}</pre>
          </div>
        </div>
      </section>
    </div>
  );
}
