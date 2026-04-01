import os
from dotenv import load_dotenv, dotenv_values

load_dotenv()


class Config:
    # Fixed framework settings (not from .env)
    SCREENSHOT_DIR = "reports/screenshots"
    REPORT_DIR     = "reports/html"
    VIDEO_DIR      = "reports/videos"

    # Typed shortcuts for commonly used keys
    @property
    def BASE_URL(self):   return os.getenv("BASE_URL", "http://localhost")
    @property
    def USERNAME(self):   return os.getenv("USERNAME", "")
    @property
    def PASSWORD(self):   return os.getenv("PASSWORD", "")
    @property
    def BROWSER(self):    return os.getenv("BROWSER", "chromium")
    @property
    def HEADLESS(self):   return os.getenv("HEADLESS", "false").lower() == "true"
    @property
    def SLOW_MO(self):    return int(os.getenv("SLOW_MO", "0"))

    def __getattr__(self, name: str) -> str:
        """Auto-resolve any .env key by attribute name (case-insensitive fallback)."""
        # Try exact name first, then uppercase
        value = os.getenv(name) or os.getenv(name.upper())
        if value is not None:
            return value
        raise AttributeError(
            f"'Config' has no attribute '{name}' and no matching .env key was found."
        )


config = Config()
