# 🛡️ Sistema de Control de Garita

Sistema web para el control de acceso vehicular. Permite registrar entradas y salidas de vehículos, generar códigos QR por vehículo y gestionar el historial de movimientos.

---

## ✨ Funcionalidades

- **Login** con autenticación JWT
- **Dashboard** con estadísticas en tiempo real (entradas, salidas y total del día)
- **Registrar vehículos** con entrada o salida, con opción de escanear QR para autocompletar
- **Solicitudes** — historial filtrado por fecha con búsqueda por placa o conductor
- **Reportes** — historial por rango de fechas con exportación a CSV
- **Administrar** — editar y eliminar registros existentes
- **Generar QR** — crea un código QR por vehículo que autocompleta el formulario al escanearlo

---

## 🗂️ Estructura del proyecto

```
sistema-garita/
├── index.html        # Frontend (HTML/CSS/JS puro)
├── main.py           # Backend (FastAPI)
├── requirements.txt  # Dependencias Python
└── Dockerfile        # Imagen Docker del backend
```

---

## 🚀 Instalación y ejecución

### Requisitos
- Docker y Docker Compose
- PostgreSQL (puede usarse como servicio externo o contenedor)

### Variables de entorno

| Variable | Descripción | Ejemplo |
|---|---|---|
| `DATABASE_URL` | URL de conexión a PostgreSQL | `postgresql://user:pass@host:5432/garita` |
| `SECRET_KEY` | Clave secreta para JWT | `mi_clave_secreta` |

### Levantar con Docker

```bash
docker compose up --build
```

El backend queda disponible en `http://localhost:8000`.

---

## 📡 Endpoints del API

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/health` | Estado del servidor |
| `POST` | `/auth/register` | Crear usuario |
| `POST` | `/auth/login` | Iniciar sesión |
| `POST` | `/registros` | Crear registro |
| `GET` | `/registros` | Listar registros (con filtro por fecha) |
| `GET` | `/registros/stats` | Estadísticas del día |
| `PUT` | `/registros/{id}` | Editar registro |
| `DELETE` | `/registros/{id}` | Eliminar registro |

---

## 🔳 Flujo del QR

1. Ir a **Generar QR** e ingresar placa, conductor y motivo
2. Se genera un QR con el formato `PLACA|CONDUCTOR|MOTIVO`
3. En **Registrar**, presionar *Escanear QR*
4. Apuntar la cámara al QR — los campos se autocompletan automáticamente

---

## 🛠️ Tecnologías

**Frontend**
- HTML, CSS y JavaScript puro
- [ZXing](https://github.com/zxing-js/library) — escaneo de QR
- [qrcode.js](https://github.com/soldair/node-qrcode) — generación de QR

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/) + PostgreSQL
- [passlib](https://passlib.readthedocs.io/) + bcrypt — hash de contraseñas
- [python-jose](https://python-jose.readthedocs.io/) — JWT

---

## 👤 Primer usuario

Al no haber interfaz de registro, el primer usuario se crea llamando directamente al endpoint:

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "email": "admin@empresa.com", "password": "tu_password"}'
```
