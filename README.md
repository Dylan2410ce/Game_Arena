# GameArena API

API creada con Django y Django REST Framework para administrar videojuegos, jugadores, torneos e inscripciones.

## Instalación y ejecución

En la terminal, dentro de la carpeta del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install django djangorestframework
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La API queda levantada en `http://127.0.0.1:8000/`.

## Pruebas

```powershell
python manage.py test
```

## Token

Solicita un token con `POST /api/token/`:

```json
{
  "username": "usuario",
  "password": "contraseña"
}
```
Para las rutas protegidas envía este header

```text
Authorization: Token tu_token
```

## Rutas principales
| Método | Ruta | Descripción |
| --- | --- | --- |
| GET, POST | `/api/videojuegos/` | Listar y crear videojuegos. |
| GET, PUT, PATCH, DELETE | `/api/videojuegos/<id>/` | Consultar y administrar un videojuego. |
| GET | `/api/videojuegos/ultimo-visitado/` | Consultar el último videojuego visto en la sesión. |
| GET, POST | `/api/jugadores/` | Listar y registrar jugadores. |
| GET, PATCH | `/api/jugadores/<id>/` | Consultar y actualizar un jugador. |
| GET | `/api/jugadores/perfil/` | Consultar el perfil del usuario autenticado. |
| GET, POST | `/api/torneos/` | Listar torneos y crearlos como administrador. |
| GET, PUT, PATCH, DELETE | `/api/torneos/<id>/` | Consultar y administrar un torneo. |
| GET, POST | `/api/torneos/<id>/inscripciones/` | Ver participantes e inscribir un jugador autenticado. |
| GET | `/api/admin/estadisticas/` | Consultar estadísticas como administrador.