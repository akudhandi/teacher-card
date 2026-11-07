"""CLI tests for list / generate / gallery."""

import cli


def test_cli_list(capsys):
    assert cli.main(["list"]) == 0
    out = capsys.readouterr().out
    assert "us" in out and "teacher_id" in out


def test_cli_generate_pdf(tmp_path):
    out_dir = tmp_path / "out"
    rc = cli.main([
        "generate", "--country", "us", "--format", "pdf",
        "--document-types", "teacher_id", "--out", str(out_dir),
    ])
    assert rc == 0
    files = list(out_dir.glob("*.pdf"))
    assert len(files) == 1
    assert files[0].read_bytes()[:5] == b"%PDF-"


def test_cli_generate_is_reproducible(tmp_path):
    args = [
        "generate", "--country", "us", "--document-types", "teacher_id",
        "--seed", "42",
    ]
    a = tmp_path / "a"
    b = tmp_path / "b"
    cli.main(args + ["--out", str(a)])
    cli.main(args + ["--out", str(b)])
    fa = next(a.glob("*.png")).read_bytes()
    fb = next(b.glob("*.png")).read_bytes()
    assert fa == fb


def test_cli_gallery_builds_index(tmp_path):
    out_dir = tmp_path / "gallery"
    rc = cli.main(["gallery", "--out", str(out_dir)])
    assert rc == 0
    index = out_dir / "index.html"
    assert index.exists()
    html = index.read_text(encoding="utf-8")
    assert "Yowes demo gallery" in html
    assert "teaching_license" in html or "teacher_id" in html