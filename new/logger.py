# logger.py
import logging
from pathlib import Path
from constants import Constants

class AppLogger:
    """Centraliza el logging de la aplicación."""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Patrón singleton para obtener la instancia del logger."""
        if cls._instance is None:
            cls._instance = AppLogger()
        return cls._instance
    
    def __init__(self):
        """Inicializa el logger."""
        self.logger = logging.getLogger('PyBingWallpaper')
        self.logger.setLevel(logging.INFO)
        
        # Asegura que exista el directorio de logs
        log_file = Constants.get_log_file()
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Handler para archivo
        file_handler = logging.FileHandler(str(log_file))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def info(self, message):
        """Registra un mensaje informativo."""
        self.logger.info(message)
    
    def warning(self, message):
        """Registra una advertencia."""
        self.logger.warning(message)
    
    def error(self, message):
        """Registra un error."""
        self.logger.error(message)
    
    def debug(self, message):
        """Registra un mensaje de depuración."""
        self.logger.debug(message)

# Funciones de conveniencia
def get_logger():
    """Obtiene la instancia del logger."""
    return AppLogger.get_instance()

def log_info(message):
    """Registra un mensaje informativo."""
    get_logger().info(message)

def log_warning(message):
    """Registra una advertencia."""
    get_logger().warning(message)

def log_error(message):
    """Registra un error."""
    get_logger().error(message)

def log_debug(message):
    """Registra un mensaje de depuración."""
    get_logger().debug(message)
