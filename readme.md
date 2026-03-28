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
release/*   → preparación de versiones antes de merge a main
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
│   │   ├── security.py
│   │   └── xtream_store.py
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
│   │   ├── test_series_mapper.py
│   │   └── test_xtream_client.py
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
JWT_SECRET=supersecret
DATABASE_URL=sqlite:///./iptv.db
```
Las credenciales Xtream ahora se configuran por usuario mediante endpoint protegido.
`POST /auth/xtream`

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

## 👥 Credenciales Xtream por Usuario

El backend ahora soporta credenciales Xtream independientes por usuario.
Cada usuario puede configurar su propio proveedor IPTV sin afectar a otros.

Endpoint:

POST /auth/xtream

Body:

{
  "host": "http://example.com:8080",
  "username": "user",
  "password": "pass"
}

Requiere autenticación JWT.

Flujo:

1. Usuario se registra
2. Usuario inicia sesión
3. Usuario configura sus credenciales Xtream
4. El backend usa esas credenciales en todos los endpoints

Ventajas:

* Multi-usuario real
* Sin variables globales
* Cada usuario usa su propio proveedor IPTV
* Preparado para persistencia futura en base de datos


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
* `POST /auth/xtream`

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

* `test_live_mapper_dirty_titles`
* `test_live_mapper_country_detection`
* `test_live_mapper_requires_stream_id`
* `test_live_mapper_title_fallback`
* `test_live_mapper_country_without_spaces`
* `test_live_mapper_handles_missing_logo`
* `test_live_mapper_handles_missing_optional_fields`
* `test_live_mapper_handles_empty_name`
* `test_live_mapper_extracts_quality_in_weird_positions`

Cobertura lograda:

* Limpieza de títulos ofuscados y corryptos (IPTV real)
* Detección de país desde prefijos (CL |, AR |, etc)
* Extracción de calidad (HD, SD, etc)
* Normalización de títulos finales
* Manejor de datos faltantes(logo, category_id)
* Validación de `stream_id` obligatorio
* Protección contra títulos vacíos o inválidos

Resultado:

* `live_mapper` validado contra múltiples formatos reales de listas IPTV
* Datos limpios y consistentes para consumo del frontend
* Mayor resiliencia frente a datos corruptos del proveedor

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
* `test_series_detail_empty_seasons`
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
* Manejo de episodios sin `episode_num`

Corrección aplicada:

* Ordenamiento explícito de temporadas (`season_number`)
* Prevención de desorden típico en respuestas de Xtream

Resultado:

* series_mapper validado contra estructuras reales de Xtream
* Datos consistentes y ordenados para consumo del frontend
* Eliminación de errores potenciales en UI (temporadas desordenadas)

---


### Tests de cliente Xtream (`xtream_client`)

Se añadieron **tests unitarios para el método `_get` del cliente Xtream**.

Tests implementados:

* `test_get_success`
* `test_get_http_error`
* `test_get_timeout`
* `test_get_invalid_json`
* `test_get_api_error_field`
* `test_get_with_extra_params`
* `test_get_empty_response`

Cobertura lograda:

* Manejo de errores HTTP
* Manejo de timeouts
* Protección ante JSON inválido
* Detección de errores lógicos en respuesta (`"error"`)
* Envío correcto de parámetros adicionales (`category_id`)
* Manejo de respuestas vacías `{}` como válidas

Resultado:

* Cliente Xtream resiliente ante fallos reales
* Diferenciación clara entre error (`None`) y respuesta válida vacía (`{}`)
* Base sólida para consumo seguro desde servicios web

---

Resultado del Día:

* Validación de streams completamente testeada
* Limpieza de títulos mejorada (`text_cleaner` refactor)
* `live_mapper`, `movie_mapper` y `series_mapper` cubiertos con tests unitarios
* `xtream_client` completamente testeado (método `_get`)
* Normalización robusta para movies, live y series validada
* Manejo robusto de errores HTTP, timeout y respuestas inválidas
* Manejo correcto de respuestas vacías {} en cliente Xtream
* Orden correcto de temporadas y episodios garantizado
* Backend más robusto frente a datos inconsistentes de Xtream


### Día 13

Objetivo:

* Publicar la primera versión estable del backend
* Preparar base para soporte multi-usuario Xtream

Alcance:

* Release v1.0.0 (backend single-user)
* Implementación de credenciales Xtream por usuario en memoria
* Eliminación de variables globales XTREAM_*
* Creación de endpoint protegido POST /auth/xtream
* Asociación de credenciales Xtream al usuario autenticado
* Ajuste de endpoints movies, series y live para usar credenciales por usuario
* Validación de credenciales antes de consumir Xtream
* Backend preparado para arquitectura multi-tenant
* Implementación inicial sin persistencia (almacenamiento temporal en memoria)

Resultado:

* Backend estable v1.0.0 publicado
* Soporte multi-usuario Xtream en memoria
* Eliminación de dependencia de variables globales
* Arquitectura preparada para persistencia en base de datos

### Día 14

Objetivo:

* Persistir credenciales Xtream por usuario en base de datos
* Proteger datos sensibles mediante hashing

Alcance:

* Creación de modelo XtreamCredentials
* Relación 1:M con User
* Migración de almacenamiento en memoria a base de datos
* Hash de password Xtream antes de guardar
* Ajuste de servicios para leer desde DB
* Eliminación del almacenamiento en memoria
* Manejo de credenciales inexistentes

Resultado:

* Credenciales persistentes
* Mayor seguridad
* Backend preparado para producción


### Día 15

Objetivo:

* Preparar release v1.1.0
* Completar despliegue en Render

Alcance:

* Configuración variables de entorno producción
* Ajuste DATABASE_URL para PostgreSQL
* Validación JWT en producción
* Pruebas de endpoints desplegados
* Configuración CORS para frontend
* Verificación de timeouts Xtream en entorno real

Resultado:

* Backend desplegado en Render
* Release v1.1.0
* Backend listo para integración frontend en producción


---

## 📌 Estado Actual

```text
Estado: 🟢 Estable – Multi-usuario Xtream (en memoria)
Última fase: Día 13 – Release v1.0.0 y Credenciales Xtream por usuario (COMPLETADO)

Avances recientes:

- Soporte multi-usuario para credenciales Xtream
- Eliminación de variables globales XTREAM_*
- Endpoint protegido POST /auth/xtream
- Asociación de credenciales por usuario autenticado
- Backend preparado para multi-tenant
- Ajuste de endpoints movies, series y live para usar credenciales por usuario

Próximos pasos:

- Persistir credenciales Xtream en base de datos
- Hash de datos sensibles
- Release v1.1.0
- Deploy en Render

```

---

## 🧭 Nota Importante
Este README es la **fuente de verdad del proyecto**.

Cualquier cambio importante en arquitectura, stack o flujo **debe reflejarse aquí**.

---

✍️ Proyecto desarrollado como práctica profesional de backend y arquitectura web.

```

