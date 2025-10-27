#!/usr/bin/env python3
"""Convert DOCX tropical updates into Jekyll posts."""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import mammoth

DOC_GLOB = "incoming/posts/*.docx"
POSTS_DIR = Path("_posts")
ASSETS_ROOT = Path("assets/docs")
SUMMARY_LIMIT = 160


def _slugify(value: str) -> str:
    lowered = value.lower()
    cleaned = re.sub(r"[^a-z0-9\-\s]+", "", lowered)
    collapsed = re.sub(r"[\s_-]+", "-", cleaned)
    return collapsed.strip("-")


def _titlecase_slug(slug: str) -> str:
    parts = re.split(r"[-_]+", slug)
    titled = []
    for part in parts:
        if not part:
            continue
        if re.fullmatch(r"\d+[lL]", part):
            titled.append(part[:-1] + "L")
        elif part.isupper():
            titled.append(part)
        else:
            titled.append(part.capitalize())
    return " ".join(titled)


@dataclass
class PostMetadata:
    date_ymd: str
    datetime_iso: str
    slug: str
    slug_raw: str
    title: str


def _parse_filename(path: Path) -> PostMetadata:
    stem = path.stem
    tokens = stem.split("-")
    if len(tokens) < 4:
        raise ValueError(f"Filename '{path.name}' must follow YYYY-MM-DD[-time]-slug.docx")

    yyyy, mm, dd = tokens[0], tokens[1], tokens[2]
    rest = tokens[3:]
    if not (yyyy.isdigit() and mm.isdigit() and dd.isdigit()):
        raise ValueError(f"Filename '{path.name}' must start with YYYY-MM-DD")

    hour = 0
    minute = 0
    slug_tokens = rest
    if rest:
        first = rest[0]
        normalized = re.sub(r"[\s:_-]", "", first).lower()
        if normalized.endswith("am") or normalized.endswith("pm"):
            digits = normalized[:-2]
            if digits.isdigit() and 1 <= len(digits) <= 4:
                if len(digits) <= 2:
                    hour = int(digits)
                    minute = 0
                else:
                    hour = int(digits[:-2])
                    minute = int(digits[-2:])
                if 1 <= hour <= 12 and 0 <= minute < 60:
                    period = normalized[-2:]
                    hour_mod = hour % 12
                    if period == "pm":
                        hour_mod += 12
                    hour = hour_mod
                    slug_tokens = rest[1:] or rest
                else:
                    hour = 0
                    minute = 0
            # if invalid, treat token as part of slug
    if not slug_tokens:
        slug_tokens = rest

    slug_raw = "-".join(slug_tokens)
    slug = _slugify(slug_raw or "update")
    date_ymd = f"{int(yyyy):04d}-{int(mm):02d}-{int(dd):02d}"
    datetime_iso = f"{date_ymd} {hour:02d}:{minute:02d}:00"
    title = _titlecase_slug(slug_raw or slug)
    return PostMetadata(date_ymd=date_ymd, datetime_iso=datetime_iso, slug=slug, slug_raw=slug_raw, title=title)


def _clean_summary(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text).strip()
    if not collapsed:
        return ""
    if len(collapsed) <= SUMMARY_LIMIT:
        return collapsed
    truncated = collapsed[:SUMMARY_LIMIT]
    last_space = truncated.rfind(" ")
    if last_space > 40:
        truncated = truncated[:last_space]
    return truncated.rstrip() + "…"


def _write_post(meta: PostMetadata, body_html: str, summary: str, thumb_rel: Optional[str], youtube_id: Optional[str]) -> Path:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    post_path = POSTS_DIR / f"{meta.date_ymd}-{meta.slug}.html"
    with post_path.open("w", encoding="utf-8") as fh:
        fh.write("---\n")
        fh.write(f"layout: default\n")
        fh.write(f"title: {json.dumps(meta.title)}\n")
        fh.write(f"date: {meta.datetime_iso}\n")
        if summary:
            fh.write(f"summary: {json.dumps(summary)}\n")
        if thumb_rel:
            fh.write(f"thumb: {json.dumps(thumb_rel)}\n")
            fh.write(f"thumb_alt: {json.dumps(meta.title)}\n")
        if youtube_id:
            fh.write(f"youtube_id: {json.dumps(youtube_id)}\n")
        fh.write("---\n")
        fh.write(body_html.strip())
        fh.write("\n")
    return post_path


def _ensure_asset_dir(slug: str) -> Path:
    asset_dir = ASSETS_ROOT / slug
    if asset_dir.exists():
        shutil.rmtree(asset_dir)
    (asset_dir / "media").mkdir(parents=True, exist_ok=True)
    return asset_dir


def process_doc(path: Path) -> Path:
    meta = _parse_filename(path)
    asset_dir = _ensure_asset_dir(meta.slug)
    media_dir = asset_dir / "media"
    image_index = 0

    def _save_image(image: mammoth.images.Image) -> dict[str, str]:  # type: ignore[name-defined]
        nonlocal image_index
        content_type = image.content_type or "image/png"
        ext = content_type.split("/")[-1].split(";")[0]
        if not ext:
            ext = "png"
        image_index += 1
        filename = f"image{image_index}.{ext}"
        output_path = media_dir / filename
        with output_path.open("wb") as img_file:
            img_file.write(image.get_bytes())
        rel_src = f"/assets/docs/{meta.slug}/media/{filename}"
        return {"src": rel_src}

    with path.open("rb") as docx_file:
        result = mammoth.convert_to_html(docx_file, convert_image=mammoth.images.inline(_save_image))
    body_html = result.value
    warnings = [w for w in result.messages if getattr(w, "type", "") == "warning"]
    if warnings:
        print(f"Warnings for {path.name}: {warnings}")

    youtube_regex = re.compile(r"(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))([A-Za-z0-9_-]{11})")
    match = youtube_regex.search(body_html)
    youtube_id: Optional[str] = match.group(1) if match else None

    if youtube_id:
        anchor_regex = re.compile(
            r"<a\b[^>]*href=\"[^\"]*(?:youtu\.be/|youtube\.com/(?:watch\?v=|embed/))[A-Za-z0-9_-]{11}[^\"]*\"[^>]*>.*?</a>",
            re.IGNORECASE | re.DOTALL,
        )
        body_html = anchor_regex.sub("", body_html)
        body_html = youtube_regex.sub("", body_html)
        body_html = re.sub(r"https?://(?=[^A-Za-z0-9])", "", body_html)

    empty_paragraph_regex = re.compile(r"<p(?: [^>]*)?>\s*(?:&nbsp;|<br\s*/?>|\s)*</p>", re.IGNORECASE)
    body_html = empty_paragraph_regex.sub("", body_html)

    thumb_rel: Optional[str] = None

    img_regex = re.compile(r'(<img\b[^>]*\bsrc=\")([^\"]+)(\"[^>]*>)', re.IGNORECASE)

    def _replace_img(match: re.Match[str]) -> str:
        nonlocal thumb_rel
        prefix, src, suffix = match.groups()
        normalized = src
        if not normalized.startswith("/"):
            normalized = f"/assets/docs/{meta.slug}/media/{normalized}"
        if thumb_rel is None:
            thumb_rel = normalized
        new_src = "{{ '" + normalized + "' | relative_url }}"
        return f"{prefix}{new_src}{suffix}"

    body_html = img_regex.sub(_replace_img, body_html)

    plain_text = re.sub(r"<[^>]+>", " ", body_html)
    summary = _clean_summary(plain_text)

    post_path = _write_post(meta, body_html, summary, thumb_rel, youtube_id)
    print(f"Wrote {post_path.relative_to(Path('.'))}")
    return post_path


def main() -> None:
    paths = sorted(Path(".").glob(DOC_GLOB))
    if not paths:
        print("No DOCX posts found.")
        return
    for doc_path in paths:
        try:
            process_doc(doc_path)
        except Exception as exc:  # pragma: no cover
            raise RuntimeError(f"Failed to process {doc_path}") from exc


if __name__ == "__main__":
    main()
