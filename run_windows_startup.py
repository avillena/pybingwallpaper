import os
import sys
import winreg
from constants import Constants
from logger import log_error

class StartupManager:
    """Gestiona la configuración de inicio con Windows."""
    
    @staticmethod
    def get_run_on_startup():
        """Comprueba si la aplicación está configurada para iniciarse con Windows."""
        try:
            # Abre la clave del registro
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Constants.Windows.REGISTRY_RUN_PATH,
                0, winreg.KEY_READ
            )
            
            # Intenta leer el valor
            try:
                value, _ = winreg.QueryValueEx(key, Constants.APP_NAME)
                winreg.CloseKey(key)
                
                # Verifica que el comando coincida con el comando esperado
                expected_cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" /background'
                return value == expected_cmd
            except Exception:
                winreg.CloseKey(key)
                return False
                
        except Exception as e:
            log_error(f"Error al verificar inicio automático: {str(e)}")
            return False
    
    @staticmethod
    def set_run_on_startup(enable):
        """Configura si la aplicación debe iniciarse con Windows."""
        try:
            # Abre la clave del registro con permisos de escritura
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                Constants.Windows.REGISTRY_RUN_PATH,
                0, winreg.KEY_WRITE
            )
            
            if enable:
                # Define el comando para ejecutar al inicio
                # Usa sys.executable para obtener la ruta del intérprete de Python
                # y sys.argv[0] para obtener la ruta del script actual
                cmd = f'"{sys.executable}" "{os.path.abspath(sys.argv[0])}" /background'
                winreg.SetValueEx(key, Constants.APP_NAME, 0, winreg.REG_SZ, cmd)
            else:
                # Elimina la entrada del registro
                try:
                    winreg.DeleteValue(key, Constants.APP_NAME)
                except Exception:
                    pass  # Si no existe, simplemente ignoramos el error
                    
            winreg.CloseKey(key)
            return True
        except Exception as e:
            log_error(f"Error al configurar el inicio automático: {str(e)}")
            return False