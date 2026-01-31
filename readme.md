# IPTV Viewer – Backend

## 📌 Descripción

Backend del proyecto **IPTV Viewer**, desarrollado para consumir la API de **Xtream Codes** de forma segura y exponer endpoints propios para un frontend web.

Este proyecto se construye **siguiendo un flujo profesional**, con control de versiones en GitHub, ramas, pull requests y trabajo secuenciado por días, simulando un entorno real de equipo.

---

## 🎯 Objetivo del Backend

* Encapsular la API de Xtream Codes
* Evitar exponer credenciales en el frontend
* Proveer endpoints limpios y seguros
* Gestionar usuarios, favoritos e historial
* Servir como base para el frontend web

---

## 🧱 Stack Tecnológico

* **Python 3.12+**
* **FastAPI** – Framework backend
* **Pydantic / pydantic-settings** – Validación y configuración
* **SQLAlchemy** – ORM
* **SQLite** (inicio) → **PostgreSQL** (futuro)
* **httpx** – Cliente HTTP async
* **JWT** – Autenticación
* **pytest** – Testing

---

## 🧠 Arquitectura General

```text
Frontend (React)
   ↓
FastAPI Backend
   ↓
Xtream Codes API
```

El frontend **nunca** se comunica directamente con Xtream Codes.

---

## 🌳 Flujo Git (Obligatorio)

### Repositorio

El proyecto vive en **GitHub** y el repositorio se crea **antes de iniciar el desarrollo local**.

Estado inicial del repositorio:

```text
main      → rama estable (vacía o solo README)
develop   → rama base de desarrollo
```

No se crean otras ramas permanentes.

Las ramas `feature/*` y `test/*` se crean **solo cuando son necesarias** y se eliminan después del merge.

### Ramas principales

```text
main        → versión estable / releases
develop     → integración continua
feature/*   → desarrollo de funcionalidades
test/*      → pruebas y fixes (temporales)
```

### Reglas

* ❌ No commits directos a `main`
* ❌ No desarrollo directo en `develop`
* ✅ Todo entra vía Pull Request
* ✅ Commits semánticos

Ejemplo:

```text
feat: agregar endpoint de películas
fix: manejar timeout en xtream
chore: preparar entorno de desarrollo
```

---

## 🧾 Convención de Commits (Conventional Commits)

Este proyecto utiliza **Conventional Commits en español**.

### 📌 Formato

```text
<tipo>(opcional-alcance): descripción breve en infinitivo
```

### 🏷️ Tipos permitidos

* **feat**: nueva funcionalidad
* **fix**: corrección de errores
* **docs**: documentación
* **chore**: tareas de mantenimiento
* **refactor**: cambios internos sin alterar comportamiento
* **test**: pruebas
* **perf**: mejoras de rendimiento
* **build**: dependencias o build
* **ci**: integración continua

### 📍 Ejemplos reales

```text
feat: agregar health check
feat(xtream): implementar cliente base
fix(auth): corregir validación de token
docs: documentar variables de entorno
chore: inicializar estructura del proyecto
```

### ⚠️ Reglas

* Usar verbo en infinitivo
* No usar mayúsculas iniciales
* No terminar con punto
* Un commit = un cambio lógico

---

## 📁 Estructura del Backend

```text
backend/
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── api/
│   │   └── routes/
│   │       ├── movies.py
│   │       ├── series.py
│   │       ├── live.py
│   │       └── auth.py
│   ├── models/
│   ├── schemas/
│   ├── services/
│   │   └── xtream_service.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   └── utils/
├── tests/
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🔐 Variables de Entorno

```env
XTREAM_HOST=http://example.com:8080
XTREAM_USERNAME=user
XTREAM_PASSWORD=pass
JWT_SECRET=supersecret
DATABASE_URL=sqlite:///./iptv.db
```

⚠️ El archivo `.env` **no se sube al repositorio**.

---

## 🛡️ Uso responsable de la API Xtream Codes

Xtream Codes **no es una API pública oficial** y puede aplicar bloqueos automáticos ante uso abusivo.

Este backend implementa medidas preventivas para evitar el bloqueo del acceso.

### Medidas obligatorias

* **Nunca** exponer credenciales en el frontend
* **Cachear respuestas** según tipo de recurso
* **Timeouts estrictos** en todas las peticiones
* **Control de concurrencia**
* **Evitar peticiones masivas sin filtros**

### Política de cache recomendada

```text
Categorías        → 6 horas
Películas / Series → 30–60 minutos
Live TV           → 1–5 minutos
```

### Buenas prácticas

* No solicitar listas completas sin categoría
* No realizar múltiples llamadas concurrentes
* No aplicar retries infinitos

Estas decisiones son **arquitectónicas** y forman parte del diseño del backend.

---

## 📡 Endpoints Planeados

### Películas

* `GET /movies/categories`
* `GET /movies`
* `GET /movies/{id}`

### Series

* `GET /series/categories`
* `GET /series`
* `GET /series/{id}`

### Live TV

* `GET /live/categories`
* `GET /live`

### Auth

* `POST /auth/login`
* `POST /auth/register`

---

## 📆 Roadmap de Desarrollo (Backend)

### Día 1

* Setup del proyecto
* FastAPI corriendo
* Health check

### Día 2

* Configuración y entorno

### Día 3

* Cliente Xtream Codes

### Día 4

* Endpoints de películas

### Día 5

* Endpoints de series

### Día 6

* Live TV

### Día 7

* Base de datos y modelos

### Día 8

* Autenticación JWT

### Día 9

* Tests

### Día 10

* Release v1.0.0

---

## 📌 Estado Actual

```text
Estado: 🟢 En desarrollo
Última fase: Día 1 – Setup del proyecto (COMPLETADO)
Avances:
- Repositorio y ramas configuradas (main / develop)
- README y .gitignore iniciales
- Entorno virtual creado
- Dependencias base instaladas
- FastAPI levantado correctamente
- Endpoint /health operativo
- Swagger (/docs) funcionando
Próximo paso: Día 2 – Configuración y entorno
```

```

---

## 🧭 Nota Importante
Este README es la **fuente de verdad del proyecto**.

Cualquier cambio importante en arquitectura, stack o flujo **debe reflejarse aquí**.

---

✍️ Proyecto desarrollado como práctica profesional de backend y arquitectura web.

```
