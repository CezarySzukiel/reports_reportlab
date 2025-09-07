
from pathlib import Path

from reportlab.lib.pagesizes import LETTER

from src.build_pdf import build_pdf
from src.config import ASSETS_PATH, FONTS_PATH, IMAGES_PATH, DocConfig
from src.fontspec import FontSpec

cfg = DocConfig(
    output_path=ASSETS_PATH / Path("report.pdf"),
    pagesize=LETTER,
    fonts=[
        FontSpec(name="Roboto-Light-Italic", file_path=FONTS_PATH / Path("Roboto-Italic.ttf")),
        FontSpec(name="Roboto-Regular", file_path=FONTS_PATH / Path("Roboto.ttf")),
    ],
    override_title_font="Roboto-Light-Italic",
    override_body_font="Roboto-Regular",
    image_max_height_px=250.0,
)

build_pdf(
    config=cfg,
    title="Quarterly Summary",
    body="This document contains the quarterly financial summary for Q3 2025.",
    image_path=IMAGES_PATH / Path("ml_alg.jpg"),
)
