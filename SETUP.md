# Setup del Proyecto - FastAPI + React

Este proyecto incluye un backend en **FastAPI** con Docker y un frontend en **React** con Vite que corre localmente.

## Estructura del Proyecto

```
hackathon-modelo-lenguaje/
├── 📁 backend/                    # Backend FastAPI
│   ├── Dockerfile                 # Docker para FastAPI
│   ├── main.py                    # Aplicación FastAPI
│   ├── requirements.txt           # Dependencias Python
│   └── .dockerignore             # Exclusiones Docker
├── 📁 frontend/                   # Frontend React + Vite + TypeScript
│   ├── src/                      # Código fuente React
│   │   ├── components/           # Componentes React
│   │   ├── hooks/                # Custom hooks
│   │   ├── services/             # Servicios API
│   │   ├── types/                # Tipos TypeScript
│   │   ├── utils/                # Utilidades
│   │   ├── App.tsx               # Componente principal
│   │   └── main.tsx              # Entry point
│   ├── public/                   # Archivos estáticos
│   ├── package.json              # Dependencias Node.js
│   ├── vite.config.ts            # Configuración Vite
│   └── tsconfig.*.json           # Configuración TypeScript
├── 📄 docker-compose.yml          # Orquestación completa
├── 📄 .gitignore                  # Archivos ignorados
└── 📄 README.md                   # Documentación
```

## 🚀 Cómo Ejecutar

### 1. Backend (FastAPI con Docker)

```bash
# En la raíz del proyecto
docker-compose up --build
```

El backend estará disponible en:

- **API**: http://localhost:8000
- **Documentación**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### 2. Frontend (React con Vite - Local)

```bash
# Navegar al directorio frontend
cd frontend

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar en modo desarrollo
npm run dev
```

El frontend estará disponible en:

- **Aplicación**: http://localhost:3000

## 🔧 Configuración

### Backend

- **Puerto**: 8000
- **Hot Reload**: Activado con volúmenes Docker
- **Documentación automática**: FastAPI genera docs en `/docs`
- **Ubicación**: `./backend/`

### Frontend

- **Puerto**: 3000
- **Hot Reload**: Activado con Vite
- **Proxy API**: Configurado para `/api` → `http://localhost:8000`
- **TypeScript**: Completamente tipado
- **Path Aliases**: Configurados (@components, @hooks, etc.)
- **Ubicación**: `./frontend/`

## 📁 Estructura Frontend

```
frontend/src/
├── components/     # Componentes React
├── hooks/         # Custom hooks
├── services/      # Servicios API
├── types/         # Tipos TypeScript
├── utils/         # Utilidades
├── App.tsx        # Componente principal
└── main.tsx       # Entry point
```

## 🌐 Comunicación Frontend-Backend

El frontend está configurado con un proxy en Vite que redirige las llamadas `/api/*` al backend en `http://localhost:8000`.

Ejemplo de uso:

```typescript
// En el frontend, esto llamará a http://localhost:8000/health
const response = await fetch("/api/health");
```

## 📝 Scripts Disponibles

### Backend (desde la raíz)

```bash
docker-compose up --build    # Ejecutar backend
docker-compose down          # Detener backend
docker-compose logs          # Ver logs
```

### Frontend (desde ./frontend/)

```bash
cd frontend                  # Cambiar al directorio frontend
npm run dev                  # Desarrollo
npm run build                # Build producción
npm run preview              # Preview del build
npm run lint                 # Linter ESLint
```

## 🔍 Testing de la API

El frontend incluye un componente `ApiTest` que automáticamente:

- ✅ Prueba la conexión con el backend
- ✅ Muestra el health check
- ✅ Demuestra las llamadas a la API

## 🗂️ Archivos Importantes

### **`__pycache__`**

- ⚠️ **Se eliminó**: Es una carpeta temporal de Python
- 🔄 **Se regenera automáticamente** cuando ejecutas Python
- 📝 **Está en .gitignore** para no subirla al repositorio

### **Un solo `docker-compose.yml`**

- 📍 **Ubicación**: Raíz del proyecto
- 🎯 **Función**: Orquesta todo el backend
- 🔗 **Referencia**: `./backend/` como contexto de build

## 🛠️ Tecnologías Utilizadas

### Backend

- **FastAPI** - Framework web rápido para Python
- **Uvicorn** - Servidor ASGI
- **Docker** - Containerización
- **Pydantic** - Validación de datos

### Frontend

- **React 19** - Biblioteca UI
- **Vite** - Build tool y dev server
- **TypeScript** - Tipado estático
- **Custom Hooks** - Lógica reutilizable
- **Path Aliases** - Imports limpios
