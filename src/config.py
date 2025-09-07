
from collections.abc import Sequence
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field, PositiveFloat
from reportlab.lib.pagesizes import A4

from src.fontspec import FontSpec

# __file__ - globals z python w tym przypadku to nazwa pliku, parent to directory

ASSETS_PATH: Final = Path(__file__).parent.parent / "assets"
FONTS_PATH: Final = Path(__file__).parent.parent / "fonts"
IMAGES_PATH: Final = Path(__file__).parent.parent / "images"


class DocConfig(BaseModel):
    """Configuration model for PDF document generation.

    This model is immutable, strictly validated and forbids extra fields.
    It defines output location, page layout, fonts, and style overrides.

    Attributes
    ----------
    output_path : Path
        Destination file for the generated PDF. Parent directories will be created.
    pagesize : tuple[float, float]
        Page size in points, defaults to A4. Can be replaced with `LETTER`, `landscape(A4)`, etc.
    fonts : Sequence[FontSpec]
        Fonts to register before rendering the document. Each font is validated.
    override_title_font : str | None
        Optional font name to override the "Title" style.
    override_body_font : str | None
        Optional font name to override the "BodyText" style.
    image_max_height_px : PositiveFloat
        Maximum height of inline images (Platypus flowables). Must be > 0.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    output_path: Path = Field(
        ...,
        description="Destination file for the generated PDF.",
        examples=[Path("pdf/output.pdf")],
    )

    pagesize: tuple[float, float] = Field(
        default=A4,
        description="Page size in points (width, height). Defaults to A4.",
    )

    fonts: Sequence[FontSpec] = Field(
        default_factory=tuple,
        description="Fonts to register before rendering the document.",
    )

    override_title_font: str | None = Field(
        default=None,
        description="Optional font name to override the 'Title' style.",
        examples=["Roboto-Bold", "Inter-Regular"],
    )

    override_body_font: str | None = Field(
        default=None,
        description="Optional font name to override the 'BodyText' style.",
        examples=["Roboto-Italic"],
    )

    image_max_height_px: PositiveFloat = Field(
        default=300.0,
        description="Maximum image height in points. Must be > 0.",
        examples=[200.0, 400.0],
    )
