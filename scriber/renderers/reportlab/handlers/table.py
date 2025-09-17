from __future__ import annotations
from typing import List, Tuple
from reportlab.platypus import Flowable, Paragraph, Table, TableStyle

from ....core.nodes import TableNode
from ....document import Document


def _normalize_table_source(source, columns):
    # pandas
    try:
        import pandas as pd  # type: ignore
        if isinstance(source, pd.DataFrame):
            if columns is None:
                columns = list(source.columns)
            rows = source[columns].astype(object).values.tolist()
            return columns, rows
    except Exception:
        pass
    # polars
    try:
        import polars as pl  # type: ignore
        if isinstance(source, pl.DataFrame):
            if columns is None:
                columns = list(source.columns)
            rows = source.select(columns).to_numpy().tolist()
            return columns, rows
    except Exception:
        pass
    # list[dict]
    if isinstance(source, list) and source and isinstance(source[0], dict):
        keys = columns or list(source[0].keys())
        rows = [[row.get(k) for k in keys] for row in source]
        return keys, rows
    # list[list]
    if isinstance(source, list) and source and isinstance(source[0], (list, tuple)):
        if columns is None:
            return None, [list(r) for r in source]
        else:
            return columns, [list(r) for r in source]
    return columns, []


def table_flowables(doc: Document, node: TableNode, styles) -> List[Flowable]:
    theme = doc.theme
    src = node.props.get("source")
    columns = node.props.get("columns")
    header = bool(node.props.get("header", True))
    zebra = bool(node.props.get("zebra", False))
    compact = bool(node.props.get("compact", False))
    align_prop = node.props.get("align")
    header_align_prop = node.props.get("header_align")
    header_bold = bool(node.props.get("header_bold", True))
    formats = node.props.get("formats", {}) or {}
    currency_symbol = node.props.get("currency_symbol") or doc.settings.currency_symbol
    col_widths_prop = node.props.get("col_widths")

    cols, rows = _normalize_table_source(src, columns)
    n_cols = len(cols) if cols else (len(rows[0]) if rows else 0)

    # numeric detection
    import numbers as _numbers
    numeric_cols = [False] * n_cols
    if n_cols:
        for ci in range(n_cols):
            is_numeric = True
            for r in rows:
                if ci >= len(r):
                    continue
                v = r[ci]
                if v is None:
                    continue
                if isinstance(v, _numbers.Number):
                    continue
                try:
                    float(str(v).replace(",", ""))
                except Exception:
                    is_numeric = False
                    break
            numeric_cols[ci] = is_numeric

    # build data with formatting
    from ..base import format_number, format_percent, apply_separators
    def fmt_cell(ci: int, v):
        if v is None:
            return ""
        from datetime import date, datetime
        if isinstance(v, (datetime, date)):
            try:
                if isinstance(v, datetime):
                    return v.strftime(doc.settings.datetime_format)
                return v.strftime(doc.settings.date_format)
            except Exception:
                return str(v)
        fmt = None
        fmt_decimals = None
        if isinstance(formats, dict):
            if cols and ci < len(cols) and cols[ci] in formats:
                fmt = formats[cols[ci]]
            elif ci in formats:
                fmt = formats[ci]
        if isinstance(fmt, dict):
            fmt_decimals = fmt.get("decimals")
            fmt = fmt.get("type")
        elif isinstance(fmt, (list, tuple)) and fmt:
            fmt, *rest = fmt
            if rest:
                fmt_decimals = rest[0]
        if fmt == "currency" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                s = format_number(num, doc.settings, fmt_decimals)
                return f"{currency_symbol}{s}"
            except Exception:
                return str(v)
        if fmt == "percent" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return format_percent(num, doc.settings, fmt_decimals)
            except Exception:
                return str(v)
        if fmt == "int" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                s = format_number(num, doc.settings, 0)
                if doc.settings.decimal_separator in s:
                    s = s.split(doc.settings.decimal_separator)[0]
                return s
            except Exception:
                return str(v)
        if fmt == "thousands" and numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return format_number(num, doc.settings, 0)
            except Exception:
                return str(v)
        if isinstance(fmt, str) and fmt not in ("currency",):
            try:
                num = float(str(v).replace(",", ""))
                s = format(num, fmt)
                if any(ch in s for ch in [",", "."]):
                    s = apply_separators(s, doc.settings)
                return s
            except Exception:
                return str(v)
        if numeric_cols[ci]:
            try:
                num = float(str(v).replace(",", ""))
                return format_number(num, doc.settings)
            except Exception:
                return str(v)
        return str(v)

    data = []
    if header and cols:
        if header_bold:
            from reportlab.lib.styles import ParagraphStyle
            base_header_style = ParagraphStyle(name="Header", parent=styles["Body"], fontName="Helvetica-Bold")
        else:
            base_header_style = styles["Body"]

        def ps_with_align(base, align_token):
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
            if not align_token:
                return base
            token = str(align_token).lower()
            align_map = {"left": TA_LEFT, "center": TA_CENTER, "right": TA_RIGHT}
            if token not in align_map:
                return base
            from reportlab.lib.styles import ParagraphStyle
            return ParagraphStyle(name=base.name + f"-{token}", parent=base, alignment=align_map[token])

        header_cells = []
        for i, h in enumerate(cols):
            a = header_align_prop[i] if isinstance(header_align_prop, (list, tuple)) and i < len(header_align_prop) else header_align_prop
            st = ps_with_align(base_header_style, a)
            header_cells.append(Paragraph(str(h), st))
        data.append(header_cells)

    for row in rows:
        data.append([Paragraph(fmt_cell(ci, (row[ci] if ci < len(row) else None)), styles["Body"]) for ci in range(n_cols)])

    class _DataTable(Flowable):
        def __init__(self, data, cols, align_prop, col_widths_prop, zebra, compact):
            super().__init__()
            self.data = data
            self.cols = cols
            self.align_prop = align_prop
            self.col_widths_prop = col_widths_prop
            self.zebra = zebra
            self.compact = compact
            self._t = None

        def _col_widths(self, availWidth):
            n = len(self.cols) if self.cols else (len(self.data[0]) if self.data else 0)
            if not n:
                return []
            if isinstance(self.col_widths_prop, (list, tuple)) and self.col_widths_prop:
                vals = []
                total_frac = 0.0
                for w in self.col_widths_prop:
                    if isinstance(w, (int, float)):
                        vals.append(float(w))
                    elif isinstance(w, str) and w.endswith("%"):
                        try:
                            frac = float(w[:-1]) / 100.0
                        except Exception:
                            frac = 0
                        vals.append(frac)
                        total_frac += frac
                    else:
                        vals.append(None)
                if total_frac > 0:
                    scaled = [vw * availWidth if isinstance(vw, float) and vw <= 1 else vw for vw in vals]
                    return scaled
                return vals
            return [availWidth / n] * n

        def _alignments(self, n_cols):
            def map_align(a):
                return {"left": "LEFT", "center": "CENTER", "right": "RIGHT"}.get(str(a).lower(), "LEFT")
            if isinstance(self.align_prop, (list, tuple)):
                arr = [map_align(a) for a in self.align_prop]
                if len(arr) < n_cols:
                    arr += ["LEFT"] * (n_cols - len(arr))
                return arr[:n_cols]
            elif self.align_prop:
                return [map_align(self.align_prop)] * n_cols
            else:
                return ["LEFT"] * n_cols

        def _build(self, availWidth):
            n_cols = len(self.data[0]) if self.data else 0
            col_widths = self._col_widths(availWidth)
            repeat = 1 if (header and cols) else 0
            t = Table(self.data, colWidths=col_widths or None, repeatRows=repeat)
            pad_y = theme.control["sizes"]["sm" if self.compact else "md"]["py"]
            pad_x = theme.control["sizes"]["sm" if self.compact else "md"]["px"]
            style_cmds = [
                ("LEFTPADDING", (0, 0), (-1, -1), pad_x),
                ("RIGHTPADDING", (0, 0), (-1, -1), pad_x),
                ("TOPPADDING", (0, 0), (-1, -1), pad_y),
                ("BOTTOMPADDING", (0, 0), (-1, -1), pad_y),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, theme.colors["border"]),
            ]
            if self.cols:
                style_cmds += [
                    ("BACKGROUND", (0, 0), (-1, 0), theme.colors["surface"]),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.8, theme.colors["border"]),
                ]
            if zebra and len(self.data) > (1 if self.cols else 0):
                start = 1 if self.cols else 0
                for r in range(start, len(self.data)):
                    if (r - start) % 2 == 0:
                        style_cmds.append(("BACKGROUND", (0, r), (-1, r), theme.colors["surface"]))

            aligns = self._alignments(n_cols)
            if not align_prop:
                aligns = ["RIGHT" if numeric_cols[c] else "LEFT" for c in range(n_cols)]
            for c, a in enumerate(aligns):
                style_cmds.append(("ALIGN", (c, 0), (c, -1), a))

            t.setStyle(TableStyle(style_cmds))
            self._t = t

        def wrap(self, availWidth, availHeight):
            self._build(availWidth)
            return self._t.wrap(availWidth, availHeight)

        def split(self, availWidth, availHeight):
            if not self._t:
                self._build(availWidth)
            return self._t.split(availWidth, availHeight)

        def draw(self):
            self._t.drawOn(self.canv, 0, 0)

    return [_DataTable(data, cols, align_prop, col_widths_prop, zebra, compact)]

