from __future__ import annotations
from typing import List, Optional
from pathlib import Path as _Path
import io
import sys

DEFAULT_HEADERS = {"User-Agent": "scriber/0.1"}

from reportlab.lib.pagesizes import A4, LETTER
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Flowable, Image, Paragraph, Spacer

from ....core.nodes import ImageNode
from ....document import Document

_ALIGN_MAP = {
    "start": "LEFT",
    "center": "CENTER",
    "end": "RIGHT",
}

_PAGE_SIZES = {
    "A4": A4,
    "LETTER": LETTER,
}

_FIT_CHOICES = {"contain", "cover", "stretch", "scale-down"}


def _log_image_warning(message: str) -> None:
    try:
        print(f"[scriber] {message}", file=sys.stderr)
    except Exception:
        pass



def _derive_cache_key(source, explicit: Optional[str]) -> Optional[str]:
    if explicit:
        return explicit
    if isinstance(source, (str, _Path)):
        return str(source)
    return None


def _read_image_bytes(source) -> bytes:
    if source is None:
        raise TypeError("Image source cannot be None")

    if isinstance(source, str):
        trimmed = source.strip()
        lower = trimmed.lower()
        if lower.startswith(("http://", "https://")):
            try:
                import requests  # type: ignore
            except Exception as exc:  # noqa: PERF203
                raise RuntimeError("requests is required for HTTP image sources") from exc
            try:
                resp = requests.get(trimmed, timeout=10, headers=DEFAULT_HEADERS)
                resp.raise_for_status()
                return resp.content
            except requests.HTTPError as exc:  # type: ignore[attr-defined]
                status = exc.response.status_code if exc.response is not None else "unknown"
                raise RuntimeError(f"Failed to download image from {trimmed}: HTTP {status}") from exc
            except Exception as exc:  # noqa: PERF203
                raise RuntimeError(f"Failed to download image from {trimmed}: {exc}")
        src = _Path(trimmed).expanduser()
        try:
            return src.read_bytes()
        except Exception as exc:  # noqa: PERF203
            raise RuntimeError(f"Failed to read image file {src}: {exc}")

    if isinstance(source, _Path):
        src = source.expanduser()
        try:
            return src.read_bytes()
        except Exception as exc:  # noqa: PERF203
            raise RuntimeError(f"Failed to read image file {src}: {exc}")

    raise TypeError("ui.image expects a file path or URL string")


def _load_image_bytes(doc: Document, node: ImageNode) -> bytes:
    source = node.props.get("source")
    cache_key = _derive_cache_key(source, node.props.get("cache_key"))
    cache = getattr(doc, "_image_cache", None)
    if cache is None:
        cache = {}
        doc._image_cache = cache  # type: ignore[attr-defined]
    if cache_key and cache_key in cache:
        return cache[cache_key]

    data = _read_image_bytes(source)
    if cache_key:
        cache[cache_key] = data
    return data


def _frame_dimensions(doc: Document) -> tuple[float, float]:
    page_size = _PAGE_SIZES.get(doc.size.upper(), A4)
    frame_w = page_size[0] - doc.margin * 2
    frame_h = page_size[1] - doc.margin * 2
    return float(frame_w), float(frame_h)


def _compute_dimensions(px_w: float, px_h: float, width: Optional[float], height: Optional[float], fit: str, frame_w: float, frame_h: float) -> tuple[float, float]:
    # Convert pixels to points assuming 144 DPI -> divide by 2
    natural_w = px_w / 2.0
    natural_h = px_h / 2.0
    fit = fit if fit in _FIT_CHOICES else "contain"

    if width and height:
        if fit == "stretch":
            target_w, target_h = width, height
        else:
            scale_w = width / natural_w
            scale_h = height / natural_h
            scale = max(scale_w, scale_h) if fit == "cover" else min(scale_w, scale_h)
            target_w, target_h = natural_w * scale, natural_h * scale
    elif width:
        scale = width / natural_w
        target_w, target_h = natural_w * scale, natural_h * scale
    elif height:
        scale = height / natural_h
        target_w, target_h = natural_w * scale, natural_h * scale
    else:
        target_w, target_h = natural_w, natural_h

    if fit in {"contain", "scale-down"}:
        if target_w > frame_w or target_h > frame_h:
            scale = min(frame_w / target_w, frame_h / target_h)
            target_w *= scale
            target_h *= scale
    elif fit == "cover" and not (width or height):
        scale = max(frame_w / target_w, frame_h / target_h)
        target_w *= scale
        target_h *= scale

    return target_w, target_h


def image_flowables(doc: Document, node: ImageNode, styles) -> List[Flowable]:
    def _fallback(message: str) -> List[Flowable]:
        _log_image_warning(message)
        return [Paragraph(message, styles["Muted"])]

    try:
        data = _load_image_bytes(doc, node)
    except Exception as exc:
        source = node.props.get("source")
        label = f"Image unavailable ({source})" if source is not None else "Image unavailable"
        message = f"{label}: {exc}"
        return _fallback(message)

    try:
        reader = ImageReader(io.BytesIO(data))
        px_w, px_h = reader.getSize()
        reader.getRGBData()
    except Exception as exc:
        source = node.props.get("source")
        label = f"Image decode failed ({source})" if source is not None else "Image decode failed"
        message = f"{label}: {exc}"
        return _fallback(message)
    width = node.props.get("width")
    height = node.props.get("height")
    fit = (node.props.get("fit") or "contain").lower()
    frame_w, frame_h = _frame_dimensions(doc)
    target_w, target_h = _compute_dimensions(float(px_w), float(px_h), width, height, fit, frame_w, frame_h)

    image_flow = Image(io.BytesIO(data), width=target_w, height=target_h)
    align = _ALIGN_MAP.get((node.props.get("align") or "start").lower(), "LEFT")
    image_flow.hAlign = align

    flows: List[Flowable] = [image_flow]

    caption = node.props.get("caption")
    if caption:
        flows.append(Spacer(1, doc.theme.spacing["xs"]))
        flows.append(Paragraph(str(caption), styles["Muted"]))

    return flows
