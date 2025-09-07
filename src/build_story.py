import logging
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import cast

from reportlab.lib.styles import ParagraphStyle, StyleSheet1
from reportlab.platypus import Flowable, KeepTogether, Paragraph, Spacer

from src.scale_image import scaled_image_flowable

log = logging.getLogger(__name__)


def _get_style(styles: StyleSheet1, name: str) -> ParagraphStyle:
    """Fetch a ParagraphStyle by name with a precise error message."""
    try:
        return cast(ParagraphStyle, styles[name])
    except KeyError as exc:
        raise KeyError(f"Required style '{name}' not found in stylesheet.") from exc


def build_story(
    *,
    title: str,
    body: str,
    styles: StyleSheet1,
    image_path: Path | None = None,
    image_max_height_px: float | None = None,
    spacing: Mapping[str, float] | None = None,
    prepend: Sequence[Flowable] | None = None,
    append: Sequence[Flowable] | None = None,
    keep_image_with_body: bool = True,
) -> list[Flowable]:
    """Compose a Platypus story (Flowables) in a safe, extensible way.

    Parameters
    ----------
    title
        Document title text (can be empty).
    body
        Main body paragraph text (can be empty).
    styles
        Stylesheet containing at least "Title" and "BodyText" styles.
    image_path
        Optional path to an image; if invalid, image is skipped (and logged).
    image_max_height_px
        Maximum image height (points). Must be > 0 to scale; see `scaled_image_flowable`.
    spacing
        Optional spacing overrides in points: keys: "after_title", "after_body".
        Defaults: after_title=12, after_body=24.
    prepend
        Flowables to insert at the beginning of the story.
    append
        Flowables to append at the end of the story.
    keep_image_with_body
        If True, wraps body+image in `KeepTogether` to avoid orphaned image.

    Returns
    -------
    list[Flowable]
        The composed story.
    """
    sp_after_title = (spacing or {}).get("after_title", 12.0)
    sp_after_body = (spacing or {}).get("after_body", 24.0)

    title_style = _get_style(styles, "Title")
    body_style = _get_style(styles, "BodyText")

    story: list[Flowable] = []

    if prepend:
        story.extend(prepend)

    story.append(Paragraph(title, style=title_style))
    story.append(Spacer(1, sp_after_title))

    body_flowable: list[Flowable] = [Paragraph(body, style=body_style), Spacer(1, sp_after_body)]

    img_block: list[Flowable] = []

    if image_path is not None:
        img = scaled_image_flowable(image_path, max_height=image_max_height_px or 100)
        if img is not None:
            img_block.append(img)
        else:
            log.warning("Image skipped (unavailable or invalid): %s", image_path)

    if keep_image_with_body and img_block:
        story.append(KeepTogether(body_flowable + img_block))
    else:
        story.extend(body_flowable)
        story.extend(img_block)

    if append:
        story.extend(append)

    return story