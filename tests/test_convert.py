import os
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from convert_to_webp import ConvertOptions, convert_to_webp, main  # noqa: E402


def test_rgba_png_keeps_transparency(tmp_path):
    src = tmp_path / "alpha.png"
    Image.new("RGBA", (8, 8), (255, 0, 0, 0)).save(src)
    out = tmp_path / "alpha.webp"
    assert convert_to_webp(src, out)
    with Image.open(out) as img:
        assert img.mode == "RGBA"
        assert img.getpixel((0, 0))[3] == 0


def test_la_image_keeps_alpha(tmp_path):
    src = tmp_path / "la.png"
    Image.new("LA", (4, 4), (128, 0)).save(src)
    out = tmp_path / "la.webp"
    assert convert_to_webp(src, out)
    with Image.open(out) as img:
        assert "A" in img.mode


def test_animated_gif_keeps_all_frames(tmp_path):
    src = tmp_path / "anim.gif"
    frames = [Image.new("RGB", (6, 6), color) for color in ("red", "green", "blue")]
    frames[0].save(src, save_all=True, append_images=frames[1:], duration=80, loop=0)
    out = tmp_path / "anim.webp"
    assert convert_to_webp(src, out)
    with Image.open(out) as img:
        assert img.n_frames == 3


def test_exif_orientation_is_applied(tmp_path):
    src = tmp_path / "rotated.jpg"
    exif = Image.Exif()
    exif[0x0112] = 6  # rotate 90° CW on display
    Image.new("RGB", (20, 10), "white").save(src, exif=exif.tobytes())
    out = tmp_path / "rotated.webp"
    assert convert_to_webp(src, out, options=ConvertOptions(keep_metadata=True))
    with Image.open(out) as img:
        assert img.size == (10, 20)


def test_lossless_round_trip_is_exact(tmp_path):
    src = tmp_path / "pixels.png"
    original = Image.new("RGB", (3, 1))
    original.putdata([(10, 20, 30), (40, 50, 60), (70, 80, 90)])
    original.save(src)
    out = tmp_path / "pixels.webp"
    assert convert_to_webp(src, out, options=ConvertOptions(lossless=True))
    with Image.open(out) as img:
        converted = img.convert("RGB")
        assert [converted.getpixel((x, 0)) for x in range(3)] == [original.getpixel((x, 0)) for x in range(3)]


def test_cli_preserves_structure_and_skips_up_to_date(tmp_path, capsys):
    src_dir = tmp_path / "in"
    (src_dir / "sub").mkdir(parents=True)
    Image.new("RGB", (4, 4), "blue").save(src_dir / "a.jpg")
    Image.new("RGB", (4, 4), "green").save(src_dir / "sub" / "b.png")
    (src_dir / "notes.txt").write_text("ignore me")
    out_dir = tmp_path / "out"

    assert main(["-i", str(src_dir), "-o", str(out_dir), "-j", "2"]) == 0
    assert (out_dir / "a.webp").exists()
    assert (out_dir / "sub" / "b.webp").exists()
    assert not (out_dir / "notes.webp").exists()

    capsys.readouterr()
    assert main(["-i", str(src_dir), "-o", str(out_dir)]) == 0
    assert "成功 0, 失败 0, 跳过 2" in capsys.readouterr().out


def test_cli_returns_error_for_missing_input(tmp_path):
    assert main(["-i", str(tmp_path / "missing")]) == 1


def test_cli_reports_failures(tmp_path):
    src_dir = tmp_path / "in"
    src_dir.mkdir()
    (src_dir / "broken.png").write_bytes(b"not an image")
    assert main(["-i", str(src_dir), "-o", str(tmp_path / "out")]) == 1
