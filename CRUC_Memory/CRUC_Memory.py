import reflex as rx
import plotly.graph_objects as go
from pydantic import BaseModel
from CRUC_Memory.cbr_engine import cargar_casos, retrieve, reuse, retain, ATRIBUTOS
from CRUC_Memory.ia_service import explicar_recomendacion

# ── Tema de colores ──────────────────────────────────────────────────────────
ACCENT  = "#E9B84A"   # dorado cálido
BG      = "#080C14"   # fondo casi negro
PANEL   = "#0F1623"   # tarjeta oscura
BORDER  = "rgba(255,255,255,0.08)"
INK     = "#EDF0F7"
MUTED   = "#8A95A8"
GREEN   = "#22C98A"
PURPLE  = "#9B8AFF"


# ── Modelos de datos ─────────────────────────────────────────────────────────
class CasoSimilar(BaseModel):
    nombre: str
    carrera: str
    distancia_euclidiana: float
    similitud_coseno: float
    vector: list[float]


# ── Estado global ────────────────────────────────────────────────────────────
class State(rx.State):
    matematica:   list[float] = [5]
    logica:       list[float] = [5]
    comunicacion: list[float] = [5]
    creatividad:  list[float] = [5]
    ciencias:     list[float] = [5]
    liderazgo:    list[float] = [5]

    casos_similares:    list[CasoSimilar] = []
    carrera_recomendada: str  = ""
    explicacion_ia:      str  = ""
    loading:             bool = False
    caso_retenido:       bool = False

    # Setters para cada slider
    def set_matematica(self, v):   self.matematica   = v
    def set_logica(self, v):       self.logica       = v
    def set_comunicacion(self, v): self.comunicacion = v
    def set_creatividad(self, v):  self.creatividad  = v
    def set_ciencias(self, v):     self.ciencias     = v
    def set_liderazgo(self, v):    self.liderazgo    = v

    @property
    def _perfil(self) -> dict:
        """Construye el diccionario de perfil del estudiante."""
        return {
            "matematica":   int(self.matematica[0]),
            "logica":       int(self.logica[0]),
            "comunicacion": int(self.comunicacion[0]),
            "creatividad":  int(self.creatividad[0]),
            "ciencias":     int(self.ciencias[0]),
            "liderazgo":    int(self.liderazgo[0]),
        }

    def consultar(self):
        """Ejecuta el ciclo CBR: Retrieve → Reuse → explicación IA."""
        self.loading      = True
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
        """Fase Retain: guarda el nuevo caso en la memoria CBR."""
        retain(self._perfil, self.carrera_recomendada)
        self.caso_retenido = True

    @rx.var
    def grafico_radar(self) -> go.Figure:
        """Gráfico radar: perfil del estudiante vs. caso más similar."""
        vals = [int(self.matematica[0]), int(self.logica[0]), int(self.comunicacion[0]),
                int(self.creatividad[0]), int(self.ciencias[0]), int(self.liderazgo[0])]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=vals + [vals[0]], theta=ATRIBUTOS + [ATRIBUTOS[0]],
            fill="toself", name="Tu perfil",
            line_color=PURPLE, fillcolor="rgba(155,138,255,0.25)",
        ))
        if self.casos_similares:
            v = self.casos_similares[0].vector
            fig.add_trace(go.Scatterpolar(
                r=v + [v[0]], theta=ATRIBUTOS + [ATRIBUTOS[0]],
                fill="toself", name=self.casos_similares[0].nombre,
                line_color=GREEN, fillcolor="rgba(34,201,138,0.18)",
            ))
        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=MUTED, size=11),
            margin=dict(l=40, r=40, t=40, b=40),
            height=340,
        )
        return fig


# ── Componentes de UI ────────────────────────────────────────────────────────

def slider_field(label: str, atributo: str, valor) -> rx.Component:
    """Un slider con etiqueta y badge de valor."""
    return rx.vstack(
        rx.hstack(
            rx.text(label, size="2", color=MUTED),
            rx.spacer(),
            rx.badge(valor[0].to(int), variant="soft", color_scheme="violet"),
            width="100%",
        ),
        rx.slider(
            min=1, max=10, step=1,
            default_value=[5],
            on_change=getattr(State, f"set_{atributo}"),
            color_scheme="violet",
            width="100%",
        ),
        spacing="1",
        width="100%",
    )


def tarjeta_carrera() -> rx.Component:
    """Tarjeta principal con la carrera recomendada."""
    return rx.card(
        rx.hstack(
            rx.box(
                rx.icon("graduation-cap", size=20, color=BG),
                background=ACCENT,
                padding="10px",
                border_radius="12px",
            ),
            rx.vstack(
                rx.text("Carrera recomendada", size="1", color=MUTED),
                rx.heading(State.carrera_recomendada, size="5", color=INK),
                spacing="0",
                align="start",
            ),
            spacing="3",
            align="center",
            width="100%",
        ),
        background=PANEL,
        border=f"1px solid {BORDER}",
        width="100%",
    )


def tarjeta_ia() -> rx.Component:
    """Tarjeta con la explicación generada por IA."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("sparkles", size=18, color=ACCENT),
                rx.text("Análisis IA", weight="bold", color=INK),
                spacing="2",
                align="center",
            ),
            rx.separator(color=BORDER),
            rx.text(State.explicacion_ia, size="2", color=MUTED, line_height="1.7"),
            spacing="3",
            width="100%",
        ),
        background=PANEL,
        border=f"1px solid {BORDER}",
        width="100%",
    )


def tabla_casos() -> rx.Component:
    """Tabla con los 3 graduados más similares."""
    return rx.cond(
        State.casos_similares,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    *[rx.table.column_header_cell(h) for h in
                      ["Graduado", "Carrera", "Dist. Euclidiana", "Similitud Coseno"]]
                )
            ),
            rx.table.body(
                rx.foreach(
                    State.casos_similares,
                    lambda c: rx.table.row(
                        rx.table.cell(c.nombre),
                        rx.table.cell(c.carrera),
                        rx.table.cell(c.distancia_euclidiana),
                        rx.table.cell(c.similitud_coseno),
                    ),
                )
            ),
            variant="surface",
            width="100%",
        ),
        rx.box(),
    )


def seccion_resultados() -> rx.Component:
    """Sección de resultados que aparece tras la consulta."""
    return rx.cond(
        State.carrera_recomendada != "",
        rx.vstack(
            rx.separator(color=BORDER),
            rx.hstack(
                rx.icon("chart-bar", size=16, color=ACCENT),
                rx.text("Resultados", weight="bold", size="4", color=INK),
                spacing="2", align="center", justify="center", width="100%",
            ),
            tarjeta_carrera(),
            tarjeta_ia(),

            # Gráfico radar
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("radar", size=16, color=ACCENT),
                        rx.text("Gráfico de similitud", weight="bold", color=INK),
                        spacing="2", align="center",
                    ),
                    rx.plotly(data=State.grafico_radar, width="100%"),
                    spacing="3", width="100%",
                ),
                background=PANEL,
                border=f"1px solid {BORDER}",
                width="100%",
            ),

            # Tabla de casos similares
            rx.card(
                rx.vstack(
                    rx.hstack(
                        rx.icon("users", size=16, color=ACCENT),
                        rx.text("Casos más similares (k=3)", weight="bold", color=INK),
                        spacing="2", align="center",
                    ),
                    tabla_casos(),
                    spacing="3", width="100%",
                ),
                background=PANEL,
                border=f"1px solid {BORDER}",
                width="100%",
            ),

            # Botón de retención o confirmación
            rx.cond(
                ~State.caso_retenido,
                rx.button(
                    rx.icon("bookmark-check", size=16),
                    "Confirmar carrera y guardar mi caso",
                    on_click=State.confirmar_y_retener,
                    size="3", width="100%",
                    color_scheme="amber",
                    variant="solid",
                    border_radius="12px",
                ),
                rx.callout(
                    "Tu caso fue guardado en la memoria CBR correctamente.",
                    icon="circle-check",
                    color_scheme="green",
                    variant="surface",
                    width="100%",
                ),
            ),

            spacing="4", width="100%", align="center",
        ),
        rx.box(),
    )


# ── Página principal ─────────────────────────────────────────────────────────

def index() -> rx.Component:
    return rx.box(
        rx.center(
            rx.vstack(

                # ── Header ──────────────────────────────────────────────────
                rx.vstack(
                    rx.hstack(
                        rx.box(
                            rx.icon("graduation-cap", size=18, color=BG),
                            background=ACCENT,
                            padding="10px",
                            border_radius="999px",
                        ),
                        rx.text("CRUC-Memory", size="4", weight="bold", color=INK),
                        spacing="2", align="center", justify="center",
                    ),
                    rx.heading(
                        "Orientación Vocacional por Similitud",
                        size="8", color=INK,
                        text_align="center",
                        letter_spacing="-0.03em",
                    ),
                    rx.text(
                        "Compara tu perfil con graduados exitosos usando CBR + IA",
                        size="3", color=MUTED, text_align="center",
                    ),
                    align="center", spacing="3", width="100%",
                    padding="28px",
                    background=PANEL,
                    border=f"1px solid {BORDER}",
                    border_radius="18px",
                ),

                # ── Sliders ──────────────────────────────────────────────────
                rx.card(
                    rx.vstack(
                        rx.hstack(
                            rx.hstack(
                                rx.icon("sliders-horizontal", size=16, color=ACCENT),
                                rx.text("Tu perfil de habilidades", weight="bold", color=INK),
                                spacing="2", align="center",
                            ),
                            rx.spacer(),
                            rx.badge("Escala 1 – 10", variant="outline", color_scheme="gray"),
                            width="100%", align="center",
                        ),
                        rx.separator(color=BORDER),
                        rx.grid(
                            slider_field("Matemática",    "matematica",   State.matematica),
                            slider_field("Lógica",        "logica",       State.logica),
                            slider_field("Comunicación",  "comunicacion", State.comunicacion),
                            slider_field("Creatividad",   "creatividad",  State.creatividad),
                            slider_field("Ciencias",      "ciencias",     State.ciencias),
                            slider_field("Liderazgo",     "liderazgo",    State.liderazgo),
                            columns="2",
                            spacing="5",
                            width="100%",
                        ),
                        rx.button(
                            rx.cond(
                                State.loading,
                                rx.hstack(rx.spinner(size="2"), rx.text("Analizando…"), spacing="2"),
                                rx.hstack(rx.icon("search", size=16), rx.text("Encontrar mi carrera"), spacing="2"),
                            ),
                            on_click=State.consultar,
                            loading=State.loading,
                            size="3",
                            width="100%",
                            color_scheme="amber",
                            variant="solid",
                            border_radius="12px",
                        ),
                        spacing="4", width="100%",
                    ),
                    background=PANEL,
                    border=f"1px solid {BORDER}",
                    width="100%",
                ),

                # ── Resultados ───────────────────────────────────────────────
                seccion_resultados(),

                spacing="5",
                width="100%",
                max_width="860px",
                padding_y="36px",
                padding_x="18px",
                align="center",
            ),
            width="100%",
        ),
        background=BG,
        min_height="100vh",
        width="100%",
    )


# ── App ───────────────────────────────────────────────────────────────────────
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="amber",
        gray_color="slate",
        radius="medium",
    ),
    stylesheets=["https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;600;800&display=swap"],
    style={"font_family": "DM Sans, sans-serif", "color": INK},
)
app.add_page(index)