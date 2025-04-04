from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional, Tuple
from enum import Enum
from rich.panel import Panel
from rich.text import Text


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




@dataclass(frozen=True)
class Wallpaper:
    date: str
    title: str
    description: str
    url: str
    file_path: str
    country: Country
    language: Language

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def __rich__(self) -> Panel:
        lines = []

        for key, value in self.to_dict().items():
            if isinstance(value, Enum):
                value = value.value
            lines.append(f"[bold yellow]{key}[/]: [white]{value}[/]")

        return Panel(Text.from_markup("\n".join(lines)), title="Bing Wallpaper", expand=False)
        
    @property
    def wallpaper_id(self) -> Tuple[str, str, str]:
        """Retorna la tupla identificadora (country, language, date)"""
        return (self.country.value, self.language.value, self.date)
        
    @property
    def filename(self) -> str:
        """Retorna el nombre de archivo formateado según la convención yyyymmdd.jpg"""
        # Convertir YYYY-MM-DD a YYYYMMDD
        date_parts = self.date.split('-')
        if len(date_parts) == 3:
            return f"{''.join(date_parts)}.jpg"
        return f"{self.date}.jpg"
