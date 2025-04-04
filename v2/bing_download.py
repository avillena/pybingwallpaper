import logging
import sys
import webbrowser
from datetime import datetime
import argparse
from rich.logging import RichHandler
from rich.console import Console
from rich.table import Table
from services.bing_service import BingService, Country, Language
from models.wallpaper import Wallpaper

# Configuración de logging con RichHandler
FORMAT = "%(message)s"
logging.basicConfig(level=logging.INFO, format=FORMAT, handlers=[RichHandler()])
logger = logging.getLogger("rich")

from rich import print as rich_print

def print_wallpaper(wallpaper: Wallpaper) -> None:
    rich_print(wallpaper)

def parse_args() -> str:
    parser = argparse.ArgumentParser(description="Descarga wallpapers de Bing por fecha.")
    parser.add_argument(
        "date",
        type=str,
        help="Fecha en formato yyyymmdd (ej: 20240101)"
    )
    args = parser.parse_args()

    # Validar formato de fecha
    try:
        return datetime.strptime(args.date, "%Y%m%d").strftime("%Y-%m-%d")
    except ValueError:
        logger.error("Formato de fecha inválido. Use yyyymmdd.")
        sys.exit(1)

def main() -> None:
    date = parse_args()

    service = BingService(default_country=Country.US, default_language=Language.EN)
    wallpaper = service.get_wallpaper_by_date(date)

    if not wallpaper:
        logger.error("No se encontró imagen para la fecha indicada.")
        sys.exit(1)

    print_wallpaper(wallpaper)

    if service.download_wallpaper(wallpaper):
        logger.info(f"Imagen descargada correctamente en {wallpaper.file_path}")
        webbrowser.open(wallpaper.file_path)
    else:
        logger.error("Fallo en la descarga o validación de la imagen.")

if __name__ == "__main__":
    main()
