/* ----- ISLAS ----- */
INSERT INTO isla (id_isla, nombre) VALUES
 (1,'1.1 Fracciones numéricas'),
 (2,'1.2 Jerarquía de operaciones'),
 (3,'1.3 Leyes de los exponentes'),
 (4,'1.4 Expresiones algebraicas'),
 (5,'1.5 Productos notables'),
 (6,'1.6 Factorización'),
 (7,'1.7 Fracciones algebraicas'),
 (8,'1.8 Solución de ecuaciones'),
 (9,'1.9 Sistemas de ecuaciones lineales'),
 (10,'1.10 Logaritmos: definición y propiedades');

/* ----- TEMAS ----- (inserta los 10 temas según UI) */
INSERT INTO tema (nombre, descripcion) VALUES
 ('Fracciones',              'Operaciones con fracciones numéricas y algebraicas'),
 ('Jerarquía',               'Jerarquía de operaciones'),
 ('Exponentes',              'Leyes y propiedades de los exponentes'),
 ('Expresiones',             'Expresiones algebraicas'),
 ('Productos notables',      'Productos notables y factorización básica'),
 ('Factorización',           'Técnicas de factorización'),
 ('Fracciones algebraicas',  'Operaciones con fracciones algebraicas'),
 ('Ecuaciones',              'Solución de ecuaciones'),
 ('Sistemas lineales',       'Sistemas de ecuaciones lineales'),
 ('Logaritmos',              'Logaritmos: definición y propiedades');

/* ----- ADMIN de prueba (pwd = "admin123") */
INSERT INTO profesor
(nombre, apellido, correo, pwd, rol, activo, campus, titulo)
VALUES
('Ada','Lovelace','admin@demo.mx',
 '$2b$12$aI1II6mlSEhaya9HXEt4qO5D9nj3WyyBF.HaUyf4afBB.eZ.26gzy',
 'admin',1,'Campus Central','M. C.');
