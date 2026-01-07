from app.core.config import AppConfig
from app.ui.layout import AppLayout


class StreamlitApp:
    """Main application entrypoint."""

    def __init__(self) -> None:
        """Initialize the app."""
        self._config = AppConfig()
        self._layout = AppLayout(self._config)

    def run(self) -> None:
        """Run the Streamlit application."""
        self._layout.configure_page()
        self._layout.render()


def main() -> None:
    """Streamlit execution entrypoint."""
    StreamlitApp().run()


if __name__ == "__main__":
    main()
