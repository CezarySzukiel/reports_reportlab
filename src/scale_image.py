import logging
from pathlib import Path

from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image

log = logging.logger(__name__)


def scaled_image_flowable(img_path: Path, *, max_height: float, upscale: bool = False) -> Image | None:
    """Create a Platypus ``Image`` flowable scaled to a maximum height.

    The aspect ratio is preserved. Returns ``None`` if the image
    cannot be loaded.

    Parameters
    ----------
    img_path:
        Path to the image file.
    max_height:
        Maximum height of the flowable in points. Must be > 0.
    upscale:
        If ``False`` (default), images shorter than ``max_height`` will keep
        their original size. If ``True``, they will be upscaled.

    Returns
    -------
    Image | None
        A Platypus ``Image`` flowable or ``None`` if the file is missing or invalid.

    Notes
    -----
    - The function catches and logs any exception raised by
      :class:`reportlab.lib.utils.ImageReader`.
    - ``max_height`` is validated; if invalid, the function logs an error
      and returns ``None``.
    """
    if max_height <= 0:
        log.error("Invalid max_height=%s; must be > 0.", max_height)
        return None

    if not img_path.exists():
        log.warning("Image file not found: %s", img_path)
        return None
    try:
        img = ImageReader(img_path.as_posix())
        iw, ih = img.getSize()
    except Exception as exc:
        log.exception("Failed to read image metadata for %s: %s", img_path, exc)
        return None

    if iw <= 0 or ih <= 0:
        log.error("Invalid image dimensions for %s: width=%s, height=%s", img_path, iw, ih)
        return None

    if not upscale and ih < max_height:
        scale = 1.0
    else:
        scale = max_height / float(ih)
    new_width = iw * scale
    new_height = ih * scale

    log.debug(
        "Creating Image flowable for %s scaled %.2fx (orig=%dx%d, new=%.1fx%.1f).",
        img_path,
        scale,
        iw,
        ih,
        new_width,
        new_height,
    )

    return Image(img_path.as_posix(), width=new_width, height=new_height)
