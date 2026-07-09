-- =========================================================
-- Sistema de Gestión de Biblioteca
-- Base de datos: MySQL
-- =========================================================

CREATE DATABASE IF NOT EXISTS biblioteca
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE biblioteca;

-- ---------------------------------------------------------
-- Tabla: administradores
-- Controla el acceso al sistema
-- ---------------------------------------------------------
CREATE TABLE administradores (
    id_admin        INT AUTO_INCREMENT PRIMARY KEY,
    usuario         VARCHAR(50)  NOT NULL UNIQUE,
    contrasena_hash VARCHAR(255) NOT NULL,
    intentos_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0,
    bloqueado       BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: usuarios (usuarios de la biblioteca)
-- ---------------------------------------------------------
CREATE TABLE usuarios (
    id_usuario      INT AUTO_INCREMENT PRIMARY KEY,
    nombre_completo VARCHAR(150) NOT NULL,
    dui             VARCHAR(10)  NOT NULL UNIQUE,   -- formato: 00000000-0
    correo          VARCHAR(150) NOT NULL UNIQUE,
    telefono        VARCHAR(15)  NOT NULL,
    fecha_registro  DATE NOT NULL DEFAULT (CURRENT_DATE)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: libros (inventario)
-- ---------------------------------------------------------
CREATE TABLE libros (
    isbn                VARCHAR(20)  PRIMARY KEY,
    titulo              VARCHAR(200) NOT NULL,
    autor               VARCHAR(150) NOT NULL,
    editorial           VARCHAR(150),
    anio_publicacion    SMALLINT UNSIGNED,
    categoria           VARCHAR(80)  NOT NULL,
    cantidad_disponible INT UNSIGNED NOT NULL DEFAULT 0,
    estado              ENUM('Disponible', 'No disponible') NOT NULL DEFAULT 'Disponible',

    INDEX idx_titulo (titulo),
    INDEX idx_autor (autor),
    INDEX idx_categoria (categoria)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: prestamos (encabezado del préstamo)
-- ---------------------------------------------------------
CREATE TABLE prestamos (
    codigo_prestamo INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario      INT NOT NULL,
    fecha_prestamo  DATE NOT NULL DEFAULT (CURRENT_DATE),
    fecha_limite    DATE NOT NULL,
    estado          ENUM('Activo', 'Devuelto', 'Vencido') NOT NULL DEFAULT 'Activo',

    CONSTRAINT fk_prestamo_usuario
        FOREIGN KEY (id_usuario) REFERENCES usuarios(id_usuario)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    INDEX idx_prestamo_estado (estado),
    INDEX idx_prestamo_usuario (id_usuario)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Tabla: detalle_prestamo (permite varios libros por préstamo)
-- ---------------------------------------------------------
CREATE TABLE detalle_prestamo (
    id_detalle        INT AUTO_INCREMENT PRIMARY KEY,
    codigo_prestamo   INT NOT NULL,
    isbn_libro        VARCHAR(20) NOT NULL,
    fecha_devolucion  DATE NULL,

    CONSTRAINT fk_detalle_prestamo
        FOREIGN KEY (codigo_prestamo) REFERENCES prestamos(codigo_prestamo)
        ON UPDATE CASCADE
        ON DELETE CASCADE,

    CONSTRAINT fk_detalle_libro
        FOREIGN KEY (isbn_libro) REFERENCES libros(isbn)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,

    -- Evita registrar el mismo libro dos veces dentro del mismo préstamo
    UNIQUE KEY uq_prestamo_libro (codigo_prestamo, isbn_libro)
) ENGINE=InnoDB;

-- =========================================================
-- Notas de diseño
-- =========================================================
-- 1. "detalle_prestamo" separa el encabezado del préstamo (quién,
--    cuándo, estado general) de los libros específicos prestados,
--    permitiendo soportar múltiples libros por préstamo (RF-04).
--
-- 2. La regla de negocio "máximo 3 préstamos activos por usuario"
--    y "no repetir el mismo libro mientras esté activo" NO se
--    modela como restricción de base de datos porque depende de
--    lógica de estado (fechas, "Activo" vs "Devuelto"); esa
--    validación debe implementarse en la capa de controlador
--    (controllers/prestamo_controller.py) antes del INSERT.
--
-- 3. Los reportes de "Préstamos vencidos" pueden calcularse con:
--    SELECT * FROM prestamos
--    WHERE estado = 'Activo' AND fecha_limite < CURDATE();
--
-- 4. Los reportes de "Libros más prestados" pueden calcularse con:
--    SELECT l.isbn, l.titulo, COUNT(*) AS veces_prestado
--    FROM detalle_prestamo dp
--    JOIN libros l ON l.isbn = dp.isbn_libro
--    GROUP BY l.isbn, l.titulo
--    ORDER BY veces_prestado DESC;
-- =========================================================