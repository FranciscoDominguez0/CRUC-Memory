# CRUC-Memory: Orientacion Vocacional por Similitud

Sistema de orientacion vocacional basado en Razonamiento Basado en Casos (CBR) con explicaciones generadas por inteligencia artificial. Desarrollado como proyecto academico del Tema 8 para el Centro Regional Universitario de Cocle (CRUC), Panama.

---

## El Problema: Orientacion sin Precedentes

Muchos estudiantes ingresan al CRUC sin saber que carrera elegir. En lugar de usar un test psicotecnico rigido, este sistema utiliza CBR para comparar el perfil del nuevo estudiante con casos de exito de graduados reales, ofreciendo una recomendacion explicable y fundamentada en datos historicos.

---

## Ciclo de Vida del CBR

El sistema implementa las 4 etapas del ciclo CBR:

1. **Retrieve (Recuperar):** Busca en la base de datos los casos mas parecidos al perfil del usuario mediante Distancia Euclidiana y Similitud de Coseno.
2. **Reuse (Reutilizar):** Aplica la solucion (carrera) del caso historico mas similar al nuevo estudiante.
3. **Revise (Revisar):** Genera una explicacion mediante IA (Gemini) que justifica por que la carrera recomendada es apropiada segun el perfil.
4. **Retain (Retener):** Permite al usuario confirmar la recomendacion y guardar su perfil como nuevo caso en la memoria del sistema para consultas futuras.

---

## Implementacion Tecnologica

El sistema representa cada perfil estudiantil como un vector de seis atributos en escala del 1 al 10:

- Matematica
- Logica
- Comunicacion
- Creatividad
- Ciencias
- Liderazgo

La similitud entre perfiles se calcula usando **Distancia Euclidiana** y **Similitud de Coseno** mediante la libreria `scipy`. Los 3 casos mas similares (K-Nearest Neighbors) se presentan en una tabla con sus metricas de similitud y un grafico radar comparativo.

---

## Tecnologias Utilizadas

| Tecnologia | Funcion |
|---|---|
| Reflex | Framework web full-stack en Python |
| pandas | Manejo de la base de casos (CSV) |
| scipy | Calculo de distancias y similitud |
| plotly | Grafico radar de similitud |
| google-genai | Explicacion de la recomendacion por IA |
| python-dotenv | Gestion de variables de entorno |

---

## Requisitos Previos

- Python 3.10 o superior
- Node.js 18 o superior (requerido por Reflex para el frontend)
- Git

---

## Instalacion

**1. Clonar el repositorio**

```bash
git clone https://github.com/TU_USUARIO/CRUC-Memory.git
cd CRUC-Memory
```

**2. Crear y activar el entorno virtual**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS / Linux:
```bash
python -m venv venv
source venv/bin/activate
```

**3. Instalar dependencias**

```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno**

Crear un archivo `.env` en la raiz del proyecto con el siguiente contenido:

```
GEMINI_API_KEY=tu_clave_de_api_aqui
```

La clave de API de Gemini se obtiene de forma gratuita en: https://aistudio.google.com/app/apikey

**5. Ejecutar la aplicacion**

```bash
reflex run
```

La aplicacion estara disponible en `http://localhost:3000`.

---

## Estructura del Proyecto

```
CRUC-Memory/
├── CRUC_Memory/
│   ├── CRUC_Memory.py     # Interfaz principal
│   ├── cbr_engine.py      # Motor CBR (Retrieve, Reuse, Retain)
│   ├── ia_service.py      # Integracion con Gemini AI (Revise)
│   └── casos.csv          # Base de casos historicos
├── rxconfig.py            # Configuracion de Reflex
├── requirements.txt       # Dependencias del proyecto
└── .env                   # Variables de entorno (no incluido en el repositorio)
```

---

## Actividades de Pensamiento Profundo

1. **Ajuste de Atributos:** Que ocurre si un estudiante tiene valores altos en todos los atributos (10, 10, 10...)? Que carrera le asigna el CBR y por que?

2. **Aprendizaje del Sistema (Retain):** El sistema permite que el usuario confirme la recomendacion. Al confirmar, ese nuevo perfil se agrega automaticamente a la lista de casos para mejorar futuras recomendaciones.

3. **Comparacion Critica:** En que se diferencia el CBR de una Red Neuronal? En el CBR la explicabilidad es total: se sabe exactamente de que caso historico proviene cada recomendacion. Las redes neuronales son cajas negras; el CBR es completamente transparente.

---

## Nota Academica

Este proyecto fue desarrollado como trabajo practico del Tema 8 del curso, aplicando los conceptos de Razonamiento Basado en Casos en un contexto real de orientacion vocacional universitaria.