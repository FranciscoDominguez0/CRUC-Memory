import pandas as pd
import numpy as np
from scipy.spatial.distance import euclidean, cosine

ATRIBUTOS = ["matematica", "logica", "comunicacion", "creatividad", "ciencias", "liderazgo"]

def cargar_casos(ruta: str = "CRUC_Memory/casos.csv"):
    return pd.read_csv(ruta)

def retrieve(nuevo_perfil: dict, df: pd.DataFrame, k=3):
    """Fase 1 — Recuperar los k casos más similares."""
    nuevo_vec = np.array([nuevo_perfil[a] for a in ATRIBUTOS], dtype=float)
    
    resultados = []
    for _, row in df.iterrows():
        caso_vec = np.array([row[a] for a in ATRIBUTOS], dtype=float)
        
        dist_euc = euclidean(nuevo_vec, caso_vec)
        # similitud coseno: 1 = idénticos, 0 = ortogonales
        sim_cos = 1 - cosine(nuevo_vec, caso_vec) if np.any(caso_vec) else 0
        
        resultados.append({
            "nombre": row["nombre"],
            "carrera": row["carrera"],
            "distancia_euclidiana": round(dist_euc, 3),
            "similitud_coseno": round(sim_cos, 4),
            "vector": caso_vec.tolist()
        })
    
    # Ordenar por distancia euclidiana (menor = más similar)
    resultados.sort(key=lambda x: x["distancia_euclidiana"])
    return resultados[:k]

def reuse(casos_similares: list):
    """Fase 2 — Reutilizar: la carrera del caso más cercano es la sugerencia."""
    caso0 = casos_similares[0]
    return caso0.carrera if hasattr(caso0, "carrera") else caso0["carrera"]

def retain(nuevo_perfil: dict, carrera_confirmada: str, ruta="CRUC_Memory/casos.csv"):
    """Fase 4 — Retener: guardar el nuevo caso en la base de datos."""
    df = cargar_casos(ruta)
    nueva_fila = {**nuevo_perfil, "nombre": "Nuevo_" + str(len(df)+1), "carrera": carrera_confirmada}
    df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
    df.to_csv(ruta, index=False)
    return df