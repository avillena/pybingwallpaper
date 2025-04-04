from enum import Enum
from typing import Optional
from models.wallpaper import Wallpaper
from utils.http_client import get_json, download_file
from utils.validation import is_valid_jpeg
import os

class Country(Enum):
    US = "US"
    CA = "CA"
    IT = "IT"
    ES = "ES"
    FR = "FR"
    DE = "DE"
    GB = "GB"
    IN = "IN"
    CN = "CN"
    JP = "JP"
    BR = "BR"
    ROW = "ROW"

class Language(Enum):
    EN = "en"
    IT = "it"
    ES = "es"
    FR = "fr"
    DE = "de"
    JA = "ja"
    PT = "pt"
    ZH = "zh"

class BingService:
    def __init__(self, default_country: Country, default_language: Language) -> None:
        self.default_country = default_country
        self.default_language = default_language

    @property
    def base_url(self) -> str:
        return f"https://bing.npanuhin.me/{self.default_country.value}/{self.default_language.value}"

    def get_wallpaper_by_date(self, date: str) -> Optional[Wallpaper]:
        return self.get_wallpaper(self.default_country, self.default_language, date)

    def download_wallpaper(self, wallpaper: Wallpaper) -> bool:
        return self.download(wallpaper)

    @staticmethod
    def get_wallpaper(country: Country, language: Language, date: str) -> Optional[Wallpaper]:
        base_url = f"https://bing.npanuhin.me/{country.value}/{language.value}"
        metadata = BingService._fetch_metadata(base_url, date)
        if metadata is None:
            return None

        return Wallpaper(
            date=date,
            title=metadata["title"],
            description=metadata["description"],
            url=f"{base_url}/{date}.jpg",
            file_path=f"{date}.jpg",
             country=country,
             language=language
        )

    @staticmethod
    def download(wallpaper: Wallpaper) -> bool:
        if not download_file(wallpaper.url, wallpaper.file_path):
            return False
        if not is_valid_jpeg(wallpaper.file_path):
            os.remove(wallpaper.file_path)
            return False
        return True

    @staticmethod
    def _fetch_metadata(base_url: str, date: str) -> Optional[dict[str, str]]:
        data = get_json(f"{base_url}.json")
        return next((item for item in data if item.get("date") == date), None) if data else None
