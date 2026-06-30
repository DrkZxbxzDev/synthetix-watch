
# 🔍 Synthetix Watch

API de monitoreo automatizado para sitios web. Verifica disponibilidad, tiempos de respuesta y la presencia de elementos clave en una página usando Playwright para simular un navegador real. Incluye scheduler en background, capturas de pantalla como evidencia y dashboard con estadísticas de uptime.

Proyecto de portafolio — Sebastián Rodríguez

---

## ✨ Funcionalidades

- 🌐 Monitoreo de múltiples URLs registradas como targets
- ⚡ Verificación de código de estado HTTP y tiempo de respuesta
- 🔎 Validación de selectores CSS esperados (assertion de QA)
- 📸 Captura de pantalla automática como evidencia en cada check
- ⏱️ Scheduler en background — checks automáticos cada 5 minutos
- 📊 Dashboard con uptime %, último estado y tiempos por target
- 🛠️ Endpoints para checks manuales y control del scheduler
- 💾 Persistencia en base de datos SQLite async

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|---|---|
| Framework | FastAPI |
| Automatización | Playwright |
| Base de datos | SQLAlchemy async + aiosqlite |
| Scheduler | APScheduler |
| Configuración | Pydantic Settings |
| Lenguaje | Python 3.10+ |

---

## 🚀 Instalación y uso

```bash
# 1. Clonar el repositorio
git clone https://github.com/DrkZxbxzDev/synthetix-watch.git
cd synthetix-watch

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate       # Linux / macOS
.venv\Scripts\activate          # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Instalar navegador de Playwright
playwright install chromium
```

Crea un archivo `.env` en la raíz del proyecto:

```env
PROJECT_NAME=Synthetix Watch API
DATABASE_URL=sqlite+aiosqlite:///./synthetix_watch.db
SCREENSHOT_DIR=screenshots
```

Levanta el servidor:

```bash
uvicorn main:app --reload
```

Documentación interactiva disponible en `http://127.0.0.1:8000/docs`

---

## 📡 Endpoints principales

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/targets` | Lista todos los targets |
| `POST` | `/targets` | Registra un nuevo target |
| `PATCH` | `/targets/{id}` | Edita un target |
| `DELETE` | `/targets/{id}` | Elimina un target |
| `POST` | `/targets/{id}/check` | Ejecuta un check manual |
| `GET` | `/targets/{id}/results` | Historial de resultados |
| `GET` | `/dashboard` | Resumen general con uptime % |
| `GET` | `/scheduler/status` | Estado del scheduler |
| `POST` | `/scheduler/run-now` | Fuerza todos los checks ahora |

---

## 📁 Estructura del proyecto

```
synthetix-watch/
├── app/
│   ├── api/
│   │   └── endpoints.py       # Todos los endpoints de la API
│   ├── core/
│   │   ├── config.py          # Configuración vía .env
│   │   └── scheduler.py       # Checks automáticos periódicos
│   ├── database/
│   │   ├── connection.py      # Engine y sesión async
│   │   └── models.py          # Modelos MonitorTarget y MonitorResult
│   └── services/
│       └── monitor.py         # Lógica de verificación con Playwright
├── screenshots/               # Capturas generadas en cada check
├── .env                       # Variables de entorno (no se sube a git)
├── main.py                    # Punto de entrada
└── requirements.txt
```

---

## 📈 Roadmap

- [x] CRUD de targets
- [x] Check manual por endpoint
- [x] Scheduler automático en background
- [x] Captura de pantalla como evidencia
- [x] Dashboard con uptime %
- [ ] Notificaciones por email al detectar caída
- [ ] Soporte para autenticación en páginas protegidas
- [ ] Frontend visual para el dashboard

---

## 📄 Licencia

MIT — Libre para usar, modificar y aprender.

---

Made with ❤️ by Sebastián Rodríguez
```