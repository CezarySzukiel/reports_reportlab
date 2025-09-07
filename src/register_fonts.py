
import logging

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from src.fontspec import FontSpec


def register_fonts(fonts: list[FontSpec], *, logger: logging.Logger | None = None) -> None:
    """Register TrueType/OpenType fonts in ReportLab safely and idempotently.

    This function:
    - skips duplicate font names in the input,
    - checks if a font is already registered before re-registering,
    - verifies file existence (in case validation was bypassed),
    - logs warnings and errors appropriately,
    - guarantees that calling it multiple times will not cause conflicts.

    Parameters
    ----------
    fonts:
        Collection of font specifications to register.
    logger:
        Optional logger. If omitted, the module's default logger is used.
    """
    log = logger if logger else logging.getLogger(__name__)
    seen_names: set[str] = set()

    for spec in fonts:
        if spec.name in seen_names:
            log.warning(f"Duplicate font in input: {spec.name} (skipped)")
            continue

        seen_names.add(spec.name)

        try:
            pdfmetrics.getFont(spec.name)
        except KeyError:
            already_registered = False
        else:
            already_registered = True

        if already_registered:
            log.debug(f"Font {spec.name} already registered")
            continue

        try:
            pdfmetrics.registerFont(TTFont(spec.name, spec.file_path.as_posix()))
        except Exception:
            log.exception(f"Failed to register font {spec.name}, {spec.file_path}")
            continue

        log.info("Successfully registered font: %s (%s)", spec.name, spec.file_path)
