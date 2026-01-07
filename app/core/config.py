from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AppConfig:
    """Hold application configuration values."""

    app_title: str = "MP3 Cutter"
    app_icon: str = "🎧"
    page_layout: str = "wide"

    temp_dir_name: str = ".tmp"
    max_upload_mb: int = 200

    def temp_dir(self) -> Path:
        """Return the temp directory path for runtime files."""
        return Path(self.temp_dir_name)
