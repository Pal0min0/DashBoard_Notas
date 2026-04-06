-- ============================================================
--  dashnotas.sql  —  Base de datos completa del proyecto ミク
--  Importar con: mysql -u root -p < dashnotas.sql
-- ============================================================

CREATE DATABASE IF NOT EXISTS `dashnotas`
  CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `dashnotas`;

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

-- ─── TABLA USUARIOS ──────────────────────────────────────────────────────────
DROP TABLE IF EXISTS `usuarios`;
CREATE TABLE `usuarios` (
  `id`       INT          NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(50)  NOT NULL,
  `password` VARCHAR(255) NOT NULL,   -- almacena hash werkzeug o texto plano legacy
  `rol`      ENUM('administrador','docente') DEFAULT 'docente',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Contraseñas en texto plano (legacy) — al registrar nuevos usuarios
-- la app las hashea automáticamente con werkzeug.
INSERT INTO `usuarios` (`username`, `password`, `rol`) VALUES
  ('admin',    'aaa', 'administrador'),
  ('docente1', 'bbb', 'docente');

-- ─── TABLA ESTUDIANTES ───────────────────────────────────────────────────────
DROP TABLE IF EXISTS `estudiantes`;
CREATE TABLE `estudiantes` (
  `id`        INT            NOT NULL AUTO_INCREMENT,
  `nombre`    VARCHAR(100)   DEFAULT NULL,
  `edad`      INT            DEFAULT NULL,
  `carrera`   VARCHAR(50)    DEFAULT NULL,
  `nota1`     DECIMAL(4,2)   DEFAULT NULL,
  `nota2`     DECIMAL(4,2)   DEFAULT NULL,
  `nota3`     DECIMAL(4,2)   DEFAULT NULL,
  `promedio`  DECIMAL(4,2)   DEFAULT NULL,
  `desempeno` VARCHAR(20)    DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO `estudiantes`
  (`nombre`,`edad`,`carrera`,`nota1`,`nota2`,`nota3`,`promedio`,`desempeno`)
VALUES
  ('Paula',  21, 'Fisica',       4.00, 4.50, 3.00, 3.83, 'Bueno'),
  ('Ana',    18, 'Ingenieria',   2.00, 5.00, 3.00, 3.33, 'Regular'),
  ('Maria',  23, 'Ingenieria',   5.00, 4.50, 3.00, 4.17, 'Bueno'),
  ('Luis',   22, 'Matematicas',  2.00, 3.50, 4.00, 3.17, 'Regular'),
  ('Ana',    21, 'Ingenieria',   5.00, 5.00, 5.00, 5.00, 'Excelente'),
  ('Maria',  23, 'Ingenieria',   4.00, 3.00, 3.00, 3.33, 'Regular'),
  ('Ana',    20, 'Fisica',       2.00, 3.00, 3.00, 2.67, 'Deficiente'),
  ('Luis',   20, 'Ingenieria',   4.00, 2.50, 4.00, 3.50, 'Bueno'),
  ('Luis',   23, 'Fisica',       4.00, 3.00, 2.00, 3.00, 'Regular'),
  ('Luis',   22, 'Ingenieria',   3.50, 3.00, 2.00, 2.83, 'Deficiente'),
  ('Ana',    20, 'Fisica',       5.00, 3.00, 2.00, 3.33, 'Regular'),
  ('Carlos', 19, 'Fisica',       4.00, 2.50, 2.00, 2.83, 'Deficiente'),
  ('Luis',   21, 'Fisica',       2.00, 5.00, 5.00, 4.00, 'Bueno'),
  ('Maria',  22, 'Fisica',       5.00, 2.50, 2.00, 3.17, 'Regular'),
  ('Jose',   18, 'Fisica',       4.00, 3.50, 2.00, 3.17, 'Regular'),
  ('Paula',  21, 'Fisica',       5.00, 4.50, 2.00, 3.83, 'Bueno'),
  ('Luis',   22, 'Ingenieria',   2.00, 3.00, 2.00, 2.33, 'Deficiente'),
  ('Maria',  22, 'Matematicas',  5.00, 5.00, 2.00, 4.00, 'Bueno'),
  ('Luis',   20, 'Matematicas',  5.00, 4.50, 5.00, 4.83, 'Excelente'),
  ('Ana',    22, 'Ingenieria',   2.00, 3.00, 4.00, 3.00, 'Regular'),
  ('Ana',    20, 'Fisica',       3.50, 5.00, 2.00, 3.50, 'Bueno'),
  ('Carlos', 20, 'Ingenieria',   2.00, 4.50, 5.00, 3.83, 'Bueno'),
  ('Luis',   23, 'Fisica',       3.50, 2.50, 5.00, 3.67, 'Bueno'),
  ('Ana',    21, 'Ingenieria',   3.50, 5.00, 4.00, 4.17, 'Bueno'),
  ('Carlos', 19, 'Matematicas',  4.00, 3.00, 3.00, 3.33, 'Regular'),
  ('Maria',  18, 'Fisica',       3.50, 3.00, 5.00, 3.83, 'Bueno'),
  ('Carlos', 22, 'Matematicas',  3.50, 4.50, 2.00, 3.33, 'Regular'),
  ('Luis',   21, 'Ingenieria',   2.00, 3.00, 5.00, 3.33, 'Regular'),
  ('Jose',   20, 'Matematicas',  4.00, 3.00, 3.00, 3.33, 'Regular'),
  ('Ana',    19, 'Ingenieria',   3.50, 2.50, 3.00, 3.00, 'Regular'),
  ('Maria',  18, 'Ingenieria',   5.00, 4.50, 4.00, 4.50, 'Excelente'),
  ('Maria',  23, 'Fisica',       2.00, 3.00, 4.00, 3.00, 'Regular'),
  ('Jose',   18, 'Matematicas',  5.00, 3.50, 4.00, 4.17, 'Bueno'),
  ('Ana',    18, 'Matematicas',  5.00, 2.50, 5.00, 4.17, 'Bueno'),
  ('Jose',   20, 'Fisica',       2.00, 2.50, 2.00, 2.17, 'Deficiente'),
  ('Paula',  23, 'Fisica',       5.00, 5.00, 3.00, 4.33, 'Bueno'),
  ('Jose',   18, 'Fisica',       4.00, 3.50, 3.00, 3.50, 'Bueno'),
  ('Ana',    21, 'Fisica',       5.00, 3.50, 5.00, 4.50, 'Excelente'),
  ('Ana',    22, 'Ingenieria',   3.50, 5.00, 2.00, 3.50, 'Bueno'),
  ('Ana',    23, 'Fisica',       3.50, 2.50, 2.00, 2.67, 'Deficiente'),
  ('Luis',   18, 'Fisica',       3.50, 3.50, 4.00, 3.67, 'Bueno'),
  ('Luis',   23, 'Fisica',       3.50, 4.50, 3.00, 3.67, 'Bueno'),
  ('Ana',    22, 'Fisica',       2.00, 5.00, 3.00, 3.33, 'Regular'),
  ('Maria',  21, 'Fisica',       5.00, 5.00, 4.00, 4.67, 'Excelente'),
  ('Paula',  20, 'Matematicas',  2.00, 3.00, 2.00, 2.33, 'Deficiente'),
  ('Ana',    18, 'Fisica',       5.00, 2.50, 2.00, 3.17, 'Regular');
