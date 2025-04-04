#!/usr/bin/env python
"""
Script independiente para actualizar los favoritos de PyBingWallpaper.
Lee un archivo TXT con la lista de wallpapers (por ejemplo, "20240906.jpg")
y, para cada uno, utiliza la función de la app para agregarlo a favoritos.
Se muestra metadata estructurada sin barras de progreso animadas.
Al finalizar, abre automáticamente la carpeta de favoritos.
"""

import argparse
import logging
import time
import json
import requests
from pathlib import Path
import sys

from constants import Constants
from core.wallpaper_favorites import add_favorite_by_date, WallpaperFavorites
from utils.resource_utils import open_folder
from utils.wallpaper_utils import build_wallpaper_info_by_date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.logging import RichHandler

# Configuración de consola Rich para salida formateada
console = Console()

def get_wallpaper_metadata(date_str):
    """
    Obtiene la metadata completa del wallpaper para una fecha específica.
    
    Args:
        date_str: La fecha en formato YYYYMMDD o YYYY-MM-DD
        
    Returns:
        dict: Diccionario con toda la metadata disponible para el wallpaper
    """
    formatted_date = date_str
    if '-' not in date_str and len(date_str) == 8:
        formatted_date = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
    
    try:
        # Intentar obtener los metadatos desde el archivo JSON del servicio
        url = Constants.get_archive_url()
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Buscar la imagen correspondiente a la fecha
            for image_data in data:
                if image_data.get("date") == formatted_date:
                    return image_data
        
        return {"date": formatted_date, "title": "Sin título disponible", "description": "Sin descripción disponible"}
    except Exception as e:
        logging.error(f"Error al obtener metadata de wallpaper {date_str}: {str(e)}")
        return {"date": formatted_date, "error": str(e)}

def display_metadata(metadata, date_str, index, total):
    """
    Muestra la metadata del wallpaper en un formato estructurado y visualmente agradable.
    
    Args:
        metadata: Diccionario con la metadata del wallpaper
        date_str: Fecha del wallpaper en formato YYYYMMDD
        index: Índice actual en el proceso
        total: Total de wallpapers a procesar
    """
    # Crear una tabla para la metadata
    metadata_table = Table(box=None, show_header=False, pad_edge=False)
    metadata_table.add_column("Clave", style="yellow")
    metadata_table.add_column("Valor")
    
    # Ordenar las claves para una presentación consistente
    for key in sorted(metadata.keys()):
        if key != "title" and key != "description":
            value = metadata[key]
            # Truncar valores muy largos para mejor visualización
            if isinstance(value, str) and len(value) > 80:
                value = value[:77] + "..."
            metadata_table.add_row(key, str(value))
    
    # Crear texto para el título y descripción
    title = metadata.get("title", "Sin título disponible")
    description = metadata.get("description", "Sin descripción disponible")
    
    # Crear el panel con toda la información
    content = Text()
    content.append(f"📅 Fecha: {date_str}\n", style="bold cyan")
    content.append(f"📷 Título: ", style="bold yellow")
    content.append(f"{title}\n\n", style="bold white")
    content.append(f"📝 Descripción:\n", style="yellow")
    content.append(f"{description}\n\n", style="white")
    content.append("🔵 METADATA:\n", style="bold blue")
    
    # Crear un panel con toda la información
    panel = Panel(
        Group(
            content,
            metadata_table
        ),
        title=f"[bold white]WALLPAPER {index}/{total}[/bold white]",
        border_style="cyan",
        expand=False
    )
    
    console.print(panel)

def add_wallpaper_favorite(date_str, index, total):
    """
    Agrega un wallpaper a favoritos y muestra su metadata estructurada
    
    Args:
        date_str: La fecha en formato YYYYMMDD
        index: Índice actual en el proceso
        total: Total de wallpapers a procesar
    
    Returns:
        bool: True si se agregó correctamente, False en caso contrario
    """
    console.print(f"[cyan]Procesando wallpaper[/cyan] [bold white]{index}/{total}[/bold white]: {date_str}")
    
    try:
        # Obtener la metadata completa
        metadata = get_wallpaper_metadata(date_str)
        
        # Intentar agregar a favoritos
        result = add_favorite_by_date(date_str)
        
        if result:
            console.print(f"[green]✅ Wallpaper {date_str} agregado a favoritos correctamente.[/green]")
            # Mostrar la metadata estructurada
            display_metadata(metadata, date_str, index, total)
        else:
            console.print(f"[red]❌ Error al agregar wallpaper {date_str} a favoritos.[/red]")
        
        return result
    except Exception as e:
        console.print(f"[red]❌ Excepción al procesar {date_str}: {str(e)}[/red]")
        return False

def process_favorites_file(file_path: Path, delay_seconds: float = 1.0):
    """
    Procesa un archivo de lista de wallpapers para agregarlos a favoritos.
    
    Args:
        file_path: Ruta al archivo con la lista
        delay_seconds: Retraso entre descargas para evitar sobrecargar el servidor
    """
    if not file_path.exists():
        console.print(f"[red]El archivo {file_path} no existe.[/red]")
        return

    with file_path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    # Filtrar líneas vacías y extraer fechas de los nombres de archivo
    wallpapers_to_process = []
    for line in lines:
        filename = line.strip()
        if not filename:
            continue
        if not filename.lower().endswith(".jpg"):
            console.print(f"[yellow]El archivo '{filename}' no tiene extensión .jpg. Se omitirá.[/yellow]")
            continue
            
        date_str = filename[:-4]  # Se asume formato "YYYYMMDD.jpg"
        wallpapers_to_process.append(date_str)
    
    total = len(wallpapers_to_process)
    console.print(f"[bold cyan]📋 Procesando {total} wallpapers...[/bold cyan]")
    console.print()
    
    success_count = 0
    error_count = 0
    
    # Procesamiento secuencial con presentación estructurada
    for i, date_str in enumerate(wallpapers_to_process, 1):
        console.rule(f"Progreso: {i}/{total} ({i/total*100:.1f}%)")
        
        if add_wallpaper_favorite(date_str, i, total):
            success_count += 1
        else:
            error_count += 1
        
        console.print()
        
        if delay_seconds > 0 and i < total:
            time.sleep(delay_seconds)  # Evitar sobrecargar el servidor
    
    # Resumen final
    console.rule("[bold green]Proceso Completado[/bold green]")
    console.print(f"[bold]✨ Proceso completado:[/bold] [green]{success_count} exitosos[/green], [red]{error_count} fallidos[/red] de [cyan]{total} total[/cyan].")
    
    # Mostrar sugerencia de verificación visual
    if error_count > 0:
        console.print("[yellow]⚠️  Se recomienda verificar visualmente los wallpapers descargados.[/yellow]")

def main():
    parser = argparse.ArgumentParser(
        description="Actualizador de favoritos para PyBingWallpaper. "
                    "El script recibe un archivo TXT con la lista de wallpapers."
    )
    parser.add_argument("file", help="Ruta al archivo TXT con la lista de wallpapers (ej: wallpapers.txt)")
    parser.add_argument("--delay", type=float, default=1.0, 
                      help="Retraso en segundos entre descargas (default: 1.0)")
    parser.add_argument("--no-open", action="store_true",
                      help="No abrir automáticamente la carpeta de favoritos al finalizar")
    args = parser.parse_args()
    
    # Configurar logging para ser más discreto pero aún útil
    logging.basicConfig(
        level=logging.WARNING,  # Solo mostrar advertencias y errores
        format="%(message)s",
        handlers=[RichHandler(rich_tracebacks=True, show_time=False)]
    )
    
    process_favorites_file(Path(args.file), delay_seconds=args.delay)
    
    # Si no se especificó --no-open, abrimos la carpeta de favoritos
    if not args.no_open:
        favorites_path = Constants.get_favorites_path()
        console.print(f"[cyan]🔍 Abriendo carpeta de favoritos: {favorites_path}[/cyan]")
        if open_folder(favorites_path):
            console.print("[green]✅ Carpeta de favoritos abierta correctamente.[/green]")
        else:
            console.print("[red]❌ No se pudo abrir la carpeta de favoritos automáticamente.[/red]")

if __name__ == "__main__":
    # Importar Group aquí para evitar problemas de dependencias circulares
    from rich.console import Group
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Proceso interrumpido por el usuario.[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Error inesperado:[/bold red] {str(e)}")
        sys.exit(1)
