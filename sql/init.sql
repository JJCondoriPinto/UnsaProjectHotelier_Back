-- Configuraciones para usuario gerente (en caso tengamos un servicio de db en el compose)

GRANT ALL PRIVILEGES ON fastbooking.* TO 'gerente'@'%';

FLUSH PRIVILEGES;