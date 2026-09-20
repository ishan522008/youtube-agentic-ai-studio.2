from agents.researcher import research_topic
from agents.scriptwriter import write_script
import config

# Investigar el tema (parámetro correcto: topic_override)
print("\n⏳ Generando research...")
research = research_topic(
    channel_description=config.CHANNEL_DESCRIPTION,
    topic_override="Cómo usar Claude para analizar Excel sin programar"
)

# Generar el guión
print("\n⏳ Generando guión...")
script = write_script(research)

# Analizar el resultado
print("\n" + "=" * 60)
print("RESULTADO DEL ANÁLISIS DEL GUIÓN")
print("=" * 60)

secciones = script.get("sections", [])
total_palabras = sum(len(sec.get("narration", "").split()) for sec in secciones)

print(f"\nSecciones generadas: {len(secciones)}")
print(f"Palabras totales: {total_palabras}")
print(f"Duración estimada: {total_palabras / 150:.2f} minutos")
print("\nPalabras por sección:")

for sec in secciones:
    palabras = len(sec.get("narration", "").split())
    print(f"  Sección {sec['id']} ({sec.get('section_type', '?')}): {palabras} palabras")

# Veredicto
print("\n" + "=" * 60)
if 450 <= total_palabras <= 600:
    print("✅ OBJETIVO CUMPLIDO: 3-4 minutos")
elif total_palabras < 450:
    print(f"⚠️ FALTAN {450 - total_palabras} palabras para llegar a 3 min")
else:
    print(f"⚠️ SOBRAN {total_palabras - 600} palabras, el video será largo")
print("=" * 60)

# Guardar el guión completo para inspección
import json
with open("debug_guion_prueba.json", "w", encoding="utf-8") as f:
    json.dump(script, f, ensure_ascii=False, indent=2)
print("\n📄 Guión completo guardado en: debug_guion_prueba.json")