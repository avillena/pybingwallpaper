"""
Herramienta para generar archivos .qm precompilados a partir de definiciones JSON
Compatible con PyQt5 sin requerir herramientas externas

Uso:
    python translate.py translations   # Usa la carpeta 'translations'
    python translate.py --help         # Muestra ayuda
"""
import os
import json
import struct
import argparse
from pathlib import Path


def create_qm_file(translations, output_file):
    """
    Crea un archivo QM binario simple con las traducciones proporcionadas.
    
    Args:
        translations: Diccionario de traducciones (context::source -> target)
        output_file: Ruta del archivo QM a crear
    """
    with open(output_file, 'wb') as f:
        # Encabezado de archivo QM (magic number)
        f.write(b'\x3C\xB8\x64\x18\x01\x00\x00\x00')
        
        # Para cada traducción, escribir los registros
        for key, translation in translations.items():
            # Separar contexto y texto fuente
            if "::" in key:
                context, source = key.split("::", 1)
            else:
                context, source = "", key
                
            # Escribir contexto
            if context:
                # Longitud y datos del contexto
                context_bytes = context.encode('utf-8')
                f.write(struct.pack('!BI', 1, len(context_bytes)))
                f.write(context_bytes)
                
            # Escribir texto fuente
            source_bytes = source.encode('utf-8')
            f.write(struct.pack('!BI', 2, len(source_bytes)))
            f.write(source_bytes)
            
            # Escribir traducción
            translation_bytes = translation.encode('utf-8')
            f.write(struct.pack('!BI', 3, len(translation_bytes)))
            f.write(translation_bytes)


def load_translations(json_file):
    """Carga traducciones desde un archivo JSON"""
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error al cargar archivo de traducciones {json_file}: {e}")
        return {}


def parse_arguments():
    """Procesa los argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Compilador de traducciones para PyBingWallpaper"
    )
    
    parser.add_argument(
        "translations_dir", 
        nargs="?",
        default="translations",
        help="Directorio donde están los archivos JSON y donde se guardarán los archivos QM (default: translations)"
    )
    
    return parser.parse_args()


def main():
    """Genera archivos QM para cada idioma soportado"""
    args = parse_arguments()
    
    # Preparar rutas
    translations_dir = Path(args.translations_dir)
    
    # Asegurar que el directorio existe
    translations_dir.mkdir(parents=True, exist_ok=True)
    
    # Definir rutas de archivos
    es_json = translations_dir / "translations_es.json"
    en_json = translations_dir / "translations_en.json"
    es_qm = translations_dir / "pybingwallpaper_es.qm"
    en_qm = translations_dir / "pybingwallpaper_en.qm"
    
    print(f"Procesando traducciones en la carpeta: {translations_dir}")
    
    # Procesar traducciones en español
    if es_json.exists():
        print(f"Cargando traducciones en español desde: {es_json}")
        es_translations = load_translations(es_json)
        if es_translations:
            create_qm_file(es_translations, es_qm)
            print(f"✓ Generado archivo QM para español: {es_qm}")
        else:
            print("⚠ Error al cargar traducciones en español")
    else:
        print(f"⚠ No se encontró el archivo de traducciones en español: {es_json}")
    
    # Procesar traducciones en inglés
    if en_json.exists():
        print(f"Cargando traducciones en inglés desde: {en_json}")
        en_translations = load_translations(en_json)
        if en_translations:
            create_qm_file(en_translations, en_qm)
            print(f"✓ Generado archivo QM para inglés: {en_qm}")
        else:
            print("⚠ Error al cargar traducciones en inglés")
    else:
        print(f"⚠ No se encontró el archivo de traducciones en inglés: {en_json}")
    
    print("\n¡Listo! Los archivos QM han sido generados en la misma carpeta que los archivos JSON.")


if __name__ == "__main__":
    main()