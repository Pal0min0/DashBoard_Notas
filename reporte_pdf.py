"""
reporte_pdf.py — Genera el reporte de notas en PDF con estilo Miku
Uso: from reporte_pdf import generar_reporte_pdf
"""
import io
import datetime
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from reportlab.lib.pagesizes import A4
from reportlab.lib.units    import mm
from reportlab.lib           import colors
from reportlab.pdfgen        import canvas as rl_canvas
from reportlab.platypus      import Table, TableStyle


# ── Paleta Miku ───────────────────────────────────────────────────────────────
BG        = colors.HexColor("#0d0d1a")
BG2       = colors.HexColor("#0a1628")
CARD      = colors.HexColor("#0e1f3a")
TEAL      = colors.HexColor("#39c5bb")
TEAL_DARK = colors.HexColor("#1ba8a0")
TEXT      = colors.HexColor("#e0f8f7")
TEXT_DIM  = colors.HexColor("#5dd9d0")
RED       = colors.HexColor("#e74c3c")
GOLD      = colors.HexColor("#f0c040")
GREEN     = colors.HexColor("#2ecc71")
WHITE     = colors.white

W, H = A4   # 595 x 842 pts


def _bar_chart(nota1, nota2, nota3, promedio):
    """Genera gráfica de barras como bytes PNG."""
    fig, ax = plt.subplots(figsize=(5.2, 2.4), facecolor="#0a1628")
    ax.set_facecolor("#0a1628")

    notas  = [nota1, nota2, nota3]
    labels = ["Nota 1", "Nota 2", "Nota 3"]
    colores = ["#39c5bb", "#1ba8a0", "#5dd9d0"]

    bars = ax.bar(labels, notas, color=colores, width=0.45,
                  edgecolor="#39c5bb44", linewidth=0.8)

    # línea de promedio
    ax.axhline(promedio, color="#f0c040", linewidth=1.4,
               linestyle="--", label=f"Promedio: {promedio}")

    # valores encima de cada barra
    for bar, val in zip(bars, notas):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.08,
                str(val), ha="center", va="bottom",
                color="#e0f8f7", fontsize=9, fontweight="bold")

    ax.set_ylim(0, 5.6)
    ax.set_yticks([0, 1, 2, 3, 4, 5])
    ax.tick_params(colors="#5dd9d0", labelsize=8)
    for spine in ax.spines.values():
        spine.set_edgecolor("#39c5bb44")
    ax.yaxis.label.set_color("#5dd9d0")
    ax.xaxis.label.set_color("#5dd9d0")
    ax.tick_params(axis="x", colors="#e0f8f7")
    ax.tick_params(axis="y", colors="#5dd9d0")
    ax.legend(facecolor="#0d0d1a", edgecolor="#39c5bb44",
              labelcolor="#f0c040", fontsize=8)

    buf = io.BytesIO()
    plt.tight_layout(pad=0.4)
    plt.savefig(buf, format="png", dpi=140, facecolor="#0a1628")
    plt.close(fig)
    buf.seek(0)
    return buf


def _rounded_rect(c, x, y, w, h, r=6, fill=None, stroke=None, stroke_width=1):
    """Dibuja un rectángulo redondeado."""
    c.saveState()
    if fill:
        c.setFillColor(fill)
    if stroke:
        c.setStrokeColor(stroke)
        c.setLineWidth(stroke_width)
    path = c.beginPath()
    path.roundRect(x, y, w, h, r)
    c.drawPath(path, fill=1 if fill else 0, stroke=1 if stroke else 0)
    c.restoreState()


def _kpi_card(c, x, y, w, h, label, value, color=None):
    color = color or TEAL
    _rounded_rect(c, x, y, w, h, r=8, fill=CARD, stroke=color, stroke_width=0.8)
    # label
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 7)
    c.drawCentredString(x + w/2, y + h - 16, label.upper())
    # value
    c.setFillColor(color)
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(x + w/2, y + h/2 - 8, str(value))


def _section_title(c, x, y, text):
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x, y, text.upper())
    c.setStrokeColor(TEAL)
    c.setLineWidth(0.4)
    c.line(x, y - 3, x + 480, y - 3)


def _nivel_color(desempeno):
    d = (desempeno or "").lower()
    if "excelente" in d: return GREEN
    if "bueno"     in d: return TEAL
    if "regular"   in d: return GOLD
    return RED


def generar_reporte_pdf(datos: dict) -> bytes:
    """
    datos = {
        "estudiante": { id, nombre, edad, carrera,
                        nota1, nota2, nota3, promedio, desempeno },
        "stats":      { promedio_carrera, total, aprobados, reprobados },
        "posicion":   int
    }
    Devuelve bytes del PDF.
    """
    est   = datos["estudiante"]
    stats = datos["stats"]
    pos   = datos["posicion"]

    buf = io.BytesIO()
    c   = rl_canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Reporte de Notas — {est['nombre']}")

    # ── FONDO ────────────────────────────────────────────────────────────────
    c.setFillColor(BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # ── HEADER ───────────────────────────────────────────────────────────────
    _rounded_rect(c, 0, H - 62*mm, W, 62*mm, r=0, fill=BG2)
    # borde inferior teal
    c.setStrokeColor(TEAL)
    c.setLineWidth(1.5)
    c.line(0, H - 62*mm, W, H - 62*mm)

    # icono 🎤 simulado con texto
    c.setFillColor(TEAL)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20*mm, H - 22*mm, "REPORTE DE NOTAS")

    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 9)
    fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    c.drawRightString(W - 20*mm, H - 22*mm, f"Generado el {fecha}")

    # nombre y carrera
    c.setFillColor(TEXT)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(20*mm, H - 34*mm, est["nombre"])

    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 9)
    c.drawString(20*mm, H - 42*mm,
                 f"{est['carrera']}   ·   {est['edad']} años   ·   ID #{est['id']}")

    # badge desempeño
    nivel_col = _nivel_color(est.get("desempeno", ""))
    _rounded_rect(c, W - 65*mm, H - 46*mm, 42*mm, 12*mm,
                  r=6, fill=nivel_col, stroke=None)
    c.setFillColor(BG)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W - 44*mm, H - 41*mm,
                        (est.get("desempeno") or "").upper())

    # ── SECCIÓN: NOTAS ───────────────────────────────────────────────────────
    y0 = H - 80*mm
    _section_title(c, 20*mm, y0, "Notas Actuales")

    kw = 88; kh = 38; kgap = 8; kx0 = 20*mm
    notas_data = [
        ("Nota 1",   est["nota1"],   TEAL),
        ("Nota 2",   est["nota2"],   TEAL_DARK),
        ("Nota 3",   est["nota3"],   TEXT_DIM),
        ("Promedio", round(float(est["promedio"]), 2), GOLD),
    ]
    for i, (lbl, val, col) in enumerate(notas_data):
        _kpi_card(c, kx0 + i*(kw+kgap), y0 - kh - 6, kw, kh, lbl, val, col)

    # ── GRÁFICA ──────────────────────────────────────────────────────────────
    y1 = y0 - kh - 22
    _section_title(c, 20*mm, y1, "Gráfica de Notas")

    chart_buf = _bar_chart(
        float(est["nota1"]), float(est["nota2"]), float(est["nota3"]),
        float(est["promedio"])
    )
    from reportlab.lib.utils import ImageReader
    img = ImageReader(chart_buf)
    c.drawImage(img, 20*mm, y1 - 68*mm, width=148*mm, height=58*mm,
                preserveAspectRatio=True)

    # ── SECCIÓN: COMPARACIÓN CON CARRERA ─────────────────────────────────────
    y2 = y1 - 75*mm
    _section_title(c, 20*mm, y2, "Comparación con la Carrera")

    comp_data = [
        ("Promedio carrera",   round(float(stats["promedio_carrera"] or 0), 2), TEAL),
        ("Total estudiantes",  stats["total"],      TEXT),
        ("Aprobados",          stats["aprobados"],  GREEN),
        ("Reprobados",         stats["reprobados"], RED),
        ("Tu posición",        f"#{pos}",           GOLD),
    ]
    cw = 82; ch = 38; cgap = 6; cx0 = 20*mm
    for i, (lbl, val, col) in enumerate(comp_data):
        _kpi_card(c, cx0 + i*(cw+cgap), y2 - ch - 6, cw, ch, lbl, val, col)

    # diferencia con el promedio
    diff = float(est["promedio"]) - float(stats["promedio_carrera"] or 0)
    y3   = y2 - ch - 20
    if diff >= 0:
        msg_col = GREEN
        msg_txt = f"Estas {round(diff,2)} puntos por encima del promedio de tu carrera."
    else:
        msg_col = RED
        msg_txt = f"Estas {round(abs(diff),2)} puntos por debajo del promedio de tu carrera."

    _rounded_rect(c, 20*mm, y3 - 10*mm, W - 40*mm, 12*mm,
                  r=6, fill=CARD, stroke=msg_col, stroke_width=0.6)
    c.setFillColor(msg_col)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(24*mm, y3 - 5*mm, msg_txt)

    # ── SECCIÓN: HISTORIAL ───────────────────────────────────────────────────
    y4 = y3 - 20*mm
    _section_title(c, 20*mm, y4, "Historial de Cambios de Notas")

    _rounded_rect(c, 20*mm, y4 - 18*mm, W - 40*mm, 14*mm,
                  r=6, fill=CARD, stroke=TEAL, stroke_width=0.4)
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 8)
    c.drawString(24*mm, y4 - 12*mm,
                 "Aun no hay cambios registrados en las notas de este estudiante.")

    # ── FOOTER ───────────────────────────────────────────────────────────────
    c.setStrokeColor(TEAL)
    c.setLineWidth(0.4)
    c.line(20*mm, 16*mm, W - 20*mm, 16*mm)
    c.setFillColor(TEXT_DIM)
    c.setFont("Helvetica", 7)
    c.drawCentredString(W/2, 10*mm,
                        "Control de Notas  ·  Documento generado automaticamente  ·  ミク Dashboard")

    c.save()
    buf.seek(0)
    return buf.getvalue()