# Guia Completa del Pipeline de YouTube Automatizado

**Proyecto:** IA Practica - Canal de tutoriales de IA aplicada
**Fecha:** Septiembre 2026
**Estado:** Produccion

---

## Tabla de Contenidos

1. Resumen Ejecutivo
2. Herramientas Utilizadas
3. Arquitectura del Pipeline
4. Instalacion Completa
5. Configuracion de APIs
6. Configuracion del Canal
7. Migracion de Gemini a Groq
8. Flujo de Generacion de Video
9. Despues de Crear el Video
10. Chuleta de Comandos
11. Troubleshooting
12. Lecciones Aprendidas
13. Proximos Pasos

---

## 1. Resumen Ejecutivo

Pipeline 100% gratuito para generar videos de YouTube faceless (sin mostrar rostro) sobre tutoriales de IA aplicada. El sistema crea guion con IA, voz en off sintetizada, imagenes de stock y ensamblaje automatico.

**Objetivo del canal:** Ensenar a profesionales hispanohablantes a usar herramientas de IA (ChatGPT, Claude, NotebookLM, Copilot) para automatizar tareas de oficina.

**Costo por video:** $0

**Tiempo por video:** 5-10 min de generacion + 30 min de revision

---

## 2. Herramientas Utilizadas

### 2.1 Orquestador: youtube-agentic-ai-studio

| Atributo | Detalle |
|----------|---------|
| Funcion | Orquesta todo el proceso |
| Tipo | Open-source (MIT) |
| Repositorio | https://github.com/raunakpatil/youtube-agentic-ai-studio |
| Permanente | Si |
| Costo | $0 |

### 2.2 Motor de IA: Groq

| Atributo | Detalle |
|----------|---------|
| Funcion | Genera research y guiones |
| Tipo | API de inferencia LLM |
| Sitio | https://console.groq.com |
| Permanente | Si |
| Costo | $0 (tier gratuito) |

**Modelos:** openai/gpt-oss-120b, openai/gpt-oss-20b, llama-3.3-70b-versatile

**Obtener API Key:** console.groq.com/keys -> Create API Key

### 2.3 Voz: edge-tts

| Atributo | Detalle |
|----------|---------|
| Funcion | Texto a voz |
| Tipo | Libreria Python |
| Permanente | Si |
| Costo | $0 |

**Voz:** es-MX-JorgeNeural
**Rate:** +15%
**Pitch:** +0Hz

### 2.4 Imagenes: Pexels API

| Atributo | Detalle |
|----------|---------|
| Funcion | Descarga imagenes de stock |
| Sitio | https://pexels.com/api |
| Permanente | Si |
| Costo | $0 (200 req/hora) |

### 2.5 Video: MoviePy + FFmpeg

| Herramienta | Funcion | Costo |
|-------------|---------|-------|
| MoviePy | Edicion de video | $0 |
| FFmpeg | Renderizado | $0 |

### 2.6 Dashboard: Flask (gui.py)

| Atributo | Detalle |
|----------|---------|
| URL | http://localhost:7070 |
| Permanente | Si |
| Costo | $0 |

---

## 3. Arquitectura del Pipeline
DASHBOARD WEB (Flask) -> http://localhost:7070
|
v
PIPELINE ORQUESTADOR
|
+----+----+----+
| | |
v v v
RESEARCH SCRIPT IMAGES
(Groq) (Groq) (Pexels)
| | |
+----+----+------+
|
v
NARRATION (edge-tts)
|
v
VIDEO ASSEMBLY (MoviePy + FFmpeg)
|
v
OUTPUT/video.mp4

text

---

## 4. Instalacion Completa (UNA VEZ)

### 4.1 Verificar prerrequisitos

```powershell
git --version
py -3.12 --version
Si no tienes Python 3.12:

powershell
winget install Python.Python.3.12 --accept-source-agreements --accept-package-agreements
4.2 Clonar repositorio
powershell
cd D:\Personal
git clone https://github.com/raunakpatil/youtube-agentic-ai-studio.git
cd youtube-agentic-ai-studio
4.3 Crear entorno virtual
powershell
py -3.12 -m venv venv
4.4 Activar venv
powershell
.\venv\Scripts\Activate.ps1
Si da error:

powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
4.5 Instalar dependencias
powershell
pip install -r requirements.txt
pip install python-dotenv
pip install groq
4.6 Verificar
powershell
python -c "import numpy; import moviepy; import edge_tts; import groq; import dotenv; print('Todo OK')"
5. Configuracion de APIs
5.1 Crear .env
powershell
copy .env.example .env
notepad .env
5.2 Contenido
text
GEMINI_API_KEY=
PEXELS_API_KEY=tu_key_pexels
ELEVENLABS_API_KEY=
GROQ_API_KEY=gsk_tu_key_groq
5.3 Verificar
powershell
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print('PEXELS:', 'OK' if os.getenv('PEXELS_API_KEY') else 'FALTA'); print('GROQ:', 'OK' if os.getenv('GROQ_API_KEY') else 'FALTA')"
6. Configuracion del Canal
6.1 Editar config.py
powershell
notepad config.py
6.2 Cambios
Descripcion:

python
CHANNEL_DESCRIPTION = """
Canal de tutoriales practicos de inteligencia artificial para profesionales de oficina que NO saben programar.
Ensenamos a usar herramientas de IA (ChatGPT, Claude, NotebookLM, Copilot, Julius AI) para automatizar
tareas reales: analisis de Excel, redaccion de informes, investigacion de datos, reportes ejecutivos.
Target audience: analistas, administrativos, managers y emprendedores hispanohablantes.
Tono: claro, directo, practico.
"""
Nombre:

python
CHANNEL_NAME = "IA Practica"
Voz:

python
VOICE_ID    = "es-MX-JorgeNeural"
VOICE_RATE  = "+15%"
VOICE_PITCH = "+0Hz"
Modelo:

python
GEMINI_MODEL = "openai/gpt-oss-120b"
6.3 Verificar
powershell
python -c "import config; print('Canal:', config.CHANNEL_NAME); print('Voz:', config.VOICE_ID); print('Modelo:', config.GEMINI_MODEL)"
Resultado esperado:

text
Canal: IA Practica
Voz: es-MX-JorgeNeural
Modelo: openai/gpt-oss-120b
7. Migracion de Gemini a Groq (UNA VEZ)
7.1 Backup
powershell
Copy-Item agents\gemini_client.py agents\gemini_client.py.bak
7.2 Reemplazar agents\gemini_client.py con el codigo Groq
powershell
notepad agents\gemini_client.py
El codigo nuevo usa from groq import Groq en lugar de from google import genai. Mantiene la misma interfaz generate(prompt, starting_model=None).

7.3 Verificar
powershell
python -c "from agents.gemini_client import generate; print('Import OK')"
python -c "from agents.gemini_client import generate; print(generate('Responde solo: OK'))"
Resultado esperado:

text
Import OK
   -> Using openai/gpt-oss-120b...
OK
8. Flujo de Generacion de Video (CADA VEZ)
8.1 Preparar entorno
powershell
cd D:\Personal\youtube-agentic-ai-studio
.\venv\Scripts\Activate.ps1
Verificar: ver (venv) al inicio.

8.2 Lanzar dashboard
powershell
python gui.py
Resultado:

text
YouTube AI Agent Studio
   Opening at http://localhost:7070
 * Running on http://127.0.0.1:7070
8.3 Abrir navegador
http://localhost:7070

8.4 Generar video
Introduce tema

Configura opciones

Clic en Generate

8.5 Monitorear progreso
text
Stage: research -> running
Stage: script -> running
Stage: images -> running
Stage: narration -> running
Stage: video -> running
[STAGE] video:done
8.6 Tiempos estimados
EtapaTiempo
Research10-30 seg
Script30-60 seg
Images1-2 min
Narration30-60 seg
Video assembly3-8 min
Total5-10 min
8.7 Ubicacion del video
D:\Personal\youtube-agentic-ai-studio\output\

9. Despues de Crear el Video
9.1 Revisar
powershell
start output\nombre_del_video.mp4
Checklist:

□ Voz sincroniza con imagenes
□ Subtitulos correctos
□ Ritmo adecuado
□ Imagenes relevantes
□ Musica no tapa voz
□ Audio claro
9.2 Optimizar SEO
Titulo: Palabra clave + beneficio. Max 60 caracteres.
Descripcion: Primeros 150 chars con lo importante. Timestamps.
Tags: 5-10 relevantes.
Miniatura: 1280x720, texto grande, colores contrastantes.

9.3 Subir a YouTube
Manual (recomendado):

YouTube Studio

Crear -> Subir video

Rellenar titulo, descripcion, tags

Subir miniatura

Programar publicacion

Automatica (avanzado):

Google Cloud Console

Habilitar YouTube Data API v3

Crear credenciales OAuth 2.0

Descargar client_secret.json

9.4 Analizar rendimiento (despues de 48h)
MetricaObjetivo
CTR>4%
Retencion>50%
Fuentes de traficoVariadas
SuscriptoresCreciendo
10. Chuleta de Comandos
Instalacion (una vez)
powershell
git clone https://github.com/raunakpatil/youtube-agentic-ai-studio.git
cd youtube-agentic-ai-studio
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install python-dotenv groq
Configuracion (una vez)
powershell
copy .env.example .env
notepad .env
notepad config.py
Migracion a Groq (una vez)
powershell
Copy-Item agents\gemini_client.py agents\gemini_client.py.bak
notepad agents\gemini_client.py
python -c "from agents.gemini_client import generate; print(generate('OK'))"
Uso diario
powershell
cd D:\Personal\youtube-agentic-ai-studio
.\venv\Scripts\Activate.ps1
python gui.py
Despues de generar
powershell
start output\video_final.mp4
Diagnostico
powershell
python --version
python -c "import numpy, moviepy, edge_tts, groq; print('OK')"
python -c "import config; print(config.CHANNEL_NAME, config.VOICE_ID, config.GEMINI_MODEL)"
python -c "from agents.gemini_client import generate; print(generate('OK'))"
Get-Content .env | Select-String "API_KEY"
11. Troubleshooting
ModuleNotFoundError: No module named 'groq'
powershell
pip install groq
ModuleNotFoundError: No module named 'dotenv'
powershell
pip install python-dotenv
API_KEY_INVALID o 401 UNAUTHENTICATED
Rota la clave

Actualiza el .env

Reinicia el pipeline

numpy no compila
Causa: Python 3.13 incompatible con numpy 1.26.4

powershell
py -3.12 -m venv venv
Flask no arranca
powershell
netstat -ano | findstr :7070
taskkill /PID [numero] /F
Video sin musica
Anadir archivos MP3 a music library/

Voz robotica
Considerar ElevenLabs ($5/mes)

12. Lecciones Aprendidas
Problemas resueltos
ProblemaCausaSolucion
numpy no compilaPython 3.13Instalar Python 3.12
API_KEY_INVALIDClaves AQ. cambiaronMigrar a Groq
ACCESS_TOKEN_TYPE_UNSUPPORTEDGemini rechaza authMigrar a Groq
ModuleNotFoundError: dotenvNo en venvpip install python-dotenv
Buenas practicas
Siempre usar venv

Backup antes de modificar

Verificar cada paso

No exponer API keys

Rotar claves expuestas

Documentar cambios

Reglas de oro
Nunca pegues API keys en chats

Siempre haz backup antes de editar

Verifica que el venv este activado

Rota claves si las expones

Documenta cada cambio

13. Proximos Pasos
Corto plazo (semana 1-2)
Generar 3-5 videos

Revisar calidad

Subir a YouTube con SEO

Analizar metricas

Medio plazo (mes 1-3)
Publicar 1 video/semana

Si retencion <40%: migrar a ElevenLabs

Si CTR <3%: mejorar miniaturas

Explorar Shorts

Largo plazo (mes 3-12)
Alcanzar 1K subs (YPP)

Monetizar con AdSense + afiliados

Diversificar: productos, patrocinios

Escalar a 2-3 videos/semana

Monetizacion por fase
FaseSubsMetodo
Inicio0-500Afiliados
Crecimiento500-1KAfiliados + servicios
YPP1K+AdSense + afiliados
Establecido10K+Patrocinios + productos
Escalado50K+Cursos + membresias
Apendices
A. Enlaces utiles
Pipeline: https://github.com/raunakpatil/youtube-agentic-ai-studio

Groq: https://console.groq.com

Pexels: https://pexels.com/api

edge-tts: https://github.com/rany2/edge-tts

YouTube Studio: https://studio.youtube.com

B. Voces edge-tts
VozAcentoGenero
es-MX-JorgeNeuralMexicoM
es-MX-DaliaNeuralMexicoF
es-AR-TomasNeuralArgentinaM
es-CO-GonzaloNeuralColombiaM
es-ES-AlvaroNeuralEspanaM
es-US-AlonsoNeuralEE.UU.M
C. Parametros de configuracion
ParametroValor
VIDEO_WIDTH1920
VIDEO_HEIGHT1080
VIDEO_FPS24
CROSSFADE_DURATION0.7
BROLL_INTERVAL10.0
RENDER_PRESETultrafast
MUSIC_VOLUME0.12
D. Glosario
Faceless: Contenido sin mostrar rostro

CTR: Click-Through Rate

YPP: YouTube Partner Program

CPM: Cost per Mille

Ken Burns: Efecto zoom/pan

Crossfade: Transicion suave

Open Loop: Pregunta sin responder

Pattern Interrupt: Cambio para recuperar atencion

Checklist Final
Instalacion
□ Git instalado
□ Python 3.12 instalado
□ Repositorio clonado
□ Venv creado
□ Dependencias instaladas
□ Groq y dotenv instalados
Configuracion
□ .env con PEXELS_API_KEY y GROQ_API_KEY
□ config.py editado
□ gemini_client.py migrado a Groq
Verificacion
□ Import de Groq funciona
□ Test de generacion responde OK
□ Dashboard arranca en 7070
Primer video
□ Tema introducido
□ Pipeline ejecutado
□ Video generado en output/
□ Video revisado
□ Subido a YouTube
Documento generado el 11 de septiembre de 2026
Version: 1.0
Estado: Produccion
