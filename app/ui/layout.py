import streamlit as st

from app.core.config import AppConfig


class AppLayout:
    """Render the Streamlit UI layout."""

    def __init__(self, config: AppConfig) -> None:
        """Initialize the layout with configuration."""
        self._config = config

    def configure_page(self) -> None:
        """Configure Streamlit page settings."""
        st.set_page_config(
            page_title=self._config.app_title,
            page_icon=self._config.app_icon,
            layout=self._config.page_layout,
        )

    def render_header(self) -> None:
        """Render the main header and short description."""
        st.title(f"{self._config.app_icon} {self._config.app_title}")
        st.caption("Upload audio files and cut them into MP3 chunks (coming next).")

    def render_placeholder(self) -> None:
        """Render placeholder UI elements for future features."""
        st.info("UI ready. Next step: file upload + audio processing pipeline.")
        st.button("Cut audio (disabled)", disabled=True)
