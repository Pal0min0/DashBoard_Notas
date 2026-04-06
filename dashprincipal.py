import pandas as pd
import plotly.express as px
import dash
from dash import html, Input, Output, dcc, dash_table, State, ctx, no_update
import dash_bootstrap_components as dbc

from database import (
    obtenerestudiantes, agregar_estudiante, eliminar_estudiante
)

# ── Paleta Miku ───────────────────────────────────────────────────────────────
TEAL        = "#39c5bb"
TEAL_DARK   = "#1ba8a0"
BG_CARD     = "rgba(8,20,40,0.85)"
BG_PAGE     = "#0d0d1a"
TEXT_MAIN   = "#e0f8f7"
TEXT_DIM    = "rgba(57,197,187,0.55)"

CARD_STYLE = {
    "background": BG_CARD,
    "border": f"1.5px solid {TEAL}44",
    "borderRadius": "16px",
    "padding": "20px",
    "marginBottom": "20px",
    "boxShadow": f"0 4px 32px rgba(0,0,0,0.5), 0 0 20px {TEAL}11",
}

KPI_COLORS = ["#1ba8a0", "#39c5bb", "#0e7a74"]


def make_kpi(label, value, color):
    return html.Div([
        html.P(label, style={"color": TEXT_DIM, "fontSize": "11px",
                             "letterSpacing": "2px", "textTransform": "uppercase",
                             "marginBottom": "4px"}),
        html.H2(str(value), style={"color": TEXT_MAIN, "fontWeight": "800",
                                    "fontSize": "2rem", "margin": 0}),
    ], style={
        "background": f"linear-gradient(135deg, {color}33, {color}11)",
        "border": f"1.5px solid {color}66",
        "borderRadius": "14px",
        "padding": "18px 24px",
        "minWidth": "140px",
        "flex": "1",
        "margin": "0 8px",
        "textAlign": "center",
    })


def creartablero(server):
    app = dash.Dash(
        __name__,
        server=server,
        url_base_pathname="/dashprincipal/",
        suppress_callback_exceptions=True,
        external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=M+PLUS+Rounded+1c:wght@400;700;800&display=swap"
        ],
        title="ミク Dashboard"
    )

    # quitar la scrollbar propia de Dash — el scroll lo maneja el iframe padre
    app.index_string = '''
<!DOCTYPE html>
<html>
<head>
{%metas%}
<title>{%title%}</title>
{%favicon%}
{%css%}
<style>
  html, body, #react-entry-point, #_dash-app-content {
    overflow-x: hidden !important;
    scrollbar-width: none !important;
  }
  html::-webkit-scrollbar,
  body::-webkit-scrollbar {
    display: none !important;
    width: 0 !important;
  }
</style>
</head>
<body>
{%app_entry%}
<footer>
{%config%}
{%scripts%}
{%renderer%}
</footer>
</body>
</html>
'''

    # ── Layout ────────────────────────────────────────────────────────────────
    app.layout = html.Div([

        # ── Body ────────────────────────────────────────────────────────────
        html.Div([

            # ── Filtros ─────────────────────────────────────────────────────
            html.Div([
                html.Div([
                    html.Label("Carrera", style={"color": TEXT_DIM,
                                                 "fontSize": "10px",
                                                 "letterSpacing": "3px",
                                                 "textTransform": "uppercase"}),
                    dcc.Dropdown(
                        id="filtro_carrera",
                        clearable=False,
                        style={"background": BG_CARD, "color": BG_PAGE}
                    ),
                ], style={"flex": "1", "minWidth": "200px"}),

                html.Div([
                    html.Label("Rango de edad", style={"color": TEXT_DIM,
                                                       "fontSize": "10px",
                                                       "letterSpacing": "3px",
                                                       "textTransform": "uppercase"}),
                    dcc.RangeSlider(id="slider_edad", step=1,
                                    tooltip={"placement": "bottom",
                                             "always_visible": True}),
                ], style={"flex": "2", "minWidth": "220px"}),

                html.Div([
                    html.Label("Rango promedio", style={"color": TEXT_DIM,
                                                        "fontSize": "10px",
                                                        "letterSpacing": "3px",
                                                        "textTransform": "uppercase"}),
                    dcc.RangeSlider(id="slider_promedio", min=0, max=5,
                                    step=0.5, value=[0, 5],
                                    tooltip={"placement": "bottom",
                                             "always_visible": True}),
                ], style={"flex": "2", "minWidth": "220px"}),
            ], style={
                **CARD_STYLE,
                "display": "flex",
                "gap": "32px",
                "flexWrap": "wrap",
                "alignItems": "flex-end",
            }),

            # ── KPIs ────────────────────────────────────────────────────────
            html.Div(id="kpis", style={"display": "flex",
                                       "gap": "0",
                                       "flexWrap": "wrap",
                                       "marginBottom": "20px"}),

            # ── Tabla ───────────────────────────────────────────────────────
            html.Div([
                html.H3("📋 Estudiantes", style={"color": TEAL,
                                                  "fontSize": "13px",
                                                  "letterSpacing": "3px",
                                                  "marginBottom": "12px",
                                                  "textTransform": "uppercase"}),
                dcc.Loading(
                    dash_table.DataTable(
                        id="tabla",
                        page_size=8,
                        filter_action="native",
                        sort_action="native",
                        row_selectable="multi",
                        selected_rows=[],
                        style_table={"overflowX": "auto", "borderRadius": "10px"},
                        style_header={"backgroundColor": f"{TEAL}22",
                                      "color": TEAL,
                                      "fontWeight": "700",
                                      "border": f"1px solid {TEAL}33",
                                      "letterSpacing": "1px",
                                      "fontSize": "11px"},
                        style_cell={"textAlign": "center",
                                    "backgroundColor": "rgba(8,20,40,0.7)",
                                    "color": TEXT_MAIN,
                                    "border": "1px solid rgba(57,197,187,0.12)",
                                    "fontFamily": "'M PLUS Rounded 1c'",
                                    "fontSize": "13px"},
                        style_data_conditional=[
                            {"if": {"state": "selected"},
                             "backgroundColor": f"{TEAL}22",
                             "border": f"1px solid {TEAL}66"}
                        ],
                    ),
                    type="circle",
                    color=TEAL,
                ),
            ], style=CARD_STYLE),

            # ── Agregar estudiante ───────────────────────────────────────────
            html.Div([
                html.H3("➕ Agregar Estudiante", style={"color": TEAL,
                                                         "fontSize": "13px",
                                                         "letterSpacing": "3px",
                                                         "marginBottom": "16px",
                                                         "textTransform": "uppercase"}),
                html.Div([
                    _input_field("Nombre", "inp_nombre", "text", "ej. Hatsune"),
                    _input_field("Edad",   "inp_edad",   "number", "18"),
                    _input_field("Carrera","inp_carrera","text", "Fisica / Ingenieria / Matematicas"),
                    _input_field("Nota 1", "inp_nota1",  "number", "0-5"),
                    _input_field("Nota 2", "inp_nota2",  "number", "0-5"),
                    _input_field("Nota 3", "inp_nota3",  "number", "0-5"),
                ], style={"display": "flex", "gap": "12px", "flexWrap": "wrap"}),
                html.Div([
                    html.Button("✨ Agregar", id="btn_agregar",
                                style=_btn_style()),
                    html.Button("🗑 Eliminar seleccionados", id="btn_eliminar",
                                style=_btn_style("#e74c3c", "#c0392b")),
                ], style={"display": "flex", "gap": "12px", "marginTop": "16px"}),
                html.Div(id="msg_accion", style={"marginTop": "10px",
                                                 "color": TEAL,
                                                 "fontSize": "12px",
                                                 "letterSpacing": "2px"}),
            ], style=CARD_STYLE),

            # ── Gráfico detallado ────────────────────────────────────────────
            html.Div([
                html.H3("🔍 Análisis detallado (selecciona filas)", style={
                    "color": TEAL, "fontSize": "13px",
                    "letterSpacing": "3px", "marginBottom": "8px",
                    "textTransform": "uppercase"}),
                dcc.Loading(dcc.Graph(id="gra_detallado"),
                            type="default", color=TEAL),
            ], style=CARD_STYLE),

            # ── Tabs ────────────────────────────────────────────────────────
            html.Div([
                dcc.Tabs(id="tabs", value="histo", children=[
                    dcc.Tab(label="📊 Histograma",  value="histo",
                            style=_tab_style(), selected_style=_tab_sel()),
                    dcc.Tab(label="🔵 Dispersión",  value="disp",
                            style=_tab_style(), selected_style=_tab_sel()),
                    dcc.Tab(label="🥧 Desempeño",   value="pie",
                            style=_tab_style(), selected_style=_tab_sel()),
                    dcc.Tab(label="📈 Por Carrera", value="barras",
                            style=_tab_style(), selected_style=_tab_sel()),
                ]),
                dcc.Graph(id="tab_graph"),
            ], style=CARD_STYLE),

        ], style={"maxWidth": "1300px", "margin": "0 auto", "padding": "28px 24px"}),

        # Stores
        dcc.Store(id="store_refresh", data=0),

    ], style={
        "minHeight": "100vh",
        "background": f"linear-gradient(135deg, {BG_PAGE} 0%, #0a1628 50%, {BG_PAGE} 100%)",
        "fontFamily": "'M PLUS Rounded 1c', sans-serif",
    })

    # ── Helper: cargar opciones al iniciar ───────────────────────────────────
    @app.callback(
        Output("filtro_carrera", "options"),
        Output("filtro_carrera", "value"),
        Output("slider_edad", "min"),
        Output("slider_edad", "max"),
        Output("slider_edad", "value"),
        Input("store_refresh", "data"),
    )
    def cargar_filtros(_):
        df = obtenerestudiantes()
        carreras = sorted(df["Carrera"].unique())
        opts = [{"label": c, "value": c} for c in carreras]
        return (opts, carreras[0],
                int(df["Edad"].min()), int(df["Edad"].max()),
                [int(df["Edad"].min()), int(df["Edad"].max())])

    # ── Callback principal ───────────────────────────────────────────────────
    @app.callback(
        Output("tabla", "data"),
        Output("tabla", "columns"),
        Output("kpis", "children"),
        Input("filtro_carrera", "value"),
        Input("slider_edad", "value"),
        Input("slider_promedio", "value"),
        Input("store_refresh", "data"),
    )
    def actualizar_comp(carrera, rangoedad, rangoprome, _):
        if carrera is None:
            return [], [], []
        df = obtenerestudiantes()
        filtro = df[
            (df["Carrera"] == carrera) &
            (df["Edad"] >= rangoedad[0]) &
            (df["Edad"] <= rangoedad[1]) &
            (df["Promedio"] >= rangoprome[0]) &
            (df["Promedio"] <= rangoprome[1])
        ]

        promedio = round(filtro["Promedio"].mean(), 2) if len(filtro) else 0
        total    = len(filtro)
        maximo   = round(filtro["Promedio"].max(), 2) if len(filtro) else 0

        kpis = [
            make_kpi("Promedio",          promedio, KPI_COLORS[0]),
            make_kpi("Total estudiantes", total,    KPI_COLORS[1]),
            make_kpi("Máximo",            maximo,   KPI_COLORS[2]),
        ]

        cols = [{"name": c, "id": c} for c in filtro.columns]
        return filtro.to_dict("records"), cols, kpis

    # ── Tabs ─────────────────────────────────────────────────────────────────
    @app.callback(
        Output("tab_graph", "figure"),
        Input("tabs", "value"),
        Input("filtro_carrera", "value"),
        Input("slider_edad", "value"),
        Input("slider_promedio", "value"),
        Input("store_refresh", "data"),
    )
    def actualizar_tab(tab, carrera, rangoedad, rangoprome, _):
        if carrera is None:
            return _empty_fig()
        df = obtenerestudiantes()
        filtro = df[
            (df["Carrera"] == carrera) &
            (df["Edad"] >= rangoedad[0]) &
            (df["Edad"] <= rangoedad[1]) &
            (df["Promedio"] >= rangoprome[0]) &
            (df["Promedio"] <= rangoprome[1])
        ]
        template = "plotly_dark"
        paper    = "rgba(8,20,40,0)"
        plot_bg  = "rgba(8,20,40,0)"

        if tab == "histo":
            fig = px.histogram(filtro, x="Promedio", nbins=10,
                               title="Distribución de Promedios",
                               color_discrete_sequence=[TEAL],
                               template=template)
        elif tab == "disp":
            fig = px.scatter(filtro, x="Edad", y="Promedio",
                             color="Desempeño", trendline="ols",
                             title="Edad vs Promedio",
                             template=template)
        elif tab == "pie":
            fig = px.pie(filtro, names="Desempeño",
                         title="Distribución por Desempeño",
                         color_discrete_sequence=px.colors.sequential.Teal,
                         template=template)
        else:
            promedios = df.groupby("Carrera")["Promedio"].mean().reset_index()
            fig = px.bar(promedios, x="Carrera", y="Promedio",
                         color="Carrera",
                         title="Promedio General por Carrera",
                         color_discrete_sequence=px.colors.sequential.Teal,
                         template=template)

        fig.update_layout(paper_bgcolor=paper, plot_bgcolor=plot_bg,
                          font_color=TEXT_MAIN)
        return fig

    # ── Detallado ────────────────────────────────────────────────────────────
    @app.callback(
        Output("gra_detallado", "figure"),
        Input("tabla", "derived_virtual_data"),
        Input("tabla", "derived_virtual_selected_rows"),
    )
    def actualizartab(rows, selected_rows):
        if not rows:
            return _empty_fig("Selecciona filas de la tabla para ver el análisis")
        dff = pd.DataFrame(rows)
        if selected_rows:
            dff = dff.iloc[selected_rows]
        if dff.empty:
            return _empty_fig("Sin filas seleccionadas")
        fig = px.scatter(dff, x="Edad", y="Promedio", color="Desempeño",
                         size="Promedio",
                         title="Análisis detallado",
                         trendline="ols",
                         template="plotly_dark")
        fig.update_layout(paper_bgcolor="rgba(8,20,40,0)",
                          plot_bgcolor="rgba(8,20,40,0)",
                          font_color=TEXT_MAIN)
        return fig

    # ── Agregar / Eliminar ────────────────────────────────────────────────────
    @app.callback(
        Output("store_refresh", "data"),
        Output("msg_accion", "children"),
        Output("inp_nombre", "value"),
        Output("inp_edad",   "value"),
        Output("inp_carrera","value"),
        Output("inp_nota1",  "value"),
        Output("inp_nota2",  "value"),
        Output("inp_nota3",  "value"),
        Input("btn_agregar",  "n_clicks"),
        Input("btn_eliminar", "n_clicks"),
        State("inp_nombre",  "value"),
        State("inp_edad",    "value"),
        State("inp_carrera", "value"),
        State("inp_nota1",   "value"),
        State("inp_nota2",   "value"),
        State("inp_nota3",   "value"),
        State("tabla", "derived_virtual_data"),
        State("tabla", "derived_virtual_selected_rows"),
        State("store_refresh", "data"),
        prevent_initial_call=True,
    )
    def manejar_acciones(n_add, n_del,
                         nombre, edad, carrera, n1, n2, n3,
                         rows, sel_rows, refresh):
        triggered = ctx.triggered_id
        blank = ("", None, "", None, None, None)

        if triggered == "btn_agregar":
            if not all([nombre, edad, carrera, n1 is not None,
                        n2 is not None, n3 is not None]):
                return no_update, "⚠️ Completa todos los campos", no_update, no_update, no_update, no_update, no_update, no_update
            try:
                prom, desemp = agregar_estudiante(
                    nombre, int(edad), carrera,
                    float(n1), float(n2), float(n3)
                )
                msg = f"✅ Estudiante '{nombre}' agregado — Promedio: {prom} ({desemp})"
                return refresh + 1, msg, *blank
            except Exception as e:
                return no_update, f"❌ Error: {e}", no_update, no_update, no_update, no_update, no_update, no_update

        if triggered == "btn_eliminar":
            if not rows or not sel_rows:
                return no_update, "⚠️ Selecciona filas de la tabla primero", no_update, no_update, no_update, no_update, no_update, no_update
            ids = [rows[i]["Id"] for i in sel_rows]
            for id_est in ids:
                eliminar_estudiante(id_est)
            return refresh + 1, f"🗑 {len(ids)} estudiante(s) eliminado(s)", no_update, no_update, no_update, no_update, no_update, no_update

        return no_update, "", no_update, no_update, no_update, no_update, no_update, no_update

    return app


# ── Helpers ──────────────────────────────────────────────────────────────────

def _input_field(label, id_, type_, placeholder):
    return html.Div([
        html.Label(label, style={"color": TEXT_DIM, "fontSize": "10px",
                                 "letterSpacing": "2px",
                                 "textTransform": "uppercase",
                                 "display": "block",
                                 "marginBottom": "4px"}),
        dcc.Input(id=id_, type=type_, placeholder=placeholder,
                  style={"background": "rgba(57,197,187,0.05)",
                         "border": "1.5px solid rgba(57,197,187,0.2)",
                         "borderRadius": "10px",
                         "color": "#e0f8f7",
                         "padding": "9px 12px",
                         "fontSize": "13px",
                         "fontFamily": "'M PLUS Rounded 1c'",
                         "outline": "none",
                         "width": "100%"}),
    ], style={"flex": "1", "minWidth": "130px"})


def _btn_style(bg=TEAL_DARK, hover=None):
    return {
        "background": f"linear-gradient(90deg, {bg}, {TEAL if bg == TEAL_DARK else bg})",
        "color": "#0a1628" if bg == TEAL_DARK else "#fff",
        "border": "none",
        "borderRadius": "10px",
        "padding": "10px 22px",
        "fontFamily": "'M PLUS Rounded 1c'",
        "fontWeight": "800",
        "fontSize": "13px",
        "letterSpacing": "2px",
        "cursor": "pointer",
        "boxShadow": f"0 4px 16px {bg}55",
    }


def _tab_style():
    return {"background": "rgba(8,20,40,0.6)",
            "color": TEXT_DIM,
            "border": f"1px solid {TEAL}22",
            "borderRadius": "8px 8px 0 0",
            "padding": "8px 18px",
            "fontSize": "12px",
            "letterSpacing": "1px"}


def _tab_sel():
    return {**_tab_style(),
            "background": f"{TEAL}22",
            "color": TEAL,
            "border": f"1.5px solid {TEAL}66",
            "fontWeight": "800"}


def _empty_fig(title="Sin datos"):
    import plotly.graph_objects as go
    fig = go.Figure()
    fig.update_layout(title=title,
                      paper_bgcolor="rgba(8,20,40,0)",
                      plot_bgcolor="rgba(8,20,40,0)",
                      font_color=TEXT_DIM)
    return fig