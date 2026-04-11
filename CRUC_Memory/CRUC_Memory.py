import reflex as rx
import plotly.graph_objects as go
from pydantic import BaseModel
from CRUC_Memory.cbr_engine import cargar_casos, retrieve, reuse, retain, ATRIBUTOS
from CRUC_Memory.ia_service import explicar_recomendacion

# ── Paleta ────────────────────────────────────────────────────────────────────
BG      = "#0E1117"
PANEL   = "#161B25"
PANEL2  = "#1C2333"
BORDER  = "#243044"
CYAN    = "#38BDF8"
CYAN_D  = "rgba(56,189,248,0.10)"
GREEN   = "#34D399"
GREEN_D = "rgba(52,211,153,0.08)"
INK     = "#E2E8F0"
MUTED   = "#64748B"
MUTED2  = "#94A3B8"


class CasoSimilar(BaseModel):
    nombre: str
    carrera: str
    distancia_euclidiana: float
    similitud_coseno: float
    vector: list[float]


class State(rx.State):
    matematica:   list[float] = [5]
    logica:       list[float] = [5]
    comunicacion: list[float] = [5]
    creatividad:  list[float] = [5]
    ciencias:     list[float] = [5]
    liderazgo:    list[float] = [5]

    casos_similares:     list[CasoSimilar] = []
    carrera_recomendada: str  = ""
    explicacion_ia:      str  = ""
    loading:             bool = False
    caso_retenido:       bool = False

    def set_matematica(self, v):   self.matematica   = v
    def set_logica(self, v):       self.logica       = v
    def set_comunicacion(self, v): self.comunicacion = v
    def set_creatividad(self, v):  self.creatividad  = v
    def set_ciencias(self, v):     self.ciencias     = v
    def set_liderazgo(self, v):    self.liderazgo    = v

    @property
    def _perfil(self) -> dict:
        keys = ["matematica", "logica", "comunicacion", "creatividad", "ciencias", "liderazgo"]
        return {k: int(getattr(self, k)[0]) for k in keys}

    def consultar(self):
        self.loading = True
        self.caso_retenido = False
        yield
        df = cargar_casos()
        self.casos_similares     = [CasoSimilar(**c) for c in retrieve(self._perfil, df, k=3)]
        self.carrera_recomendada = reuse(self.casos_similares)
        self.explicacion_ia      = explicar_recomendacion(
            self._perfil, self.carrera_recomendada, self.casos_similares
        )
        self.loading = False

    def confirmar_y_retener(self):
        retain(self._perfil, self.carrera_recomendada)
        self.caso_retenido = True

    @rx.var
    def grafico_radar(self) -> go.Figure:
        keys = ["matematica", "logica", "comunicacion", "creatividad", "ciencias", "liderazgo"]
        vals = [int(getattr(self, k)[0]) for k in keys]
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=ATRIBUTOS + [ATRIBUTOS[0]],
            fill="toself", name="Tu perfil",
            line=dict(color=CYAN, width=2),
            fillcolor="rgba(56,189,248,0.12)",
        ))
        if self.casos_similares:
            v = self.casos_similares[0].vector
            fig.add_trace(go.Scatterpolar(
                r=v + [v[0]], theta=ATRIBUTOS + [ATRIBUTOS[0]],
                fill="toself", name=self.casos_similares[0].nombre,
                line=dict(color=GREEN, width=1.5, dash="dot"),
                fillcolor="rgba(52,211,153,0.07)",
            ))
        fig.update_layout(
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 10],
                                gridcolor="#1E2A3A", tickfont=dict(color=MUTED, size=9),
                                linecolor="#243044"),
                angularaxis=dict(gridcolor="#1C2840",
                                 tickfont=dict(color=MUTED2, size=11),
                                 linecolor="#243044"),
            ),
            showlegend=True,
            legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=MUTED2, size=11),
                        orientation="h", y=-0.12),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=50, r=50, t=30, b=50),
            height=360,
        )
        return fig

    # Porcentaje de similitud (0-100) basado en similitud coseno del caso top
    @rx.var
    def pct_similitud(self) -> int:
        if not self.casos_similares:
            return 0
        return int(round(self.casos_similares[0].similitud_coseno * 100))

    # Nivel de coincidencia en texto legible
    @rx.var
    def nivel_match(self) -> str:
        if not self.casos_similares:
            return ""
        pct = self.casos_similares[0].similitud_coseno * 100
        if pct >= 95:   return "Excelente"
        if pct >= 85:   return "Muy alto"
        if pct >= 70:   return "Alto"
        if pct >= 55:   return "Moderado"
        return "Bajo"

    # Color del nivel
    @rx.var
    def color_match(self) -> str:
        if not self.casos_similares:
            return MUTED
        pct = self.casos_similares[0].similitud_coseno * 100
        if pct >= 85:   return "#34D399"
        if pct >= 60:   return "#38BDF8"
        return "#94A3B8"


# ── CSS ───────────────────────────────────────────────────────────────────────
GLOBAL_CSS = (
    ".rt-SliderTrack{background:#1C2D44!important;height:3px!important;border-radius:99px!important}"
    ".rt-SliderRange{background:#38BDF8!important;height:100%!important;border-radius:99px!important}"
    ".rt-SliderThumb{background:#fff!important;border:2.5px solid #38BDF8!important;"
    "width:13px!important;height:13px!important;border-radius:50%!important;"
    "box-shadow:0 0 0 3px rgba(56,189,248,0.15)!important;cursor:pointer!important;transition:all .15s!important}"
    ".rt-SliderThumb:hover{box-shadow:0 0 0 5px rgba(56,189,248,0.25)!important;outline:none!important}"
    "*::-webkit-scrollbar{width:4px}"
    "*::-webkit-scrollbar-track{background:transparent}"
    "*::-webkit-scrollbar-thumb{background:#243044;border-radius:4px}"
)

SLIDER_ICONOS = {
    "matematica":   "sigma",
    "logica":       "cpu",
    "comunicacion": "message-square",
    "creatividad":  "pen-tool",
    "ciencias":     "atom",
    "liderazgo":    "users",
}

SLIDER_LABELS = {
    "matematica":   "Matemática",
    "logica":       "Lógica",
    "comunicacion": "Comunicación",
    "creatividad":  "Creatividad",
    "ciencias":     "Ciencias",
    "liderazgo":    "Liderazgo",
}


# ── Componentes base ──────────────────────────────────────────────────────────

def tag_tech(texto: str) -> rx.Component:
    return rx.box(
        rx.text(texto, size="1", color=CYAN, weight="medium"),
        padding_x="8px", padding_y="3px",
        background=CYAN_D,
        border=f"1px solid {CYAN}22",
        border_radius="4px",
        display="inline-flex",
    )


def seccion(titulo: str, icono: str, contenido: rx.Component) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.icon(icono, size=14, color=CYAN),
            rx.text(titulo, size="2", color=MUTED2, weight="medium"),
            rx.spacer(),
            rx.box(width="20px", height="1px", background=BORDER),
            align="center", width="100%",
            margin_bottom="16px",
        ),
        contenido,
        padding="20px 22px",
        border=f"1px solid {BORDER}",
        border_top=f"1px solid {CYAN}33",
        border_radius="10px",
        background=PANEL,
        width="100%",
    )


def slider_field(atributo: str, valor) -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.icon(SLIDER_ICONOS.get(atributo, "circle"), size=13, color=MUTED),
            rx.text(SLIDER_LABELS.get(atributo, atributo), size="2", color=MUTED2),
            rx.spacer(),
            rx.text(valor[0].to(int), size="2", weight="bold", color=CYAN),
            width="100%", align="center",
        ),
        rx.slider(
            min=1, max=10, step=1, default_value=[5],
            on_change=getattr(State, f"set_{atributo}"),
            color_scheme="sky",
            width="100%",
        ),
        spacing="1", width="100%",
    )


def barra_progreso(pct: rx.Var, color: str, height: str = "6px") -> rx.Component:
    """Barra de progreso visual simple."""
    return rx.box(
        rx.box(
            width=pct.to(str) + "%",
            height=height,
            background=color,
            border_radius="99px",
            transition="width 0.6s ease",
        ),
        width="100%",
        height=height,
        background=PANEL2,
        border_radius="99px",
        overflow="hidden",
    )


def fila_graduado(c, posicion: int) -> rx.Component:
    """Fila de tabla amigable con barra visual de coincidencia."""
    pct_var = (c.similitud_coseno * 100).to(int)
    return rx.table.row(
        # Posicion
        rx.table.cell(
            rx.box(
                rx.text(str(posicion), size="1", weight="bold", color=MUTED),
                width="22px", height="22px",
                border=f"1px solid {BORDER}",
                border_radius="4px",
                background=PANEL2,
                display="flex",
                align_items="center",
                justify_content="center",
            )
        ),
        # Nombre
        rx.table.cell(
            rx.vstack(
                rx.text(c.nombre, size="2", weight="medium", color=INK),
                rx.text(c.carrera, size="1", color=MUTED2),
                spacing="0", align="start",
            )
        ),
        # Barra de coincidencia visual
        rx.table.cell(
            rx.vstack(
                rx.hstack(
                    rx.text("Coincidencia", size="1", color=MUTED),
                    rx.spacer(),
                    rx.text(
                        pct_var.to(str) + "%",
                        size="1", weight="bold", color=CYAN,
                    ),
                    width="100%",
                ),
                barra_progreso(c.similitud_coseno * 100, CYAN, "5px"),
                spacing="1",
                width="100%",
                min_width="140px",
            )
        ),
    )


# ── Resultados ────────────────────────────────────────────────────────────────

def seccion_resultados() -> rx.Component:
    return rx.cond(
        State.carrera_recomendada != "",
        rx.vstack(

            # Separador
            rx.hstack(
                rx.box(flex="1", height="1px", background=BORDER),
                rx.text("resultados", size="1", color=MUTED),
                rx.box(flex="1", height="1px", background=BORDER),
                spacing="3", align="center", width="100%",
            ),

            # Carrera recomendada
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("graduation-cap", size=14, color=CYAN),
                        rx.text("Carrera recomendada", size="2", color=MUTED2),
                        spacing="2", align="center",
                    ),
                    rx.heading(
                        State.carrera_recomendada,
                        size="8", color=INK, weight="bold",
                        letter_spacing="-0.03em",
                    ),
                    # Indicador de nivel de match
                    rx.hstack(
                        rx.box(
                            width="8px", height="8px",
                            border_radius="50%",
                            background=State.color_match,
                        ),
                        rx.text(
                            "Nivel de coincidencia: ",
                            size="2", color=MUTED2,
                        ),
                        rx.text(
                            State.nivel_match,
                            size="2", weight="bold",
                            color=State.color_match,
                        ),
                        rx.text("·", size="2", color=MUTED),
                        rx.text(
                            State.pct_similitud.to(str) + "% de similitud con el graduado más cercano",
                            size="2", color=MUTED2,
                        ),
                        spacing="1", align="center",
                    ),
                    spacing="2", width="100%",
                ),
                padding="24px",
                border=f"1px solid {BORDER}",
                border_radius="10px",
                background=PANEL,
                border_left=f"3px solid {CYAN}",
                width="100%",
            ),

            # Analisis IA
            seccion(
                "Por qué esta carrera es para ti", "sparkles",
                rx.text(State.explicacion_ia, size="2", color=MUTED2, line_height="1.8"),
            ),

            # Radar
            seccion(
                "Tu perfil vs. graduado más similar", "radar",
                rx.plotly(data=State.grafico_radar, width="100%"),
            ),

            # Tabla amigable
            seccion(
                "Graduados más parecidos a ti", "users",
                rx.vstack(
                    rx.text(
                        "El sistema encontró estos 3 graduados exitosos cuyo perfil de habilidades "
                        "se parece más al tuyo:",
                        size="2", color=MUTED, line_height="1.6",
                    ),
                    rx.table.root(
                        rx.table.body(
                            rx.table.row(
                                rx.table.cell(rx.text("#", size="1", color=MUTED, weight="medium")),
                                rx.table.cell(rx.text("Graduado / Carrera", size="1", color=MUTED, weight="medium")),
                                rx.table.cell(rx.text("Qué tan parecido es a ti", size="1", color=MUTED, weight="medium")),
                            ),
                            fila_graduado(State.casos_similares[0], 1),
                            fila_graduado(State.casos_similares[1], 2),
                            fila_graduado(State.casos_similares[2], 3),
                        ),
                        variant="ghost", width="100%",
                    ),
                    spacing="3", width="100%",
                ),
            ),

            # Boton retener
            rx.cond(
                ~State.caso_retenido,
                rx.button(
                    rx.icon("bookmark-check", size=14),
                    "Esta es mi carrera — guardar mi perfil",
                    on_click=State.confirmar_y_retener,
                    size="3", width="100%",
                    color_scheme="sky",
                    variant="outline",
                    border_radius="8px",
                    cursor="pointer",
                ),
                rx.hstack(
                    rx.icon("circle-check", size=15, color=GREEN),
                    rx.text("Tu perfil fue guardado. ¡Gracias por confirmar!",
                            size="2", color=GREEN, weight="medium"),
                    padding="14px 18px",
                    border=f"1px solid {GREEN}30",
                    border_radius="8px",
                    background=GREEN_D,
                    width="100%", align="center", spacing="2",
                ),
            ),

            spacing="4", width="100%",
        ),
        rx.box(),
    )


# ── Pagina ────────────────────────────────────────────────────────────────────
def index() -> rx.Component:
    return rx.fragment(
        rx.el.style(GLOBAL_CSS),
        rx.box(
            rx.center(
                rx.vstack(

                    # Navbar
                    rx.hstack(
                        rx.hstack(
                            rx.box(
                                rx.box(width="7px", height="7px",
                                       border_radius="50%", background=CYAN,
                                       box_shadow=f"0 0 10px {CYAN}80"),
                                width="28px", height="28px",
                                border_radius="6px",
                                border=f"1px solid {BORDER}",
                                background=PANEL2,
                                display="flex",
                                align_items="center",
                                justify_content="center",
                            ),
                            rx.text("CRUC-Memory", size="2", weight="bold", color=INK),
                            spacing="2", align="center",
                        ),
                        rx.spacer(),
                        tag_tech("CBR  ●  activo"),
                        width="100%", align="center",
                        padding_y="14px",
                        border_bottom=f"1px solid {BORDER}",
                        margin_bottom="8px",
                    ),

                    # Hero
                    rx.vstack(
                        rx.heading(
                            "Orientación Vocacional",
                            size="8", color=INK, weight="bold",
                            letter_spacing="-0.04em",
                        ),
                        rx.text(
                            "Ajusta tus habilidades y encontraremos la carrera que mejor "
                            "encaja con tu perfil, comparándote con graduados exitosos.",
                            size="2", color=MUTED2, max_width="52ch",
                            line_height="1.7",
                        ),
                        spacing="2", align="start", width="100%",
                        padding_bottom="4px",
                    ),

                    # Sliders
                    seccion(
                        "¿Qué tan bueno eres en cada área?", "sliders-horizontal",
                        rx.vstack(
                            rx.text(
                                "Mueve cada barra según cómo te evalúas del 1 al 10.",
                                size="2", color=MUTED, margin_bottom="8px",
                            ),
                            rx.grid(
                                slider_field("matematica",   State.matematica),
                                slider_field("logica",       State.logica),
                                slider_field("comunicacion", State.comunicacion),
                                slider_field("creatividad",  State.creatividad),
                                slider_field("ciencias",     State.ciencias),
                                slider_field("liderazgo",    State.liderazgo),
                                columns="2", spacing="5", width="100%",
                            ),
                            rx.box(height="4px"),
                            rx.button(
                                rx.cond(
                                    State.loading,
                                    rx.hstack(rx.spinner(size="2"),
                                              rx.text("Buscando tu carrera ideal..."),
                                              spacing="2", align="center"),
                                    rx.hstack(rx.icon("search", size=14),
                                              rx.text("Encontrar mi carrera"),
                                              spacing="2", align="center"),
                                ),
                                on_click=State.consultar,
                                loading=State.loading,
                                size="3", width="100%",
                                background=CYAN,
                                color=BG,
                                border_radius="8px",
                                cursor="pointer",
                                font_weight="600",
                                _hover={"background": "#7DD3FC"},
                            ),
                            spacing="3", width="100%",
                        ),
                    ),

                    seccion_resultados(),

                    spacing="4",
                    width="100%",
                    max_width="820px",
                    padding_y="28px",
                    padding_x="18px",
                    align="start",
                ),
                width="100%",
            ),
            background=BG,
            min_height="100vh",
            width="100%",
        ),
    )


app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="sky",
        gray_color="slate",
        radius="medium",
    ),
    stylesheets=[
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    style={"font_family": "Inter, sans-serif", "color": INK},
)
app.add_page(index)