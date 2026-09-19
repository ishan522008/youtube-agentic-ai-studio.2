"""
Script Writer Agent — Spanish Latin American tutorials about AI for office professionals.
Uses Groq (via agents.gemini_client) with simple JSON parsing and retries.
Target duration: 4-6 minutes.
"""
import json
import re
import time
from agents.gemini_client import generate


def _clean_json_response(raw: str) -> str:
    """Limpia la respuesta del LLM para que sea JSON parseable."""
    if not raw:
        return ""

    text = raw.strip()

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```\s*$", "", text)

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)

    return text.strip()

def _try_parse_json(raw: str) -> dict:
    """Intenta parsear el JSON. Si falla, intenta varios arreglos."""
    cleaned = _clean_json_response(raw)

    # Intento 1: parseo directo
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        print(f"   JSON error en intento 1: {e}")

    # Intento 2: arreglar saltos de linea mal escapados (\n dentro de strings)
    try:
        # Reemplazar \n literales (no escapados) dentro de strings por \\n
        # Busca: dentro de strings, todo \n que NO vaya precedido de \\
        fixed = re.sub(
            r'(?<!\\)\\n',
            r'\\\\n',
            cleaned
        )
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"   JSON error en intento 2: {e}")

    # Intento 3: reemplazar \n por espacio (más agresivo)
    try:
        # Dentro de strings, reemplazar saltos de línea literales por espacios
        fixed = re.sub(r'(?<!\\)\n', ' ', cleaned)
        # Y también arreglar \n escapados
        fixed = re.sub(r'(?<!\\)\\n', ' ', fixed)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"   JSON error en intento 3: {e}")

    # Intento 4: quitar comas finales antes de } o ]
    try:
        fixed = re.sub(r",\s*([}\]])", r"\1", cleaned)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"   JSON error en intento 4: {e}")

    # Intento 5: combinar los arreglos anteriores
    try:
        fixed = re.sub(r'(?<!\\)\\n', ' ', cleaned)
        fixed = re.sub(r'(?<!\\)\n', ' ', fixed)
        fixed = re.sub(r",\s*([}\]])", r"\1", fixed)
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        print(f"   JSON error en intento 5: {e}")

    # Guardar JSON crudo para debug
    try:
        with open("debug_last_script.txt", "w", encoding="utf-8") as f:
            f.write(raw)
        print("   JSON crudo guardado en debug_last_script.txt")
    except Exception:
        pass

    raise ValueError(
        f"No se pudo parsear el JSON.\n"
        f"Primeros 500 caracteres:\n{cleaned[:500]}"
    )

def write_script(research: dict, video_type: str = "normal") -> dict:
    """
    Genera un guion narrado para YouTube.
    video_type: "normal" (4-6 min, 9 secciones) | "shorts" (50-60 seg, 3 secciones)
    """
    if video_type == "shorts":
        return _write_shorts_script(research)

    key_points_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(research["key_points"]))

    prompt = f"""Eres el guionista principal de un canal de YouTube en ESPANOL LATINOAMERICANO sobre tutoriales practicos de inteligencia artificial para profesionales de oficina (analistas, administrativos, managers, emprendedores).

REGLA CRITICA DE IDIOMA: TODA la narracion, titulos de seccion y descripcion DEBEN estar en ESPANOL de Latinoamerica. Los unicos campos que van en ingles son image_query, image_query_2, image_query_3.

REGLA CRITICA DE DURACION: El video completo DEBE durar entre 2.5 y 3.5 minutos. Esto significa 400-500 palabras TOTALES. Cada narracion individual DEBE tener entre 40 y 60 palabras (3-4 frases completas).

REGLA CRITICA DE JSON:
- NUNCA uses comillas dobles dentro de los strings del JSON.
- NUNCA uses saltos de linea (\n o \n\n) dentro de ningun string del JSON. Ni en description, ni en narration, ni en ningun campo. Todo el texto de un campo va en UNA SOLA LINEA.
- El JSON debe ser 100% valido.

Video topic: {research["topic"]}
Title: {research["video_title"]}
Core hook question: {research.get("hook_question", "")}
Key points to cover:
{key_points_str}

Escribe un guion PRACTICO y DINAMICO de 4-6 minutos.

REGLAS DE RITMO:
- Seccion 4 DEBE abrir con un re-hook: "Pero espera, aqui esta el truco que nadie te dice..."
- Seccion 6 DEBE abrir con un segundo re-hook: "Ahora te muestro como aplicar esto en TU trabajo HOY..."
- Plantea una pregunta en la seccion 2 y respondela en la seccion 5.

REGLAS VISUALES (image_query en ingles para Pexels):
- Cada seccion necesita 3 busquedas de imagen DISTINTAS y CONCRETAS.
- Ejemplos: "excel spreadsheet", "office desk laptop", "AI chat interface", "business meeting", "data analytics dashboard".
- NUNCA uses terminos abstractos.

Responde SOLO con un objeto JSON valido. Sin markdown, sin texto extra:

{{
  "title": "{research['video_title']}",
  "description": "Descripcion del video en UNA SOLA LINEA, sin saltos de linea, 2-3 frases, con la palabra clave principal al inicio.",
  "tags": {json.dumps(research.get('tags', []))},
  "sections": [
    {{
      "id": 1,
      "section_type": "hook",
      "title": "Titulo corto y potente",
      "narration": "Escribe 4-6 frases completas (60-90 palabras) que enganchen al espectador. Primera frase: declaracion provocadora. Ultima: pregunta abierta que se responde en la seccion 5.",
      "image_query": "excel spreadsheet data analysis",
      "image_query_2": "person frustrated at computer office",
      "image_query_3": "AI chat interface screen closeup",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 45
    }},
    {{
      "id": 2,
      "section_type": "intro",
      "title": "Titulo en pantalla",
      "narration": "Escribe 4-6 frases completas (60-90 palabras). Contexto del problema. Pregunta open-loop explicita. Promesa de lo que viene.",
      "image_query": "business professional using laptop",
      "image_query_2": "excel spreadsheet numbers screen",
      "image_query_3": "data analytics dashboard charts",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 45
    }},
    {{
      "id": 3,
      "section_type": "content",
      "title": "Titulo en pantalla",
      "narration": "Escribe 5-7 frases completas (70-95 palabras). Primera frase: analogia concreta. Siguientes: como funciona paso a paso. Ejemplo real.",
      "image_query": "hands typing on laptop keyboard closeup",
      "image_query_2": "excel formulas spreadsheet closeup",
      "image_query_3": "person working office desk screen",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 50
    }},
    {{
      "id": 4,
      "section_type": "re_hook",
      "title": "Pero Aqui Viene Lo Bueno",
      "narration": "Escribe 5-7 frases completas (70-95 palabras). Primera frase DEBE empezar con 'Pero espera, aqui esta el truco que nadie te dice...' Siguientes: el giro contraintuitivo.",
      "image_query": "light bulb moment idea closeup",
      "image_query_2": "surprised person laptop screen",
      "image_query_3": "AI assistant interface glowing screen",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 50
    }},
    {{
      "id": 5,
      "section_type": "content",
      "title": "Titulo en pantalla",
      "narration": "Escribe 5-7 frases completas (70-95 palabras). Primera frase: respuesta a la pregunta open-loop de la seccion 2. Siguientes: como aplicarlo paso a paso.",
      "image_query": "AI prompt typed on screen closeup",
      "image_query_2": "excel data transformation before after",
      "image_query_3": "professional presenting data screen",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 50
    }},
    {{
      "id": 6,
      "section_type": "re_hook",
      "title": "Y Ahora Lo Importante",
      "narration": "Escribe 5-7 frases completas (70-95 palabras). Primera frase DEBE empezar con 'Ahora te muestro como aplicar esto en TU trabajo HOY...' Siguientes: impacto practico en el dia a dia.",
      "image_query": "office worker productive computer",
      "image_query_2": "hand clicking mouse computer",
      "image_query_3": "professional saving time dashboard",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 50
    }},
    {{
      "id": 7,
      "section_type": "content",
      "title": "Titulo en pantalla",
      "narration": "Escribe 4-6 frases completas (60-90 palabras). Angulo aspiracional para la carrera del espectador. Pregunta retorica que lleve a la conclusion.",
      "image_query": "professional career growth laptop",
      "image_query_2": "modern office team working",
      "image_query_3": "futuristic AI workplace concept",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 45
    }},
    {{
      "id": 8,
      "section_type": "conclusion",
      "title": "Titulo en pantalla",
      "narration": "Escribe 4-6 frases completas (60-90 palabras). Conclusion clave con callback al hook inicial. Pregunta directa para comentarios.",
      "image_query": "success achievement laptop celebration",
      "image_query_2": "person satisfied working computer",
      "image_query_3": "forward looking future office technology",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 45
    }},
    {{
      "id": 9,
      "section_type": "cta",
      "title": "Unete al Canal",
      "narration": "Escribe 3-4 frases completas (40-60 palabras). Invitacion a suscribirse. Pregunta especifica para comentarios.",
      "image_query": "youtube subscribe button animation",
      "image_query_2": "audience community engagement screen",
      "image_query_3": "laptop with youtube channel dashboard",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 30
    }}
  ]
}}

IMPORTANTE FINAL:
- Cada narracion DEBE tener 60-90 palabras (4-6 frases completas).
- El video total DEBE sumar 600-800 palabras.
- La pregunta open-loop de la seccion 2 DEBE responderse en la seccion 5.
- TODO el contenido en ESPANOL LATINOAMERICANO excepto los image_query.
- NUNCA uses comillas dobles dentro de strings del JSON."""

    last_error = None
    for attempt in range(3):
        try:
            print("   Writing script with Groq...")
            raw = generate(prompt)
            script = _try_parse_json(raw)

            if "sections" not in script or len(script["sections"]) < 4:
                raise ValueError("Script returned too few sections.")

            total_words = sum(len(s.get("narration", "").split()) for s in script["sections"])
            print(f"   Total palabras: {total_words}")
            print(f"   Duracion estimada: {total_words / 150:.2f} minutos")

            return script

        except Exception as e:
            last_error = e
            if attempt < 2:
                print(f"   Error en intento {attempt + 1}/3: {e}")
                print(f"   Reintentando en 3 segundos...")
                time.sleep(3)
            else:
                print(f"   Fallo despues de 3 intentos.")

    raise ValueError(f"Scriptwriter fallo tras 3 intentos.\nUltimo error:\n{last_error}")


def _write_shorts_script(research: dict) -> dict:
    """Genera un guion compacto de 50-60 segundos para YouTube Shorts."""
    key_points_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(research["key_points"][:3]))

    prompt = f"""Eres un guionista viral de YouTube Shorts en ESPANOL LATINOAMERICANO.

REGLA CRITICA DE JSON: NUNCA uses comillas dobles dentro de strings.

Video topic: {research["topic"]}
Title: {research["video_title"]}
Key points:
{key_points_str}

Escribe un guion GRIPANTE de 50-60 segundos. Reglas:
- Hook en las PRIMERAS 3 palabras
- 3 secciones: hook (10-12s), revelacion (30-35s), cta (8-10s)
- Narracion total: 120-160 palabras

Responde SOLO con JSON valido:

{{
  "title": "{research['video_title']} #Shorts",
  "description": "Descripcion corta de 2 frases, en espanol.",
  "tags": {json.dumps(research.get('tags', []) + ["Shorts", "YouTubeShorts"])},
  "sections": [
    {{
      "id": 1,
      "section_type": "hook",
      "title": "hook_internal",
      "narration": "UNA frase impactante de maximo 15 palabras.",
      "image_query": "excel spreadsheet closeup data",
      "image_query_2": "AI chat interface glowing screen",
      "image_query_3": "person typing laptop office",
      "image_query_4": "business dashboard analytics screen",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 12
    }},
    {{
      "id": 2,
      "section_type": "content",
      "title": "content_internal",
      "narration": "DOS frases cortas, maximo 30 palabras.",
      "image_query": "excel formulas screen closeup",
      "image_query_2": "AI assistant typing prompt",
      "image_query_3": "data transformation charts",
      "image_query_4": "professional working laptop screen",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 35
    }},
    {{
      "id": 3,
      "section_type": "cta",
      "title": "cta_internal",
      "narration": "UNA frase corta de maximo 15 palabras.",
      "image_query": "youtube subscribe button",
      "image_query_2": "office desk laptop productivity",
      "image_query_3": "AI workplace technology concept",
      "image_query_4": "person smiling at computer",
      "bullet_points": [],
      "caption_text": "",
      "duration_seconds": 10
    }}
  ]
}}"""

    last_error = None
    for attempt in range(3):
        try:
            print("   Writing Shorts script with Groq...")
            raw = generate(prompt)
            script = _try_parse_json(raw)

            if "sections" not in script or len(script["sections"]) < 2:
                raise ValueError("Shorts script returned too few sections.")

            script["video_type"] = "shorts"
            return script

        except Exception as e:
            last_error = e
            if attempt < 2:
                print(f"   Error en intento {attempt + 1}/3: {e}")
                time.sleep(3)
            else:
                print(f"   Fallo despues de 3 intentos.")

    raise ValueError(f"Shorts scriptwriter fallo tras 3 intentos.\nUltimo error:\n{last_error}")