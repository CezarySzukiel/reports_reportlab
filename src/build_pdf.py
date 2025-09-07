import logging
from collections.abc import Sequence
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.platypus import Flowable, SimpleDocTemplate

from src.build_story import build_story
from src.config import DocConfig
from src.make_styles import make_styles
from src.register_fonts import register_fonts

log = logging.getLogger(__name__)


def build_pdf(
    *,
    config: DocConfig,
    title: str,
    body: str,
    image_path: Path | None = None,
    extra_flowables_before: Sequence[Flowable] | None = None,
    extra_flowables_after: Sequence[Flowable] | None = None,
) -> Path:
    """Build a PDF file using the provided configuration.

    Parameters
    ----------
    config
        Document configuration (output_path, pagesize, fonts, style overrides, etc.).
    title
        Title paragraph text.
    body
        Body paragraph text.
    image_path
        Optional image path; silently skipped if not usable.
    extra_flowables_before
        Additional flowables to prepend to the story.
    extra_flowables_after
        Additional flowables to append to the story.

    Returns
    -------
    Path
        The path to the generated PDF.

    Raises
    ------
    RuntimeError
        If ReportLab fails to build the document.
    """

    out_dir = config.output_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)
    log.debug("Ensured output directory exists: %s", out_dir)

    register_fonts(config.fonts)
    styles = make_styles(
        overrides={
            "Title": {"fontName": config.override_title_font} if config.override_title_font else {},
            "BodyText": {"fontName": config.override_body_font} if config.override_body_font else {},
        }
    )
    story = build_story(
        title=title,
        body=body,
        styles=styles,
        image_path=image_path,
        image_max_height_px=float(config.image_max_height_px),
        prepend=list(extra_flowables_before or []),
        append=list(extra_flowables_after or []),
    )
    doc = SimpleDocTemplate(str(config.output_path), pagesize=config.pagesize or A4)
    try:
        doc.build(story)
    except Exception as exc:
        log.exception("Failed to build PDF at %s", config.output_path)
        raise RuntimeError(f"Failed to build PDF: {config.output_path}") from exc

    log.info("PDF generated: %s", config.output_path)
    return config.output_path