from typing import Optional, Any
import requests

def get_json(url: str, timeout: int = 10) -> Optional[Any]:
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None

def download_file(url: str, output_path: str, timeout: int = 10) -> bool:
    try:
        response = requests.get(url, stream=True, timeout=timeout)
        response.raise_for_status()

        with open(output_path, "wb") as file:
            for chunk in response.iter_content(8192):
                if chunk:
                    file.write(chunk)
        return True
    except requests.RequestException:
        return False
