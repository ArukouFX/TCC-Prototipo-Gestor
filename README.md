# UTEC Scheduler

UTEC Scheduler es un prototipo de gestor de horarios para carreras universitarias, desarrollado como parte de un proyecto de conclusión de curso (TCC). Permite la gestión y visualización de horarios de cursos, materias, docentes y aulas, integrando un algoritmo genético para la generación automática de horarios óptimos.

## Características

- **Gestión de entidades**: Cursos, materias, docentes y aulas.
- **Visualización de horarios**: Interfaz web para consultar y editar horarios.
- **Generación automática**: Algoritmo genético para optimizar la asignación de horarios.
- **API RESTful**: Backend basado en Django REST Framework.
- **Soporte para laboratorios y preferencias docentes**.
- **Despliegue con Docker**.

## Demostración en Video

[Ver en YouTube](https://www.youtube.com/watch?v=U1Fy_rCTfVc)

## Estructura del Proyecto

```
utec_scheduler/
├── scheduler/                # Aplicación principal Django
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── templates/
│   │   └── scheduler/
│   │       ├── base.html
│   │       └── schedule.html
│   ├── static/
│   │   └── scheduler/
│   │       ├── css/
│   │       │   └── style.css
│   │       └── js/
│   │           └── scheduler.js
│   ├── fixtures/             # Datos de ejemplo (JSON)
│   └── migrations/
├── utec_scheduler/
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
└── manage.py
```

## Instalación y Ejecución

### Requisitos

- Docker y Docker Compose
- (Opcional) Python 3.9+ y pip (para desarrollo local)

### Configuración rápida con Docker

1. **Clona el repositorio y entra al directorio:**

   ```sh
   git clone <repo-url>
   cd utec_scheduler
   ```

2. **Configura las variables de entorno en `.env`**  
   (ya provisto en el proyecto, revisa los valores según tu entorno)

3. **Construye y levanta los servicios:**

   ```sh
   docker-compose up --build
   ```

4. **Accede a la aplicación:**
   - Backend/API: [http://localhost:8000/api/](http://localhost:8000/api/)
   - Interfaz web: [http://localhost:8000/horarios/](http://localhost:8000/horarios/)

### Uso en desarrollo local (sin Docker)

1. Instala dependencias:

   ```sh
   pip install -r requirements.txt
   ```

2. Aplica migraciones y carga datos de ejemplo:

   ```sh
   python manage.py migrate
   python manage.py loaddata scheduler/fixtures/rooms.json
   python manage.py loaddata scheduler/fixtures/courses.json
   python manage.py loaddata scheduler/fixtures/subjects.json
   python manage.py loaddata scheduler/fixtures/teachers.json
   python manage.py loaddata scheduler/fixtures/schedules.json
   ```

3. Ejecuta el servidor:

   ```sh
   python manage.py runserver
   ```

## Endpoints principales

- `/api/rooms/` — CRUD de aulas
- `/api/courses/` — CRUD de cursos
- `/api/subjects/` — CRUD de materias
- `/api/teachers/` — CRUD de docentes
- `/api/schedules/` — CRUD de horarios
- `/horarios/` — Interfaz web para gestión de horarios

## Algoritmo Genético

El archivo [`utec_scheduler/genetic_algorithm.py`](utec_scheduler/genetic_algorithm.py) implementa la lógica para la generación automática de horarios, considerando restricciones como:

- Solapamiento de horarios
- Preferencias de docentes
- Uso adecuado de laboratorios
- Turnos de los cursos

## Personalización

- Modifica los modelos en [`scheduler/models.py`](scheduler/models.py) para adaptar a tus necesidades.
- Cambia los estilos en [`scheduler/static/scheduler/css/style.css`](scheduler/static/scheduler/css/style.css).
- Edita la lógica de frontend en [`scheduler/static/scheduler/js/scheduler.js`](scheduler/static/scheduler/js/scheduler.js).

## Licencia

Proyecto académico. Uso libre para fines educativos.

---

**Autor:**  
Luis Felipe Carballo (ArukouFX)  
UTEC - 2025
