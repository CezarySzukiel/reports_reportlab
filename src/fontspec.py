from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FontSpec(BaseModel):
    """Specification of a TrueType/OpenType font to be registered in ReportLab.

    The model is immutable (``frozen``) and validates the given font path:
    it ensures that the file exists, is a regular file, and has one of the
    supported extensions (``.ttf``, ``.otf``, ``.ttc``). The path is also
    normalized (via ``expanduser()`` and ``resolve()``) to avoid ambiguity
    across CI/CD environments and different platforms.

    Example
    -------
    ```python
    from pathlib import Path

    spec = FontSpec(
        name="Roboto-Light-Italic",
        file_path=Path("./fonts/Roboto-LightItalic.ttf"),
    )
    # spec.file_path is now absolute and validated
    ```
    """

    model_config = ConfigDict(
        frozen=True,  # dzięki temu obiekty są niemutowalne
        extra="forbid",  # dzięki temu nie można dodać dodatkowych pól
    )

    _ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".ttf", ".otf", ".ttc"}

    name: str = Field(
        ...,
        min_length=5,
        title="Font name",
        description=(
            "Logical name under which the font will be registered in ReportLab "
            "and later used in styles (e.g. in ``style.fontName``)."
        ),
        examples=["Roboto-Light-Italic", "Inter-Regular"],
    )

    file_path: Path = Field(
        ...,
        title="Font file path",
        description=(
            "Path to a valid .ttf/.otf/.ttc file. The path will be normalized "
            "to an absolute path and validated for existence and extension."
        ),
        examples=[Path("./fonts/Roboto-LightItalic.ttf")],
    )

    @field_validator("file_path")
    @classmethod
    def _validate_and_normalize_path(cls, v: Path) -> Path:
        """Normalize and validate the font path.

        Steps performed:
        - Expands ``~`` (home directory) and resolves to an absolute path.
        - Verifies that the file exists and is a regular file.
        - Ensures that the extension is one of the allowed values
          (``.ttf``, ``.otf``, ``.ttc``).

        Args:
            v: The raw path provided by the user.

        Returns:
            A validated and normalized absolute path.

        Raises:
            ValueError: If the file does not exist, is not a file, or has
            an unsupported extension.
        """
        normalized = v.expanduser().resolve()  # v - obiekt klasy Path, expanduser() rozwija ~ do katalogu domowego

        if not normalized.exists():  # sprawdzenie czy ścieżka istnieje
            raise ValueError(f"Font file does not exist: {normalized}")
        if not normalized.is_file():  # sprawdzenie czy ścieżka jest plikiem
            raise ValueError(f"Path is not a file: {normalized}")

        ext = normalized.suffix.lower()  # zamienia rozszerzenie na małe litery
        if ext not in cls._ALLOWED_EXTS:  # sprawdzenie czy rozszerzenie jest dozwolone
            raise ValueError(f"Unsupported font extension '{ext}'. Allowed: {sorted(cls._ALLOWED_EXTS)}")

        return normalized
