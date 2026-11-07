"""Command-line interface for the Yowes document generator.

Examples:
    yowes-cli list
    yowes-cli generate --country us --format pdf
    yowes-cli generate --country uk --first Jane --last Doe --seed 1234
    yowes-cli gallery --out docs/demo
"""

import argparse
import sys
from pathlib import Path

from countries import get_country, list_countries
from countries.fixtures import get_persona
from countries.utils import clear_photo_cache, format_extension

BASE_DIR = Path(__file__).parent


def _resolve_school(gen, school_name):
    if school_name:
        school = gen.search_school(school_name)
        if school is None:
            names = ", ".join(s["name"] for s in gen.schools)
            raise SystemExit(f"School '{school_name}' not found. Available: {names}")
        return school
    if not gen.schools:
        raise SystemExit(f"No schools defined for '{gen.get_country_code()}'.")
    return gen.schools[0]


def _generate_one(gen, dtype, person, school, args):
    return gen.generate_document_seeded(
        doc_type=dtype,
        first=person["first"],
        last=person["last"],
        school=school,
        position=person["position"],
        dob=person["dob"],
        seed=args.seed,
        watermark=not args.no_watermark,
        watermark_text=args.watermark_text or None,
        fmt=args.format,
        photo_path=getattr(args, "photo", None) or None,
    )


def cmd_list(args):
    for code in list_countries():
        gen = get_country(code)()
        types = ", ".join(gen.get_document_types())
        print(f"{code:12} {gen.get_country_name():20} {types}")
    return 0


def cmd_generate(args):
    gen = get_country(args.country)()
    persona = get_persona(args.country)
    person = {
        "first": args.first or persona["first"],
        "last": args.last or persona["last"],
        "position": args.position or persona["position"],
        "dob": args.dob or persona["dob"],
        "gender": args.gender or persona["gender"],
    }
    school = _resolve_school(gen, args.school)

    gen._current_person_id = f"{person['first']}_{person['last']}".lower()
    gen._current_gender = person["gender"]
    clear_photo_cache()

    types = args.document_types.split(",") if args.document_types else gen.get_document_types()
    out_dir = Path(args.out) if args.out else BASE_DIR / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = format_extension(args.format)

    for dtype in types:
        data = _generate_one(gen, dtype, person, school, args)
        path = out_dir / f"{args.country}_{dtype}_{person['first'].lower()}_{person['last'].lower()}{ext}"
        path.write_bytes(data)
        print(f"wrote {path}")
    return 0


def cmd_gallery(args):
    """Render every country x document type and build a browsable HTML index."""
    import html as _html

    out_dir = Path(args.out) if args.out else BASE_DIR / "docs" / "demo"
    out_dir.mkdir(parents=True, exist_ok=True)
    ext = format_extension(args.format)

    sections = []
    total = 0
    for code in list_countries():
        gen = get_country(code)()
        persona = get_persona(code)
        school = gen.schools[0]
        gen._current_person_id = f"{persona['first']}_{persona['last']}".lower()
        gen._current_gender = persona["gender"]
        clear_photo_cache()

        (out_dir / code).mkdir(parents=True, exist_ok=True)
        figs = []
        for dtype in gen.get_document_types():
            data = gen.generate_document_seeded(
                doc_type=dtype,
                first=persona["first"],
                last=persona["last"],
                school=school,
                position=persona["position"],
                dob=persona["dob"],
                seed=args.seed,
                watermark=not args.no_watermark,
                watermark_text=args.watermark_text or None,
                fmt=args.format,
            )
            rel = f"{code}/{dtype}{ext}"
            (out_dir / rel).write_bytes(data)
            total += 1
            figs.append(
                f'<figure><img src="{rel}" alt="{code} {dtype}">'
                f"<figcaption>{_html.escape(dtype)}</figcaption></figure>"
            )
            print(f"wrote {out_dir / rel}")

        sections.append(
            f'<section><h2>{_html.escape(gen.get_country_name())} <span class="code">{code}</span></h2>'
            f'<p class="persona">{_html.escape(persona["first"] + " " + persona["last"])} — '
            f'{_html.escape(persona["position"])}</p>'
            f'<div class="grid">{"".join(figs)}</div></section>'
        )

    banner = "" if args.no_watermark else '<p class="note">All documents carry a SAMPLE watermark.</p>'
    page = _GALLERY_TEMPLATE.format(
        title="Yowes demo gallery",
        banner=banner,
        count=total,
        sections="".join(sections),
    )
    index = out_dir / "index.html"
    index.write_text(page, encoding="utf-8")
    print(f"wrote {index} ({total} documents)")
    return 0


_GALLERY_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  :root {{ color-scheme: light; }}
  body {{ font: 15px/1.5 system-ui, sans-serif; margin: 0; padding: 24px; background: #f5f6f8; color: #1a1a1a; }}
  h1 {{ margin: 0 0 4px; font-size: 24px; }}
  .note {{ color: #a00; margin: 0 0 24px; font-weight: 600; }}
  section {{ margin-bottom: 40px; }}
  h2 {{ font-size: 18px; border-bottom: 2px solid #d5d8de; padding-bottom: 6px; }}
  .code {{ color: #888; font-weight: 400; font-size: 13px; text-transform: uppercase; }}
  .persona {{ color: #666; margin: 4px 0 16px; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }}
  figure {{ margin: 0; background: #fff; border: 1px solid #e2e5ea; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,.06); }}
  figure img {{ width: 100%; display: block; }}
  figcaption {{ padding: 8px 12px; font-size: 13px; color: #333; background: #fafbfc; border-top: 1px solid #e2e5ea; }}
</style>
</head>
<body>
<h1>{title}</h1>
{banner}
<p>{count} documents generated.</p>
{sections}
</body>
</html>
"""


def build_parser():
    parser = argparse.ArgumentParser(prog="yowes-cli", description="Yowes teacher document generator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List countries and their document types")
    p_list.set_defaults(func=cmd_list)

    p_gen = sub.add_parser("generate", help="Generate documents for one country/person")
    p_gen.add_argument("--country", required=True, help="Country code, e.g. us")
    p_gen.add_argument("--first")
    p_gen.add_argument("--last")
    p_gen.add_argument("--school", help="Exact or partial school name (default: first school)")
    p_gen.add_argument("--position")
    p_gen.add_argument("--dob", help="Display date of birth, e.g. 12/05/1988")
    p_gen.add_argument("--gender", choices=["Random", "Male", "Female"])
    p_gen.add_argument("--document-types", help="Comma-separated list, e.g. teacher_id,employment_letter")
    p_gen.add_argument("--format", default="png", choices=["png", "jpg", "pdf"])
    p_gen.add_argument("--photo", help="Path to a profile photo file (overrides the photo pool)")
    p_gen.add_argument("--seed", type=int, default=1234, help="Reproducible seed (default 1234)")
    p_gen.add_argument("--no-watermark", action="store_true", help="Disable the SAMPLE banner")
    p_gen.add_argument("--watermark-text", default="")
    p_gen.add_argument("--out", help="Output directory (default: output/)")
    p_gen.set_defaults(func=cmd_generate)

    p_gal = sub.add_parser("gallery", help="Render every country x document type and build an HTML index")
    p_gal.add_argument("--out", help="Output directory (default: docs/demo)")
    p_gal.add_argument("--format", default="png", choices=["png", "jpg", "pdf"])
    p_gal.add_argument("--seed", type=int, default=1234)
    p_gal.add_argument("--no-watermark", action="store_true")
    p_gal.add_argument("--watermark-text", default="")
    p_gal.set_defaults(func=cmd_gallery)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
