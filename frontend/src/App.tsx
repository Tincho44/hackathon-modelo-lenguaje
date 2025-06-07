import ApiTest from "@components/ApiTest";
import "./App.css";

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>React + Vite + TypeScript + FastAPI</h1>
        <p>
          Frontend moderno con <strong>Vite</strong> y backend con{" "}
          <strong>FastAPI</strong>
        </p>
      </header>

      <main className="App-main">
        <ApiTest />

        <section className="features">
          <h2>Características del Setup</h2>
          <ul>
            <li>⚡ Vite para desarrollo ultra-rápido</li>
            <li>⚛️ React 19 con TypeScript</li>
            <li>🎯 Path aliases configurados</li>
            <li>🔌 Proxy configurado para API</li>
            <li>🏗️ Estructura de proyecto escalable</li>
            <li>🚀 FastAPI como backend</li>
          </ul>
        </section>
      </main>
    </div>
  );
}

export default App;
