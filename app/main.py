from app.core.config import AppConfig
from app.ui.layout import AppLayout


class StreamlitApp:
    """Main application entrypoint."""

    def __init__(self) -> None:
        """Initialize the app with config and layout."""
        self._config = AppConfig()
        self._layout = AppLayout(self._config)

    def run(self) -> None:
        """Run the Streamlit application."""
        self._layout.configure_page()
        self._layout.render_header()
        self._layout.render_placeholder()


def main() -> None:
    """CLI-friendly entrypoint for Streamlit execution."""
    StreamlitApp().run()


if __name__ == "__main__":
    main()
