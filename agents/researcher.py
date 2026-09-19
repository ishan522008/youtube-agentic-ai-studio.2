"""
Research Agent — uses shared LLM client with model fallback chain.
Banned topics are read from banned_topics.txt (one topic per line) in the
project root. Used topics are tracked in used_topics.txt.
"""
import json
import os
import re
import random
import time
from agents.gemini_client import generate

# Path to the banned-topics file
_BANNED_TOPICS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "banned_topics.txt",
)

# Path to the used-topics file (tracks which focus angles have been consumed)
_USED_TOPICS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "used_topics.txt",
)

_BUILTIN_BANNED = [
    "The Boltzmann Brain",
    "Simulation Theory",
    "Quantum Immortality",
]

# All available focus angles — used by researcher AND exposed to the GUI
FOCUS_ANGLES = [
    # Originales
    "IA para automatizar Excel y reportes de oficina",
    "Herramientas de IA para análisis de datos sin programar",
    "Prompts y trucos de ChatGPT para profesionales",
    "Claude y NotebookLM aplicados al trabajo diario",
    "Automatización de tareas administrativas con IA",
    "Copilot y asistentes IA para productividad",
    "IA para redactar correos, informes y presentaciones",
    "Casos reales de IA en empresas hispanohablantes",
    # Expandidos
    "Comparativas de herramientas de IA para oficina",
    "IA para gestión de proyectos y equipos",
    "IA para análisis financiero y contable",
    "IA para marketing digital y ventas",
    "IA para recursos humanos y reclutamiento",
    "IA para atención al cliente automatizada",
    "IA para investigación de mercado",
    "IA para creación de presentaciones impactantes",
    "IA para toma de decisiones basadas en datos",
    "IA para optimización de procesos internos",
    "IA para gestión de inventarios y logística",
    "IA para redacción de propuestas comerciales",
    "IA para análisis de contratos legales",
    "IA para traducción y localización",
    "IA para auditoría y cumplimiento normativo",
    "IA para formación y capacitación corporativa",
    "IA para análisis de feedback de clientes",
    "IA para predicción de tendencias de mercado",
    "IA para automatización de reuniones y actas",
    "IA para generación de reportes ejecutivos",
]


def load_banned_topics() -> list:
    """
    Return the combined list of banned topics.
    Built-in list is always included; file entries are appended.
    """
    topics = list(_BUILTIN_BANNED)
    try:
        if os.path.exists(_BANNED_TOPICS_FILE):
            with open(_BANNED_TOPICS_FILE, encoding="utf-8") as f:
                for line in f:
                    t = line.strip()
                    if t and not t.startswith("#") and t not in topics:
                        topics.append(t)
    except Exception as e:
        print(f"   ⚠ Could not read banned_topics.txt: {e}")
    return topics


def save_banned_topics(topics: list) -> None:
    """
    Write the user-managed portion of the banned list to banned_topics.txt.
    """
    user_topics = [t for t in topics if t not in _BUILTIN_BANNED and t.strip()]
    with open(_BANNED_TOPICS_FILE, "w", encoding="utf-8") as f:
        f.write("# One banned topic per line. Lines starting with # are comments.\n")
        f.write("# Add topics here after you make a video about them.\n\n")
        for t in user_topics:
            f.write(t + "\n")


def _load_used_angles() -> list:
    """Lee la lista de ángulos ya usados desde used_topics.txt."""
    if not os.path.exists(_USED_TOPICS_FILE):
        return []
    try:
        with open(_USED_TOPICS_FILE, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    except Exception as e:
        print(f"   ⚠ Could not read used_topics.txt: {e}")
        return []


def _mark_angle_as_used(angle: str) -> None:
    """Añade un ángulo al archivo de usados."""
    try:
        with open(_USED_TOPICS_FILE, "a", encoding="utf-8") as f:
            f.write(angle + "\n")
    except Exception as e:
        print(f"   ⚠ Could not write used_topics.txt: {e}")


def research_topic(channel_description: str,
                   topic_override: str = "",
                   focus_angle: str = "") -> dict:
    """
    Research a video topic for the channel.

    Parameters
    ----------
    channel_description : the channel's style / audience description from config.py
    topic_override      : if non-empty, write a video about THIS EXACT topic.
    focus_angle         : if non-empty (and topic_override is empty), use this
                          angle instead of picking one randomly.
    """
    banned     = load_banned_topics()
    banned_str = ", ".join(f'"{t}"' for t in banned)

    # ── MODE 1: USER-SPECIFIED EXACT TOPIC ───────────────────────────────────
    if topic_override.strip():
        exact_topic = topic_override.strip()
        print(f"   → Exact topic override: \"{exact_topic}\"")

        prompt = f"""Eres un estratega de contenido de YouTube para un canal en ESPAÑOL LATINOAMERICANO sobre tutoriales prácticos de inteligencia artificial para profesionales de oficina.

Descripción del canal:
{channel_description}

INSTRUCCIÓN OBLIGATORIA: DEBES hacer un video sobre este tema EXACTO:
>>> {exact_topic} <<<

NO sustituyas el tema, NO elijas un ángulo relacionado — escribe específicamente sobre "{exact_topic}". El usuario ha solicitado explícitamente este tema.

TEMAS PROHIBIDOS: NO incluyas ninguno de estos en el output: {banned_str}

Tu misión: Investigar y planear un video de YouTube de 3-4 minutos sobre "{exact_topic}".

Responde SOLO con un objeto JSON válido. Sin markdown, sin explicación:

{{
  "topic": "{exact_topic}",
  "why_now": "Por qué este tema resuena con la audiencia ahora mismo",
  "video_title": "Título de YouTube impactante de menos de 70 caracteres sobre {exact_topic}",
  "description": "Descripción de YouTube de 2 frases optimizada para SEO y curiosidad, en español",
  "hook_question": "La pregunta más impactante que responde este video",
  "key_points": [
    "Primer concepto o revelación clave sobre {exact_topic}",
    "Segundo concepto — el giro o sorpresa",
    "Tercer concepto — implicación más profunda",
    "Cuarto concepto — consecuencia en el mundo real"
  ],
  "target_audience": "Quién exactamente verá y compartirá esto",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8"],
  "thumbnail_concept": "Describe la miniatura perfecta para este tema",
  "estimated_virality": "high"
}}"""

        raw = generate(prompt)
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$",          "", raw).strip()
        match = re.search(r"\{[\s\S]*\}", raw)
        if not match:
            raise ValueError(f"Researcher returned no JSON.\nRaw:\n{raw[:600]}")
        data = json.loads(match.group())
        for field in ["topic", "video_title", "key_points", "tags"]:
            if field not in data:
                raise ValueError(f"Research JSON missing field: '{field}'")
        return data

    # ── MODE 2: AI PICKS THE TOPIC ───────────────────────────────────────────
    if focus_angle.strip():
        chosen_angle = focus_angle.strip()
        print(f"   → Focus angle (GUI selected): {chosen_angle}")
    else:
        # ─── Sistema de temas usados ───
        used = _load_used_angles()
        available = [a for a in FOCUS_ANGLES if a not in used]

        if not available:
            raise RuntimeError(
                "\n\n🛑 TEMAS AGOTADOS\n"
                f"   Ya se usaron los {len(FOCUS_ANGLES)} ángulos disponibles.\n"
                f"   Para continuar:\n"
                f"   1. Abre agents/researcher.py\n"
                f"   2. Añade más ángulos a FOCUS_ANGLES\n"
                f"   3. Borra used_topics.txt\n"
                f"   4. Vuelve a ejecutar\n"
            )

        chosen_angle = random.choice(available)
        print(f"   → Focus angle (random): {chosen_angle}")
        print(f"   → Ángulos restantes: {len(available) - 1}")

        # Registrar el ángulo como usado
        _mark_angle_as_used(chosen_angle)
        # ───────────────────────────────

    print(f"   → Asking LLM for topic ideas within: {chosen_angle}")

    prompt = f"""Eres un estratega de contenido de YouTube para un canal en ESPAÑOL LATINOAMERICANO sobre tutoriales prácticos de inteligencia artificial para profesionales de oficina (analistas, administrativos, managers, emprendedores).

Descripción del canal:
{channel_description}

INSTRUCCIONES CRÍTICAS PARA ESTA EJECUCIÓN:
1. Enfócate enteramente en este tema específico: >>> {chosen_angle} <<<
2. TEMAS PROHIBIDOS: NO sugieras ninguno de los siguientes — ya hicimos videos sobre ellos: {banned_str}. Debes dar un concepto nuevo, altamente original.
3. Cache Bust ID: {time.time()} (Asegura output completamente único).

Tu misión:
1. Piensa en 3-4 ideas de temas de video altamente atractivos dentro de ese tema específico.
2. Selecciona el MEJOR tema que sea genuinamente impactante, oportuno, y explicable en 3-4 minutos.

Responde SOLO con un objeto JSON válido. Sin markdown, sin explicación:

{{
  "topic": "El tema específico del video",
  "why_now": "Por qué este tema está pegando ahora mismo",
  "video_title": "Título de YouTube impactante de menos de 70 caracteres",
  "description": "Descripción de YouTube de 2 frases optimizada para SEO y curiosidad, en español",
  "hook_question": "La pregunta más impactante que responde este video",
  "key_points": [
    "Primer concepto o revelación clave",
    "Segundo concepto — el giro o sorpresa",
    "Tercer concepto — implicación más profunda",
    "Cuarto concepto — consecuencia en el mundo real"
  ],
  "target_audience": "Quién exactamente verá y compartirá esto",
  "tags": ["tag1","tag2","tag3","tag4","tag5","tag6","tag7","tag8"],
  "thumbnail_concept": "Describe la miniatura perfecta",
  "estimated_virality": "high"
}}"""

    raw = generate(prompt)
    raw = re.sub(r"^```(?:json)?", "", raw).strip()
    raw = re.sub(r"```$",          "", raw).strip()

    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        raise ValueError(f"Researcher returned no JSON.\nRaw:\n{raw[:600]}")

    data = json.loads(match.group())
    for field in ["topic", "video_title", "key_points", "tags"]:
        if field not in data:
            raise ValueError(f"Research JSON missing field: '{field}'")
    return data