@echo off
echo Compilando archivos de traducción...

:: Carpeta donde están los archivos JSON y donde se guardarán los QM
set TRANSLATIONS_DIR=translations

:: Asegurarse de que la carpeta existe
if not exist %TRANSLATIONS_DIR% mkdir %TRANSLATIONS_DIR%

:: Ejecutar el script de Python para generar las traducciones
python translate.py %TRANSLATIONS_DIR%

echo.
echo Puedes ejecutar con una carpeta diferente:
echo python translate.py [carpeta_de_traducciones]

pause