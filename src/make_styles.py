import copy
import logging
from collections.abc import Mapping, MutableMapping
from typing import cast

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle, StyleSheet1, getSampleStyleSheet

log = logging.getLogger(__name__)

ALLOWED_ALIGNMENTS = {TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY}

_ALLOWED_ATTRS: dict[str, tuple[type, ...]] = {
    "fontName": (str,),
    "fontSize": (int, float),
    "leading": (int, float),
    "textColor": (colors.Color, str),
    "backColor": (colors.Color, str),
    "alignment": (int,),
    "spaceBefore": (int, float),
    "spaceAfter": (int, float),
    "leftIndent": (int, float),
    "rightIndent": (int, float),
    "firstLineIndent": (int, float),
    "wordWrap": (str,),
    "kerning": (int, float),
    "tracking": (int, float),
    "underlineWidth": (int, float),
    "underlineOffset": (int, float),
}


def make_styles(
    *,
    base: StyleSheet1 | None = None,
    overrides: Mapping[str, Mapping[str, object]],
    create_missing: bool = True,
    parent_for_new: str = "Normal",
) -> StyleSheet1:
    """Return a **new** stylesheet with arbitrary style overrides applied.

    Parameters
    ----------
    base
        Stylesheet to clone. If ``None``, uses ReportLab's default via
        :func:`getSampleStyleSheet`.
    overrides
        Mapping of ``style_name -> {attribute -> value}``.
        Supported attributes are whitelisted (see ``_ALLOWED_ATTRS``).
        Examples:
            ``{"Title": {"fontName": "Inter-Bold", "fontSize": 20, "leading": 24}}``
            ``{"BodyText": {"textColor": "#222222", "alignment": TA_JUSTIFY}}``
    create_missing
        If ``True``, missing styles will be created inheriting from ``parent_for_new``.
        If ``False``, missing styles are skipped with a warning.
    parent_for_new
        Name of an existing style used as the parent for newly created styles.

    Returns
    -------
    StyleSheet1
        A **new** stylesheet instance with overrides applied.

    Notes
    -----
    - Unknown attributes are ignored with a warning.
    - Values equal to the current style setting are skipped (idempotent).
    - Color strings are parsed as hex (e.g., ``"#112233"``) using ``colors.HexColor``.
    - ``alignment`` must be one of ``TA_LEFT``, ``TA_RIGHT``, ``TA_CENTER``, ``TA_JUSTIFY``.
    """
    styles_in = base if base else getSampleStyleSheet()
    styles = _clone_stylesheet(styles_in)

    if not overrides:
        return styles

    for style_name, attrs in overrides.items():
        if style_name not in styles.byName:
            if not create_missing:
                log.warning("Style '%s' not found; skipping overrides.", style_name)
                continue
            try:
                parent: ParagraphStyle = cast(ParagraphStyle, styles[parent_for_new])  # may raise KeyError
            except KeyError:
                raise KeyError(
                    f"Parent style '{parent_for_new}' not found; cannot create new style '{style_name}'."
                ) from None
            new_style = ParagraphStyle(style_name, parent=parent)
            styles.add(new_style)
            log.info("Created new style '%s' inheriting from '%s'.", style_name, parent_for_new)

        style: ParagraphStyle = cast(ParagraphStyle, styles[style_name])
        _apply_style_overrides(style, attrs)

    return styles


def _clone_stylesheet(ss: StyleSheet1) -> StyleSheet1:
    """Deep-clone a StyleSheet1, preserving byName registry."""
    clone: StyleSheet1 = copy.deepcopy(ss)
    assert isinstance(clone.byName, MutableMapping)  # noqa: S101,0
    return clone


def _apply_style_overrides(style: ParagraphStyle, attrs: Mapping[str, object]) -> None:
    """Apply validated overrides to a ParagraphStyle in-place."""
    for key, raw_val in attrs.items():
        if key not in _ALLOWED_ATTRS:
            log.warning("Attribute '%s' is not allowed; skipping for style '%s'.", key, style.name)
            continue

        value = _normalize_value(key, raw_val)
        expected_types = _ALLOWED_ATTRS[key]
        if not isinstance(value, expected_types):
            log.warning(
                "Attribute '%s' has invalid type %s (expected %s); skipping for style '%s'.",
                key,
                type(value).__name__,
                "/".join(t.__name__ for t in expected_types),
                style.name,
            )
            continue
        if key == "alignment" and isinstance(value, int) and value not in ALLOWED_ALIGNMENTS:
            log.warning("Alignment value '%s' not allowed; skipping for style '%s'.", value, style.name)
            continue

        current = getattr(style, key, None)
        if current == value:
            log.debug("Style '%s': '%s' already set to %r; skipping.", style.name, key, value)
            continue

        setattr(style, key, value)
        log.info("Style '%s': set '%s' from %r to %r.", style.name, key, current, value)


def _normalize_value(key: str, value: object) -> object:
    """Coerce friendly inputs into ReportLab-friendly objects."""
    if value is None:
        return value
    if key in {"textColor", "backColor"} and isinstance(value, str):
        hex_str = value if value.startswith("#") else f"#{value}"
        try:
            return colors.HexColor(hex_str)
        except Exception:
            return value
    return value
