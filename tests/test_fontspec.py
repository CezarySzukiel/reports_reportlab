from pathlib import Path

import pytest

from src.fontspec import FontSpec


def test_valid_font_path_is_normalized(tmp_path: Path) -> None:
    """FontSpec should accept a valid .ttf file and normalize the path."""
    font_file = tmp_path / "Font.ttf"
    font_file.write_bytes(b"dummy value")
    font_spec = FontSpec(
        name="dummy name",
        file_path=font_file,
    )

    assert font_spec.file_path.is_absolute()
    assert font_spec.file_path == font_file.resolve()
    assert font_spec.name == "dummy name"


def test_fontspec_rejects_missing_file(tmp_path: Path) -> None:
    """Nonexistent font files should raise ValueError."""
    font_file = tmp_path / "Font.ttf"
    with pytest.raises(ValueError, match="Font file does not exist:*"):
        FontSpec(
            name="dummy name",
            file_path=font_file,
        )


def test_fontspec_rejects_non_file(tmp_path: Path) -> None:
    """Directories instead of files should raise ValueError."""
    font_file = tmp_path / "some_dir"
    font_file.mkdir()

    with pytest.raises(ValueError, match="Font path is not a file:*"):
        FontSpec(
            name="dummy name",
            file_path=font_file,
        )


@pytest.mark.parametrize("ext", [".txt", ".woff", ".data"])
def test_fontspec_rejects_invalid_extension(tmp_path: Path, ext: str) -> None:
    """Only .ttf, .otf, .ttc extensions are allowed."""
    font_file = tmp_path / f"Font{ext}"
    font_file.write_bytes(b"dummy value")

    with pytest.raises(ValueError, match=f"Unsupported font extension '{ext}'*"):
        FontSpec(
            name="dummy name",
            file_path=font_file,
        )


def test_expanduser_and_resolve(tmp_path: Path, monkeypatch) -> None:
    """~ in path should expand to home directory and resolve to absolute."""
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    font_file = fake_home / "Font.otf"
    font_file.write_bytes(b"dummy")

    monkeypatch.setenv("HOME", str(fake_home))

    spec = FontSpec(name="ExpandTest", file_path=Path("~/Font.otf"))
    assert spec.file_path == font_file.resolve()
