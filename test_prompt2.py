import os
from dotenv import load_dotenv
from groq import Groq
import config
from agents.researcher import research_topic

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Generar research
print("⏳ Research...")
research = research_topic(
    channel_description=config.CHANNEL_DESCRIPTION,
    topic_override="Cómo usar Claude para analizar Excel sin programar"
)

# Construir el prompt igual que scriptwriter (versión simplificada)
key_points_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(research["key_points"]))

prompt = f"""Eres un guionista de YouTube en español. Escribe un guión corto para un video sobre: {research["topic"]}.

Devuelve SOLO un JSON válido con esta estructura:
{{
  "title": "Título del video",
  "sections": [
    {{"id": 1, "narration": "Texto de narración"}},
    {{"id": 2, "narration": "Texto de narración"}}
  ]
}}

Sin markdown. Sin texto extra. Solo el JSON."""

print(f"\n📏 Longitud del prompt de prueba: {len(prompt)} caracteres")

# Llamar a Groq directamente
print("\n⏳ Llamando a Groq...")
try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": "Eres un experto guionista de YouTube. Respondes solo con JSON válido."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        max_tokens=4096,
    )
    content = response.choices[0].message.content
    print(f"\n✅ Respuesta recibida:")
    print(f"   Longitud: {len(content) if content else 0} caracteres")
    print(f"   Finish reason: {response.choices[0].finish_reason}")
    print(f"   Contenido (primeros 500):")
    print(repr(content[:500]) if content else "VACÍO")

    # Ver usage
    if response.usage:
        print(f"\n📊 Usage:")
        print(f"   Prompt tokens: {response.usage.prompt_tokens}")
        print(f"   Completion tokens: {response.usage.completion_tokens}")
        print(f"   Total tokens: {response.usage.total_tokens}")

except Exception as e:
    print(f"\n❌ Error: {e}")