# ミク Dashboard — Instrucciones de instalación

## 📁 Estructura de carpetas

```
mikudash/
│
├── app.py                  ← Flask principal (punto de entrada)
├── database.py             ← Conexión MySQL y funciones CRUD
├── dashprincipal.py        ← Dashboard Dash integrado en Flask
├── dashnotas.sql           ← Base de datos completa
├── requirements.txt        ← Dependencias Python
│
├── templates/
│   ├── login.html          ← Pantalla de login (estilo Miku ✨)
│   └── register.html       ← Pantalla de registro
│
└── static/
    ├── sounds/
    │   └── mikudayo_notification.mp3   ← Sonido (colócalo aquí)
    └── img/
        └── miku-bg.png                 ← Imagen de fondo (colócala aquí)
```

---

## 🐍 1. Crear entorno virtual e instalar dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Mac / Linux)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🗄️ 2. Configurar MySQL

1. Abre phpMyAdmin o la terminal MySQL.
2. Importa el archivo `dashnotas.sql`:

```bash
# Desde terminal (si tienes MySQL en PATH)
mysql -u root -p < dashnotas.sql

# O desde phpMyAdmin: Importar → selecciona dashnotas.sql
```

3. Si tu MySQL tiene contraseña, edita `database.py`:

```python
def conectar():
    conexion = mysql.connector.connect(
        host="localhost",
        user="root",
        password="TU_CONTRASEÑA_AQUI",   # ← aquí
        database="dashnotas"
    )
```

---

## 🎵 3. Agregar archivos estáticos (opcionales)

- Copia `mikudayo_notification.mp3` → `static/sounds/`
- Copia tu imagen de Miku → `static/img/miku-bg.png`

Si no existen, la app funciona igual (sin sonido ni imagen de fondo).

---

## 🚀 4. Ejecutar la app

```bash
python app.py
```

Abre el navegador en: **http://localhost:5000**

---

## 👤 Usuarios por defecto

| Usuario   | Contraseña | Rol           |
|-----------|-----------|---------------|
| admin     | aaa       | administrador |
| docente1  | bbb       | docente       |

También puedes registrar nuevos usuarios desde `/register`.

---

## ✨ Funcionalidades

- **Login / Registro / Logout** con sesiones Flask
- **Dashboard Dash** con filtros interactivos (carrera, edad, promedio)
- **KPIs**: promedio, total estudiantes, nota máxima
- **Tabla interactiva** con filtro, ordenamiento y selección múltiple
- **Gráficos**: Histograma, Dispersión con trendline, Pie de desempeño, Barras por carrera
- **Análisis detallado** al seleccionar filas de la tabla
- **Agregar estudiantes** directamente desde el dashboard
- **Eliminar estudiantes** seleccionando filas y haciendo clic en eliminar
- **Efecto Miku** en login: clic en el fondo → animación + sonido 🎤
