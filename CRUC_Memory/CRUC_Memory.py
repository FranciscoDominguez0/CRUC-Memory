import reflex as rx
import plotly.graph_objects as go
from pydantic import BaseModel
from CRUC_Memory.cbr_engine import cargar_casos, retrieve, reuse, retain, ATRIBUTOS
from CRUC_Memory.ia_service import explicar_recomendacion


def _svg_data_uri(svg: str) -> str:
    return "data:image/svg+xml;utf8," + (
        svg.replace("\n", "").replace("#", "%23").replace('"', "'").strip()
    )


def svg_icon(name: str, size: str = "18px"):
    stroke = "%23E6E9F0"
    if name == "cap":
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>
          <path d='M12 3 1 9l11 6 11-6-11-6Z'/>
          <path d='M5 12v5c0 1 3 3 7 3s7-2 7-3v-5'/>
          <path d='M22 9v6'/>
        </svg>
        """
    elif name == "spark":
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>
          <path d='M12 2l1.2 5.2L18 9l-4.8 1.8L12 16l-1.2-5.2L6 9l4.8-1.8L12 2Z'/>
          <path d='M5 14l.7 3.1L9 18l-3.3 1-.7 3.1-.7-3.1L1 18l3.3-.9L5 14Z'/>
        </svg>
        """
    elif name == "check":
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>
          <path d='M20 6 9 17l-5-5'/>
        </svg>
        """
    else:
        svg = f"""
        <svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' width='{size}' height='{size}' fill='none' stroke='{stroke}' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'>
          <path d='M12 20h.01'/>
          <path d='M10 8a2 2 0 1 1 4 0c0 2-2 2-2 4'/>
          <path d='M12 2a10 10 0 1 0 0 20a10 10 0 1 0 0-20Z'/>
        </svg>
        """
    return rx.image(src=_svg_data_uri(svg), width=size, height=size)


ACCENT = "#D1A954"
INK = "#E6E9F0"
MUTED = "#A7B0C0"
BG = "#0B0F17"
PANEL = "#111827"
PANEL_2 = "#0F172A"
BORDER = "rgba(255,255,255,0.10)"


class CasoSimilar(BaseModel):
    nombre: str
    carrera: str
    distancia_euclidiana: float
    similitud_coseno: float
    vector: list[float]


class State(rx.State):
    matematica: list[float] = [5]
    logica: list[float] = [5]
    comunicacion: list[float] = [5]
    creatividad: list[float] = [5]
    ciencias: list[float] = [5]
    liderazgo: list[float] = [5]

    casos_similares: list[CasoSimilar] = []
    carrera_recomendada: str = ""
    explicacion_ia: str = ""
    loading: bool = False
    caso_retenido: bool = False

    # Setters explícitos para evitar el DeprecationWarning
    def set_matematica(self, val: list[float]):
        self.matematica = val

    def set_logica(self, val: list[float]):
        self.logica = val

    def set_comunicacion(self, val: list[float]):
        self.comunicacion = val

    def set_creatividad(self, val: list[float]):
        self.creatividad = val

    def set_ciencias(self, val: list[float]):
        self.ciencias = val

    def set_liderazgo(self, val: list[float]):
        self.liderazgo = val

    def consultar(self):
        self.loading = True
        self.caso_retenido = False
        yield

        perfil = {
            "matematica": int(self.matematica[0]),
            "logica": int(self.logica[0]),
            "comunicacion": int(self.comunicacion[0]),
            "creatividad": int(self.creatividad[0]),
            "ciencias": int(self.ciencias[0]),
            "liderazgo": int(self.liderazgo[0]),
        }

        df = cargar_casos()
        self.casos_similares = [CasoSimilar(**c) for c in retrieve(perfil, df, k=3)]
        self.carrera_recomendada = reuse(self.casos_similares)
        self.explicacion_ia = explicar_recomendacion(
            perfil, self.carrera_recomendada, self.casos_similares
        )
        self.loading = False

    def confirmar_y_retener(self):
        perfil = {
            "matematica": int(self.matematica[0]),
            "logica": int(self.logica[0]),
            "comunicacion": int(self.comunicacion[0]),
            "creatividad": int(self.creatividad[0]),
            "ciencias": int(self.ciencias[0]),
            "liderazgo": int(self.liderazgo[0]),
        }
        retain(perfil, self.carrera_recomendada)
        self.caso_retenido = True

    # Computed var que devuelve Figure directamente, no string
    @rx.var
    def grafico_radar(self) -> go.Figure:
        perfil = [
            int(self.matematica[0]),
            int(self.logica[0]),
            int(self.comunicacion[0]),
            int(self.creatividad[0]),
            int(self.ciencias[0]),
            int(self.liderazgo[0]),
        ]

        fig = go.Figure()

        fig.add_trace(go.Scatterpolar(
            r=perfil + [perfil[0]],
            theta=ATRIBUTOS + [ATRIBUTOS[0]],
            fill="toself",
            name="Tu perfil",
            line_color="#7F77DD",
            fillcolor="rgba(127,119,221,0.3)",
        ))

        if self.casos_similares:
            vec = self.casos_similares[0].vector
            fig.add_trace(go.Scatterpolar(
                r=vec + [vec[0]],
                theta=ATRIBUTOS + [ATRIBUTOS[0]],
                fill="toself",
                name=self.casos_similares[0].nombre,
                line_color="#1D9E75",
                fillcolor="rgba(29,158,117,0.2)",
            ))

        fig.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=True,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#888", size=11),
            margin=dict(l=40, r=40, t=40, b=40),
            height=350,
        )

        return fig


def slider_con_label(label: str, atributo: str, valor):
    return rx.vstack(
        rx.hstack(
            rx.text(label, font_size="0.9em", color="gray"),
            rx.spacer(),
            rx.badge(
                valor[0].to(int),
                color_scheme="purple",
            ),
            width="100%",
            max_width="300px",
        ),
        rx.slider(
            min=1,
            max=10,
            step=1,
            default_value=[5],
            on_change=getattr(State, f"set_{atributo}"),
            width="100%",
            max_width="300px",
            size="1",
        ),
        width="100%",
        max_width="300px",
        margin_x="auto",
        spacing="1",
    )


def tabla_casos():
    return rx.cond(
        State.casos_similares,
        rx.table.root(
            rx.table.header(
                rx.table.row(
                    rx.table.column_header_cell("Graduado"),
                    rx.table.column_header_cell("Carrera"),
                    rx.table.column_header_cell("Dist. Euclidiana"),
                    rx.table.column_header_cell("Similitud coseno"),
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
        rx.text(""),
    )


_SLIDER_CSS = """
.rt-SliderTrack {
  height: 2px !important;
  background: rgba(255,255,255,0.12) !important;
  border-radius: 99px !important;
}
.rt-SliderRange {
  background: #D1A954 !important;
  border-radius: 99px !important;
  height: 100% !important;
}
.rt-SliderThumb {
  width: 7px !important;
  height: 7px !important;
  background: #ffffff !important;
  border: 1.5px solid #D1A954 !important;
  border-radius: 50% !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
  cursor: pointer !important;
}
.rt-SliderThumb:hover, .rt-SliderThumb:focus {
  transform: scale(1.3) !important;
  outline: none !important;
}
"""


def index():
    return rx.fragment(
        rx.el.style(_SLIDER_CSS),
        rx.box(
        rx.center(
            rx.box(
                rx.vstack(
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.box(
                                    svg_icon("cap", size="18px"),
                                    padding="10px",
                                    border=f"1px solid {BORDER}",
                                    border_radius="999px",
                                    background=ACCENT,
                                    display="flex",
                                    align_items="center",
                                    justify_content="center",
                                    box_shadow="0 10px 30px rgba(0, 0, 0, 0.45)",
                                ),
                                rx.text(
                                    "CRUC-Memory",
                                    font_size="1.1rem",
                                    font_weight="700",
                                    letter_spacing="-0.02em",
                                    color=INK,
                                ),
                                spacing="3",
                                align="center",
                                justify="center",
                                width="100%",
                            ),
                            rx.heading(
                                "Orientación vocacional basada en similitud",
                                size="8",
                                color=INK,
                                letter_spacing="-0.03em",
                                text_align="center",
                                width="100%",
                            ),
                            rx.text(
                                "Analiza tu perfil de habilidades y te recomienda una carrera usando CBR + explicación asistida.",
                                color=MUTED,
                                max_width="48ch",
                                text_align="center",
                            ),
                            spacing="3",
                            width="100%",
                            align="center",
                        ),
                        padding="28px",
                        border=f"1px solid {BORDER}",
                        border_radius="18px",
                        background=PANEL,
                        box_shadow="0 12px 40px rgba(0, 0, 0, 0.55)",
                        width="100%",
                    ),
                    rx.box(
                        rx.vstack(
                            rx.hstack(
                                rx.text(
                                    "Tu perfil de habilidades",
                                    font_weight="700",
                                    color=INK,
                                    font_size="1.05rem",
                                ),
                                rx.spacer(),
                                rx.text("Escala 1–10", color=MUTED, font_size="0.9rem"),
                                width="100%",
                                align="center",
                            ),
                            rx.grid(
                                slider_con_label("Matemática", "matematica", State.matematica),
                                slider_con_label("Lógica", "logica", State.logica),
                                slider_con_label("Comunicación", "comunicacion", State.comunicacion),
                                slider_con_label("Creatividad", "creatividad", State.creatividad),
                                slider_con_label("Ciencias", "ciencias", State.ciencias),
                                slider_con_label("Liderazgo", "liderazgo", State.liderazgo),
                                columns="2",
                                spacing="4",
                                width="100%",
                            ),
                            rx.button(
                                rx.cond(
                                    State.loading,
                                    "Analizando…",
                                    "Encontrar mi carrera",
                                ),
                                on_click=State.consultar,
                                loading=State.loading,
                                size="3",
                                width="100%",
                                background=ACCENT,
                                color="#0B0F17",
                                border_radius="14px",
                                _hover={"filter": "brightness(1.03)"},
                            ),
                            spacing="4",
                            width="100%",
                        ),
                        padding="24px",
                        border=f"1px solid {BORDER}",
                        border_radius="18px",
                        background=PANEL_2,
                        box_shadow="0 10px 30px rgba(0, 0, 0, 0.55)",
                        width="100%",
                    ),
                    rx.cond(
                        State.carrera_recomendada != "",
                        rx.vstack(
                            rx.box(height="1px", width="100%", background=BORDER),
                            rx.text("Resultados", font_weight="800", color=INK, font_size="1.25rem", text_align="center", width="100%"),
                            rx.box(
                                rx.hstack(
                                    rx.box(
                                        svg_icon("cap", size="18px"),
                                        padding="10px",
                                        border_radius="14px",
                                        background=ACCENT,
                                        display="flex",
                                        align_items="center",
                                        justify_content="center",
                                    ),
                                    rx.vstack(
                                        rx.text("Carrera recomendada", color=MUTED, font_size="0.9rem"),
                                        rx.text(State.carrera_recomendada, font_weight="800", color=INK, font_size="1.1rem"),
                                        spacing="1",
                                        align="start",
                                    ),
                                    spacing="3",
                                    align="center",
                                    width="100%",
                                ),
                                padding="18px",
                                border=f"1px solid {BORDER}",
                                border_radius="18px",
                                background=PANEL,
                                width="100%",
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.hstack(
                                        rx.box(
                                            svg_icon("spark", size="18px"),
                                            padding="10px",
                                            border_radius="14px",
                                            background=ACCENT,
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                        rx.text("Análisis", font_weight="800", color=INK),
                                        spacing="3",
                                        align="center",
                                    ),
                                    rx.text(State.explicacion_ia, color=MUTED),
                                    spacing="3",
                                    width="100%",
                                ),
                                padding="18px",
                                border=f"1px solid {BORDER}",
                                border_radius="18px",
                                background=PANEL_2,
                                width="100%",
                            ),
                            rx.hstack(
                                rx.box(
                                    rx.vstack(
                                        rx.text("Gráfico de similitud", font_weight="800", color=INK),
                                        rx.plotly(data=State.grafico_radar, width="100%"),
                                        spacing="3",
                                        width="100%",
                                    ),
                                    padding="18px",
                                    border=f"1px solid {BORDER}",
                                    border_radius="18px",
                                    background=PANEL_2,
                                    width="100%",
                                ),
                                width="100%",
                            ),
                            rx.box(
                                rx.vstack(
                                    rx.text("Casos más similares", font_weight="800", color=INK),
                                    tabla_casos(),
                                    spacing="3",
                                    width="100%",
                                ),
                                padding="18px",
                                border=f"1px solid {BORDER}",
                                border_radius="18px",
                                background=PANEL_2,
                                width="100%",
                            ),
                            rx.cond(
                                ~State.caso_retenido,
                                rx.button(
                                    "Confirmar carrera y guardar mi caso",
                                    on_click=State.confirmar_y_retener,
                                    variant="solid",
                                    size="3",
                                    width="100%",
                                    background=ACCENT,
                                    color="#0B0F17",
                                    border_radius="14px",
                                    _hover={"filter": "brightness(1.03)"},
                                ),
                                rx.box(
                                    rx.hstack(
                                        rx.box(
                                            svg_icon("check", size="18px"),
                                            padding="10px",
                                            border_radius="14px",
                                            background=ACCENT,
                                            display="flex",
                                            align_items="center",
                                            justify_content="center",
                                        ),
                                        rx.text(
                                            "Tu caso fue guardado correctamente.",
                                            font_weight="700",
                                            color=INK,
                                        ),
                                        spacing="3",
                                        align="center",
                                    ),
                                    padding="16px",
                                    border=f"1px solid {BORDER}",
                                    border_radius="18px",
                                    background=PANEL,
                                    width="100%",
                                ),
                            ),
                            spacing="4",
                            width="100%",
                            align="center",
                        ),
                        rx.box(),
                    ),
                    spacing="4",
                    width="100%",
                    padding_y="28px",
                    align="center",
                ),
                max_width="980px",
                width="100%",
                margin_x="auto",
                padding_x="18px",
            ),
            width="100%",
        ),
        background=BG,
        min_height="100vh",
        width="100%",
        padding_x="0px",
    ),
    )


app = rx.App(
    style={
        "font_family": "Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial",
        "color": INK,
    }
)
app.add_page(index)