from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def explicar_recomendacion(perfil: dict, carrera: str, casos_similares: list) -> str:

    def _get(c, key: str):
        return getattr(c, key) if hasattr(c, key) else c[key]

    casos_texto = "\n".join([
        f"- {_get(c, 'nombre')}: {_get(c, 'carrera')} "
        f"(distancia={_get(c, 'distancia_euclidiana')}, similitud={_get(c, 'similitud_coseno')})"
        for c in casos_similares
    ])

    prompt = f"""Eres un orientador vocacional del CRUC (Centro Regional Universitario de Coclé, Panamá).

Un estudiante tiene el siguiente perfil de habilidades (escala 1-10):
- Matemática: {perfil.get('matematica')}
- Lógica: {perfil.get('logica')}
- Comunicación: {perfil.get('comunicacion')}
- Creatividad: {perfil.get('creatividad')}
- Ciencias: {perfil.get('ciencias')}
- Liderazgo: {perfil.get('liderazgo')}
- Vocación Social: {perfil.get('sociales')}
- Humanidades: {perfil.get('humanidades')}

El sistema CBR encontró estos graduados exitosos similares:
{casos_texto}

La carrera recomendada es: {carrera}

Explica en 3-4 oraciones en español, tono amigable y motivador, por qué esta carrera
es una buena opción. Menciona los atributos más destacados del estudiante."""

    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=400,
            temperature=0.7,
        )
    )

    return response.text