# 📚 Sistema de Administración de Biblioteca

Aplicación de consola desarrollada en **Python**, utilizando **Programación Orientada a Objetos (POO)**, el patrón de arquitectura **Modelo-Vista-Controlador (MVC)** y una capa **DAO (Data Access Object)** para la gestión de datos. La información se almacena de forma persistente en una base de datos **MariaDB**.

Este proyecto fue desarrollado con fines académicos para fortalecer conocimientos en diseño de software, arquitectura de aplicaciones y administración de bases de datos.

---

## Objetivos del proyecto

- Aplicar los principios de la Programación Orientada a Objetos.
- Implementar el patrón de arquitectura MVC.
- Separar el acceso a datos mediante el patrón DAO.
- Integrar Python con MariaDB.
- Implementar autenticación utilizando contraseñas cifradas.
- Desarrollar una aplicación modular, escalable y mantenible.

---

## Características

- 🔐 Autenticación de administradores mediante **bcrypt**.
- 📖 Gestión de libros (CRUD).
- 👥 Gestión de usuarios (CRUD).
- 📚 Registro de préstamos.
- 🗄️ Persistencia de datos en MariaDB.
- ⚠️ Manejo de excepciones personalizadas.
- 🧩 Arquitectura modular basada en MVC y DAO.

---

## Tecnologías utilizadas

| Tecnología | Versión |
|------------|----------|
| Python | 3.14.6 |
| MariaDB | 12.3.2 |
| mysql-connector-python | 9.7.0 |
| bcrypt | 5.0.0 |

---

## Arquitectura

El proyecto implementa una arquitectura basada en **Modelo-Vista-Controlador (MVC)** junto con una capa **DAO**, permitiendo separar claramente las responsabilidades de cada componente.

- **Models:** representan las entidades del sistema.
- **Views:** administran la interacción con el usuario mediante la consola.
- **Controllers:** contienen la lógica de negocio y coordinan la comunicación entre vistas y modelos.
- **DAO:** encapsulan todas las operaciones relacionadas con la base de datos.
- **Database:** administra la conexión con MariaDB.
- **Utils:** contiene utilidades y excepciones personalizadas.

---

## Estructura del proyecto

```text
sistema_biblioteca/
├── controllers/          # Controladores del sistema
├── dao/                  # Acceso a datos (DAO)
├── database/             # Conexión con MariaDB
├── models/               # Entidades del sistema
├── sql/                  # Script de creación de la base de datos
├── utils/                # Utilidades y excepciones
├── views/                # Interfaz de consola
├── crear_admin.py        # Creación del administrador inicial
├── main.py               # Punto de entrada de la aplicación
├── requirements.txt
└── README.md
```

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/USUARIO/sistema_biblioteca.git
```

```bash
cd sistema_biblioteca
```

---

### 2. Crear un entorno virtual

Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

### 4. Crear la base de datos

Ejecutar el archivo:

```text
sql/schema.sql
```

en MariaDB para crear la estructura del sistema.

---

### 5. Crear el primer administrador

```bash
python crear_admin.py
```

---

### 6. Ejecutar la aplicación

```bash
python main.py
```

---

## Conceptos aplicados

- Programación Orientada a Objetos (POO).
- Modelo-Vista-Controlador (MVC).
- Data Access Object (DAO).
- Arquitectura por capas.
- Diseño modular.
- Manejo de excepciones.
- Consultas SQL parametrizadas.
- Hash de contraseñas con bcrypt.
- Persistencia de datos con MariaDB.

---

## Requisitos

- Python 3.14 o superior.
- Servidor MariaDB en ejecución.
- Base de datos creada mediante `sql/schema.sql`.

---

## Posibles mejoras futuras

- Exportación de reportes en PDF.
- Sistema de multas por retraso en devoluciones.
- Búsqueda avanzada de libros.
- Historial completo de préstamos por usuario.
- Roles con diferentes niveles de permisos.
- Interfaz gráfica utilizando Tkinter o una aplicación web con Flask.

---

## Autor

**Dominic Alejandro Castillo González**

Estudiante de Técnico en Ingeniería en Computación.

GitHub: https://github.com/Nitolabs

---

## Colaboradores

- **Dominic Alejandro Castillo González** — Desarrollo del proyecto.
- **Nina 🐈** — Supervisión, pruebas informales y apoyo moral.

---

## Licencia

Este proyecto ha sido desarrollado con fines educativos y de aprendizaje.