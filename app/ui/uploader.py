import streamlit as st

from app.core.file_storage import TempFileStorage


class FileUploader:
    """Render and manage the file upload UI."""

    def __init__(self, storage: TempFileStorage) -> None:
        """Initialize uploader with storage backend."""
        self._storage = storage

    def render(self) -> None:
        """Render file uploader component."""
        uploaded_file = st.file_uploader(
            label="Upload an audio file",
            type=None,
            accept_multiple_files=False,
        )

        if uploaded_file is None:
            return

        file_path = self._storage.save(
            filename=uploaded_file.name,
            content=uploaded_file.read(),
        )

        st.success("File uploaded successfully")
        st.write(
            {
                "original_name": uploaded_file.name,
                "stored_path": str(file_path),
                "size_bytes": file_path.stat().st_size,
            }
        )
