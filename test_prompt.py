import config
from agents.researcher import research_topic
from agents.gemini_client import generate

# Generar research
print("⏳ Research...")
research = research_topic(
    channel_description=config.CHANNEL_DESCRIPTION,
    topic_override="Cómo usar Claude para analizar Excel sin programar"
)

# Construir el mismo prompt que usa el scriptwriter
key_points_str = "\n".join(f"  {i+1}. {p}" for i, p in enumerate(research["key_points"]))

# Importamos el prompt directamente desde scriptwriter
# Para eso, vamos a capturar el prompt ANTES de enviarlo
import agents.scriptwriter as sw
import inspect

# Monkey patch temporal para capturar el prompt
original_generate = sw.generate
captured_prompt = []

def capture_generate(prompt, starting_model=None):
    captured_prompt.append(prompt)
    print(f"\n=== PROMPT CAPTURADO ===")
    print(f"Longitud del prompt: {len(prompt)} caracteres")
    print(f"Tokens estimados: {len(prompt) // 4}")
    print(f"=== FIN DEL PROMPT ===\n")
    # Ahora llamamos al generate REAL para ver qué devuelve
    return original_generate(prompt, starting_model)

sw.generate = capture_generate

try:
    script = sw.write_script(research)
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    sw.generate = original_generate