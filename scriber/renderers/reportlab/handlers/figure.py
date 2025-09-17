from __future__ import annotations
from typing import List
import io
from reportlab.platypus import Flowable, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
try:
    from svglib.svglib import svg2rlg  # type: ignore
except Exception:  # optional dependency
    svg2rlg = None

from ....core.nodes import FigureNode
from ....document import Document
from ..base import figure_export


def figure_flowables(doc: Document, node: FigureNode, styles) -> List[Flowable]:
    theme = doc.theme
    obj = node.props.get("obj")
    dpi = node.props.get("dpi", 144)
    fmt, data = figure_export(obj, dpi)

    width = node.props.get("width")
    height = node.props.get("height")
    flows: List[Flowable] = []
    page_w, page_h = (A4 if doc.size.upper() == "A4" else A4)
    frame_w = page_w - doc.margin * 2
    frame_h = page_h - doc.margin * 2

    if fmt == "svg" and svg2rlg is not None:
        drawing = svg2rlg(io.BytesIO(data))
        dw, dh = float(getattr(drawing, 'width', 0) or 0), float(getattr(drawing, 'height', 0) or 0)
        if width or height:
            if width and height and dw and dh:
                s = min(width / dw, height / dh)
            elif width and dw:
                s = width / dw
            elif height and dh:
                s = height / dh
            else:
                s = 1
        else:
            s = 1
            if dw and dh:
                s = min(frame_w / dw, frame_h / dh, 1)
        drawing.width, drawing.height = (dw * s if dw else 0), (dh * s if dh else 0)
        drawing.scale(s, s)
        align = node.props.get("align", "start")
        t = Table([[drawing]])
        t.setStyle(TableStyle([
            ("ALIGN", (0,0), (-1,-1), {"start":"LEFT","center":"CENTER","end":"RIGHT"}.get(align, "LEFT")),
            ("LEFTPADDING", (0,0), (-1,-1), 0),
            ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ("TOPPADDING", (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        flows.append(t)
    else:
        reader = ImageReader(io.BytesIO(data))
        px_w, px_h = reader.getSize()
        if width and height:
            target_w, target_h = width, height
        elif width:
            scale = width / float(px_w / 2)
            target_w, target_h = width, (px_h / 2) * scale
        elif height:
            scale = height / float(px_h / 2)
            target_w, target_h = (px_w / 2) * scale, height
        else:
            target_w, target_h = px_w / 2, px_h / 2
        if target_w > frame_w or target_h > frame_h:
            s = min(frame_w / target_w, frame_h / target_h)
            target_w, target_h = target_w * s, target_h * s
        img = Image(io.BytesIO(data), width=target_w, height=target_h)
        align = node.props.get("align", "start")
        img.hAlign = {"start": "LEFT", "center": "CENTER", "end": "RIGHT"}.get(align, "LEFT")
        flows.append(img)

    caption = node.props.get("caption")
    if caption:
        cap = Paragraph(caption, styles["Muted"])
        flows.append(Spacer(1, theme.spacing["xs"]))
        flows.append(cap)
    return flows
