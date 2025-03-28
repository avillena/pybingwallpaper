# Internacionalización de PyBingWallpaper

Este documento explica cómo funciona el sistema de internacionalización (i18n) para PyBingWallpaper.

## Estructura de archivos

- **`translations/`** - Carpeta principal para archivos de traducción
  - **`translations_es.json`** - Traducciones en español (formato JSON)
  - **`translations_en.json`** - Traducciones en inglés (formato JSON)
  - **`pybingwallpaper_es.qm`** - Archivo compilado para español (usado por la app)
  - **`pybingwallpaper_en.qm`** - Archivo compilado para inglés (usado por la app)

## Cómo funciona

1. La aplicación detecta automáticamente el idioma del sistema operativo
2. Si se ejecuta en Windows en español, mostrará la interfaz en español
3. Si se ejecuta en cualquier otro idioma, mostrará la interfaz en inglés
4. Las traducciones se cargan desde los archivos `.qm` compilados

## Cómo modificar traducciones

1. Edita los archivos JSON correspondientes (`translations_es.json` y/o `translations_en.json`)
2. Ejecuta el script de compilación para generar los archivos `.qm` actualizados:

```
python translate.py translations
```

o simplemente:

```
compile_translations.bat
```

## Formato de los archivos JSON

Los archivos JSON siguen este formato:

```json
{
    "Contexto::Texto original": "Texto traducido",
    "BingWallpaperApp::Salir": "Exit"
}
```

Donde:
- **Contexto**: Ayuda a distinguir textos idénticos en diferentes partes de la aplicación
- **Texto original**: El texto en español que aparece en el código
- **Texto traducido**: El texto que se mostrará según el idioma

## Añadir nuevos idiomas

Para añadir un nuevo idioma (por ejemplo, francés):

1. Crea un nuevo archivo JSON (`translations_fr.json`)
2. Copia el contenido de `translations_en.json` y traduce los valores
3. Ejecuta:
   ```
   python translate.py translations
   ```
4. Modifica `app.py` para que detecte y cargue el nuevo idioma

## Notas técnicas

- Este sistema utiliza `QTranslator` de Qt para gestionar las traducciones
- Los archivos `.qm` son un formato binario específico de Qt
- El script `translate.py` genera estos archivos sin necesidad de herramientas externas de Qt