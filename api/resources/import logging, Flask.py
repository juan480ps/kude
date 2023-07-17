import logging

# Configurar el logger de la aplicación Python
logger = logging.getLogger('myapp')
logger.setLevel(logging.INFO)

# Configurar el controlador FileHandler
file_handler = logging.FileHandler('/var/log/nginx/access.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

# Agregar el controlador al logger de la aplicación Python
logger.addHandler(file_handler)

# Utilizar el logger en tu aplicación Python
logger.info('Registro de ejemplo')
