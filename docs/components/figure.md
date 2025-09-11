# Figure

Embed plots and charts from popular Python viz libraries.

API
- `ui.figure(obj, width=None, height=None, dpi=144, align="start", caption=None)`

Supported objects
- Matplotlib: `Figure` or `Axes` (Seaborn returns Matplotlib objects)
- Plotnine: `ggplot`
- Plotly: `plotly.graph_objects.Figure` (requires `kaleido`)
- Altair: `alt.Chart` (requires `vl-convert-python`)

Notes
- Rendering uses PNG rasterization for reliability; vector (SVG) may be added later.
- If only `width` or `height` is provided, aspect ratio is preserved.
- `align` accepts `start|center|end`. `caption` renders in a muted style under the figure.
- Optional dependencies are not installed by default. Add them as needed:
  - `uv add matplotlib` for Matplotlib/Seaborn/Plotnine
  - `uv add kaleido plotly` for Plotly
  - `uv add altair vl-convert-python` for Altair

Example (Matplotlib)
```
import matplotlib.pyplot as plt
from scriber import pdf, ui
from scriber.document import page

fig, ax = plt.subplots()
ax.plot([0,1,2], [0,1,0])

with pdf.document("out_fig.pdf", theme="shadcn"):
    with page():
        ui.h3("Line Plot")
        ui.figure(fig, caption="Simple line plot")
```

