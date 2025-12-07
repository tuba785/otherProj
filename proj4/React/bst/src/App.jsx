import React from "react";
import "./App.css";
import BSTVisualizer from "./components/bst/bst";

function App() {
  return (
    <div className="app-root">
      <header className="app-header">
        <h1>Binary Search Tree Visualizer</h1>
        <p>Интерактивный визуализатор структуры BST (Binary Search Tree)</p>
      </header>
      <main className="app-main">
        <BSTVisualizer />
      </main>
    </div>
  );
}

export default App;
