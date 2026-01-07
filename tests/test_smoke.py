def test_smoke_imports() -> None:
    """Ensure core modules import correctly."""
    from app.main import StreamlitApp  # noqa: F401
