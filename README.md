# Training IA BF

## Backend FastAPI con JWT

Este repositorio incluye una aplicación Web API en `/backend` construida con **Python**, **FastAPI** y **Poetry**.

### Funcionalidad

- Autenticación con usuario `admin`
- Contraseña `admin123`
- Generación de **access token JWT** con expiración de **300 segundos**
- Endpoint para **refrescar** el token
- Hashing de contraseñas con `passlib[bcrypt]`
- Dependencia `bcrypt` fijada a `>=3.2,<4.0`
- Archivos `Dockerfile` y `docker-compose.yml` para despliegue con Docker

### Estructura

```text
backend/
├── app/
│   └── main.py
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

### Requisitos

- Python 3.12+
- Poetry 2.x

### Ejecución local con Poetry

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

La API quedará disponible en `http://127.0.0.1:8000`.

### Endpoints

#### 1. Obtener token

`POST /auth/token`

Ejemplo de body:

```json
{
  "usuario": "admin",
  "password": "admin123"
}
```

Respuesta esperada:

```json
{
  "access_token": "jwt...",
  "refresh_token": "jwt...",
  "token_type": "bearer",
  "expires_in": 300
}
```

#### 2. Refrescar token

`POST /auth/refresh`

Ejemplo de body:

```json
{
  "refresh_token": "jwt..."
}
```

### Pruebas rápidas con curl

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/json" \
  -d '{"usuario":"admin","password":"admin123"}'
```

```bash
curl -X POST http://127.0.0.1:8000/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token":"<tu_refresh_token>"}'
```

### Ejecución con Docker

```bash
cd backend
docker compose up --build
```

La aplicación quedará expuesta en `http://127.0.0.1:8000`.

### Variable de entorno

- `JWT_SECRET_KEY`: clave usada para firmar los JWT. Si no se define, la aplicación usa `change-me-in-production`.
