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
│   │   ├── favorite.py 
│   │   └── user.py 
│   ├── schemas/
│   │   ├── xtream.py
│   │   ├── content.py
│   │   └── auth.py
│   ├── services/
│   │   ├── xtream_service.py
│   │   ├── stream_validator.py      
│   │   └── mappers/
│   │       ├── movie_mapper.py
│   │       ├── series_mapper.py
│   │       └── live_mapper.py
│   ├── db/
│   │   ├── base.py
│   │   ├── session.py
│   │   └── init_db.py
│   ├── utils/
│   │   └── text_cleaner.py
├── tests/
│   ├── unit/
│   │   ├── test_stream_validator.py
│   │   ├── test_live_mapper.py
│   │   ├── test_movie_mapper.py
│   │   └── test_series_mapper.py
│   ├── integration/
│   │   └── test_play_endpoints.py
│   ├── fixtures/       
│   ├── test_stream.py  
│   └── conftest.py  
├── pytest.ini
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

## 🔐 Autenticación y Seguridad

El backend utiliza autenticación basada en JWT (JSON Web Tokens).

### Flujo implementado

1. Usuario se registra (`POST /auth/register`)
2. Usuario inicia sesión (`POST /auth/login`) → para frontend
3. El backend genera un token firmado con `JWT_SECRET`
4. El frontend envía el token en el header:

```http
Authorization: Bearer <token>
```

### Nota: 
/auth/token se mantiene solo para pruebas internas desde Swagger; en producción se debe usar /auth/login.

## Swagger UI

* Para probar endpoints protegidos desde Swagger, se debe usar el botón Authorize y completar usuario y contraseña.
* Swagger generará el token y lo enviará automáticamente en cada request.
* Para acceder a rutas protegidas fuera de Swagger (Postman, navegador, curl), siempre se debe enviar el header:

```http
Authorization: Bearer <token>
```

Las rutas protegidas validan el token mediante:

- `OAuth2PasswordBearer`: define que se requiere un token Bearer en el header `Authorization`.
- `get_current_user`: extrae el token y valida la identidad del usuario.
- Decodificación y verificación del JWT con `python-jose` para asegurar autenticidad y expiración.


Las únicas rutas públicas son:

```text
POST /auth/register
POST /auth/login
```

El resto de endpoints pueden requerir autenticación.

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

### Películas ✅

* `GET /movies/categories`
* `GET /movies`
* `GET /movies/{id}`
* `GET /movies/{id}/play`

### Series ✅

* `GET /series/categories`
* `GET /series`
* `GET /series/{id}`
* `GET /series/{id}/play`

### Live TV ✅

* `GET /live/categories`
* `GET /live`
* `GET /live/{id}/play`

### Auth ✅

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

* Cliente Xtream Codes implementado y testeado
* Métodos: `_get`, `get_movies`, `get_series`, `get_live_tv`, `get_categories`
* Mock tests con pytest (`tests/test_stream.py`)
* Cliente modular y listo para integrarse a endpoints

### Día 4

* Implementación de endpoints de películas
* Integración real con XtreamClient
* Endpoint para listado de películas (limitado)
* Endpoint para categorías de películas
* Manejo de errores y validación de respuestas

### Día 5

* Endpoints de series
* Corrección de acceso por ID
* Ajuste del cliente Xtream (eliminación de método genérico de categorías)

### Día 6

* Implementación de endpoints de Live TV
* Integración con XtreamClient
* Esquema LiveTVSchema ajustado a datos reales de Xtream
* Manejo de campos opcionales y extra="ignore"
* Limitación de resultados para evitar sobrecarga

### Día 7

* Configuración inicial de base de datos con SQLAlchemy
* Creación de Base y SessionLocal
* Definición de modelo Favorite
* Inicialización de SQLite mediante init_db
* Separación clara entre datos de Xtream y estado propio del backend

### Día 8

* Implementación de modelo User
* Registro de usuario
* Login con validación de credenciales
* Generación de JWT Firmado
* Configuración de JWT_SECRET
* Integración de seguridad con passlib + bcrypt
* Protección de rutas mediante OAuth2PasswordBearer y get_current_user
* Ajuste de Swagger para probar rutas protegidas
* /auth/token solo para pruebas, producción usa /auth/login

### Día 9

* Limpieza y normalización robusta de datos provenientes de Xtream
* Implementación de RawMovieSchema para manejar inconsistencias de tipos
* Conversión segura de rating y stream_id
* Aplicación de límite antes de validación para evitar bloqueos
* Corrección de mapeo de poster en /movies/{id} (movie_image / cover fallback)
* Separación clara entre:
  - Capa cruda (RawSchema)
  - Capa de limpieza
  - Capa de normalización
* Normalización de series:
  - Solo se muestran temporadas con episodios
  - Episodios ordenados por número
  - Limpieza de títulos y descripciones
* Implementación de endpoints de reproducción:
  - `GET /movies/{id}/play`
  - `GET /series/{id}/play`
* Generación segura de URLs de streaming desde backend
* Encapsulamiento total de credenciales Xtream
* implementar RawLiveSchema para manejar inconsistencias de Xtream
* crear normalize_live() siguiendo el mismo flujo que movies y series
* Endpoint /live/{id}/play genera URLs de reproducción seguras
* Limpieza de títulos y extracción de calidad y país integrada

### Día 10

Objetivo: 

* Implementar segmentación del catálogo directamente en Xtream para reducir carga innecesaria y mejorar organización.

Alcance:

* Extensión de XtreamClient para soportar category_id opcional
* Modificación de: get_movies, get_series, get_live_tv
* Aplicación de filtro en origen (Xtream) mediante extra_params
* Extensión de endpoints existentes con query param opcional:
  * `GET /movies?category_id=`
  * `GET /series?category_id=`
  * `GET /live?category_id=`
* Compatibilidad hacia atrás garantizada
* Preparación arquitectónica para futura cache por categoría

Resultado esperado:

* Reducción de carga innecesaria
* Mejor segmentación del catálogo
* Base sólida para optimización futura

### Día 11

Objetivo: 

* Validar reproducibilidad de streams
* Reducir requests innecesarios a Xtream
* Agregar capa de cache con TTL y control de concurrencia

Alcance:

* Implementación de validate_stream(stream_type, stream_id, url) como única interfaz pública
* Separación interna de validadores:
  * _check_vod (HEAD para movies y series)
  * _check_live (HEAD liviano para Live TV)
* Eliminación de validación profunda por chunks en Live (evita carga infinita)
* Implementación de cache en memoria:
  * Key basada en stream_type:stream_id
  * TTL configurable por tipo
* Configuración TTL:
  * Live → 15 minutos
  * Movie → 24 horas
  * Series → 24 horas
* Implementación de _validation_semaphore para limitar concurrencia (máx 5 validaciones simultáneas)
* Prevención de múltiples requests simultáneos hacia Xtream
* Integración de validación en endpoints:
  - `/movies/{id}/play`
  - `/series/{id}/play`
  - `/live/{id}/play`
* Corrección de bloqueo en Live causado por lectura de chunks infinitos
* Optimización de tiempo de respuesta en reproducción

Decisión arquitectónica importante:

* Live TV no se valida mediante lectura de flujo completo.
* Solo se valida mediante HEAD + status + content-type.
* Streams que respondan 200 pero no transmitan señal pueden seguir apareciendo
  (limitación propia del ecosistema IPTV).

Resultado:

* Eliminada carga infinita en endpoints Live
* Capa de validación consistente y unificada
* Backend protegido ante validaciones masivas
* Reducción de riesgo de bloqueo por parte del proveedor Xtream

### Día 12 (En Progreso)

Objetivo: 

* Consolidar estabilidad del backend
* Validar comportamiento real de reproducción
* Preparar base sólida para release v1.0.0

Alcance implementado:

* Corrección en endpoint de series:
  - Validación ahora se realiza por `episode_id`
  - Eliminación de validación incorrecta por `series_id`
* Ajuste final de integración entre endpoints `/play` y `validate_stream`

Testing:

Tests unitarios:

* Cobertura completa de `stream_validator`
* Validación de:
  - Cache miss
  - Cache válido
  - Cache expirado (stale-while-revalidate)
  - Control de concurrencia
  - Prevención de validaciones duplicadas simultáneas

Tests de integración:

* `/movies/{id}/play`
* `/series/{series_id}/{episode_id}/play`
* `/live/{id}/play`

Escenarios cubiertos:

* Stream válido
* Stream inválido
* Recurso inexistente
* Episodio inexistente
* Manejo correcto de códigos HTTP (200, 404, 400)

Refactor técnico:

* Migración de `@app.on_event("startup")` a sistema moderno de `lifespan`
* Eliminación de advertencias deprecadas de FastAPI
* Limpieza general de código
* Validación final de timeouts y manejo de errores

---

### Refactor de limpieza de datos IPTV (`text_cleaner`)

Se refactorizó el módulo `text_cleaner.py` para mejorar la normalización de títulos provenientes de proveedores IPTV.

Problemas detectados en listas reales:

* Superíndices Unicode (`¹`, `²`, `³`)
* Símbolos residuales (`*`, `|`, `-`)
* Calidad mezclada con el nombre del canal (`HD`, `SD`, `FHD`, `4K`)
* Sufijos técnicos o marcas de proveedor

Mejoras implementadas:

* Eliminación de caracteres Unicode no deseados
* Limpieza consistente de símbolos
* Normalización de espacios y separadores
* Mejora en extracción de calidad
* Normalización de títulos antes de ser procesados por los mappers

Resultado:

* Títulos más consistentes
* Mejor identificación de canales
* Datos más estables para consumo del frontend

---

### Tests de normalización de Live TV (`live_mapper`)

Se iniciaron los **tests unitarios para los mappers**, comenzando por `live_mapper`.

Tests implementados:

* `test_live_mapper_normalization`
* `test_live_mapper_country_detection`
* `test_live_mapper_requires_stream_id`
* `test_live_mapper_title_fallback`
* `test_live_mapper_country_without_spaces`
* `test_live_mapper_handles_missing_logo`
* `test_live_mapper_handles_missing_optional_fields`

Cobertura lograda:

* Normalización de títulos
* Detección de país
* Manejo de caracteres extraños
* Manejo de datos faltantes
* Validación de `stream_id` obligatorio

Resultado:

* `live_mapper` validado contra múltiples formatos reales de listas IPTV
* Base preparada para continuar con:
  * `movie_mapper`
  * `series_mapper`

### Tests de normalización de películas (`movie_mapper`)

Se añadieron **tests unitarios específicos para la normalización de películas**.

Tests implementados:

* `test_movie_mapper_basic_normalization`
* `test_movie_mapper_requires_stream_id`
* `test_movie_mapper_removes_emojis`
* `test_movie_mapper_invalid_rating`
* `test_movie_mapper_handles_missing_poster`
* `test_movie_mapper_preserves_category`
* `test_movie_mapper_handles_missing_category`
* `test_movie_mapper_without_year`
* `test_movie_mapper_whitespace_cleanup`

Cobertura lograda:

* Normalización completa del objeto película
* Conversión de `stream_id → id`
* Limpieza de títulos IPTV (espacios, emojis, símbolos)
* Extracción segura de año desde el título
* Conversión segura de `rating` a float
* Manejo de ratings corruptos
* Manejo de ausencia de `poster`
* Manejo de ausencia de `category_id`
* Validación de `stream_id` obligatorio

Resultado:

* `movie_mapper` validado contra múltiples inconsistencias reales de catálogos IPTV
* Datos normalizados antes de llegar al frontend
* Prevención de errores provenientes del proveedor Xtream

---

### Tests de normalización de series (`series_mapper`)

Se añadieron **tests unitarios para la normalización de series, temporadas y episodio**.

Tests implementados:

* `test_series_mapper_basic`
* `test_series_detail_seasons_and_episodes_sorted`
* `test_series_detail_episode_title_cleanup`
* `test_series_detail_empty_seasonsg`
* `test_series_detail_total_episodes_count`
* `test_series_detail_handles_missing_episode_number`
* `def test_series_detail_ignores_empty_seasons:`

Cobertura lograda:

* Normalización de títulos de series
* Extracción de año desde el nombre
* Limpieza de títulos de episodios (emojis y ruido IPTV)
* Orden correcto de temporadas (`season_number`)
* Orden correcto de episodios dentro de cada tempodarada (`season_number`)
* Conteo total de episodios
* Manejo de estructuras vacías provenientes de Xtream

Corrección aplicada:

* Ordenamiento explícito de temporadas (`season_number`)
* Prevención de desorden típico en respuestas de Xtream
* Tolerancia a episodios incompletos (sin número)

Resultado:

* series_mapper validado contra estructuras reales de Xtream
* Datos consistentes y ordenados para consumo del frontend
* Eliminación de errores potenciales en UI (temporadas desordenadas)
* Categorías de series normalizadas correctamente desde `xtream_client`

---

### Tests de cliente xtream (`xtream_client`)

Se añadieron **tests unitarios enfocados en la obtención y normalización de categorías de series desde Xtream**.

Tests implementados:

* `test_series_categories_basic`
* `test_series_categories_invalid_data`
* `test_series_categories_empty`

Cobertura lograda:

* limpieza de nombres de categorías (emojis y texto IPTV)
* Manejo de datos inválidos provenientes de Xtream
* Manejo de listas vacías
* Robustez ante respuestas inconsistentes del proveedor

Resultado:

* Categorías normalizadas correctamente
* Cliente resiliente frente a datos corruptos
* Limpieza de categorías provenientes de Xtream
* Manejo de datos inválidos en categorías
* Manejo de listas vacías en categorías
* Base lista para consumo por frontend

---

Resultado del Día:

* Validación de streams completamente testeada
* Limpieza de títulos mejorada (text_cleanner refactor)
* `live_mapper`, `movie_mapper` y `series_mapper` cubiertos con tests unitarios
* Tests de categorías de series implementados en `xtream_cliemt`
* Normalización robusta para movies, live y series validada
* Orden correcto de temporadas y episodios garantizado
* Manejo de datos incompletos (ratings, episodios, categorías)
* Backend más robusto frente a datos inconsistentes de Xtream


### Día 13

* Release v1.0.0

---

## 📌 Estado Actual

```text
Estado: 🟢 Estable – Backend listo para frontend
Última fase: Día 12 – Tests unitarios e integración (en progreso)

Avances recientes:

- Refactor completo de text_cleaner para catálogos IPTV reales
- Implementación robusta de normalize_live()
- Detección automática de prefijos de país
- Limpieza avanzada de sufijos IPTV
- Creación de test_live_mapper.py
- Creación de test_movie_mapper.py (9 tests unitarios)
- Creación de test_series_mapper.py (normalización, temporadas, episodios y edge cases)
- Implementación de tests de categorías de series en xtream_client
- Cobertura de casos edge comunes en listas IPTV
- Manejo robusto de datos incompletos (episodios sin número, temporadas vacías, categorías inválidas)
- Validación de normalización de películas, series y live frente a datos inconsistentes de Xtream


Próximo paso:

- Edge cases adicionales en live_mapper
- Tests base para xtream_client (_get, manejo de errores HTTP, timeouts)
- Extender tests de categorías a movies y live
- Consolidación final de la capa de normalización
- Preparación para cierre de Día 12 → release v1.0.0 (Día 13)
```

---

## 🧭 Nota Importante
Este README es la **fuente de verdad del proyecto**.

Cualquier cambio importante en arquitectura, stack o flujo **debe reflejarse aquí**.

---

✍️ Proyecto desarrollado como práctica profesional de backend y arquitectura web.

```

