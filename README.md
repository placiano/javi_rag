# Chatbot RAG con Gradio y GPT-4o-mini

Este proyecto crea un chatbot que responde preguntas basadas en documentos (CSV, JSON, XLSX, DOCX, PDF y TXT) usando un sistema RAG (Retrieval-Augmented Generation) con GPT-4o-mini como modelo de lenguaje y Gradio como interfaz.

## Requisitos previos

1. **Python 3.11**: Necesitas tener Python 3.11 instalado en tu computadora. Puedes descargarlo desde [python.org](https://www.python.org/downloads/). Verifica tu versión con:

   ```bash
   python --version
   ```

Si no tienes Python 3.11, descárgalo e instálalo.

2. **Un editor de código**: Usa Visual Studio Code, PyCharm o cualquier editor que prefieras.

3. **Clave de API de OpenAI**: Regístrate en [OpenAI](https://platform.openai.com/) y obtén una clave de API.

## Estructura del proyecto

- `app.py`: El código principal del chatbot.
- `setup.py`: Script para configurar el entorno.
- `requirements.txt`: Lista de dependencias.
- `.env`: Archivo para almacenar secretos (se crea automáticamente).
- `documentos/`: Carpeta donde se guardan los archivos subidos (se crea al ejecutar).

## Paso a paso para empezar

### 1. Descargar el código fuente
El código de este proyecto está disponible en GitHub. Sigue estos pasos para descargarlo:

- Ve al enlace de descarga: [https://github.com/placiano/javi_rag/archive/refs/heads/main.zip](https://github.com/placiano/javi_rag/archive/refs/heads/main.zip)
- Haz clic en el enlace y se descargará un archivo ZIP (por ejemplo, `main.zip`).
- Descomprime el archivo en una carpeta de tu computadora, como `javi_rag`. Esto creará una carpeta con todos los archivos del proyecto (como `app.py`, `setup.py`, etc.).

Alternativa con Git (si lo tienes instalado):
```bash
git clone https://github.com/placiano/javi_rag.git
cd javi_rag
```

### 2. Abrir la terminal
Abre una terminal en la carpeta del proyecto que acabas de descomprimir:
- **Windows**: Haz clic derecho en la carpeta, selecciona "Abrir en terminal" o usa CMD/PowerShell y navega con `cd ruta/a/javi_rag`.
- **Mac/Linux**: Abre la terminal y usa `cd /ruta/a/javi_rag`.

### 3. Configurar el entorno con `setup.py`
Ejecuta el script `setup.py` para preparar todo:
```bash
python setup.py
```
- Si no hay un entorno virtual, se creará uno con Python 3.11 en una carpeta llamada `.venv`.
- Te pedirá tu clave de API de OpenAI. Pégala desde tu cuenta de OpenAI y presiona Enter.
- Si te dice que actives el entorno manualmente, sigue las instrucciones que aparecerán:
  - **Windows**: `.\.venv\Scripts\activate`
  - **Mac/Linux**: `source .venv/bin/activate`
- Una vez activado (verás `(.venv)` en la terminal), ejecuta de nuevo:
  ```bash
  python setup.py
  ```
- Esto instalará todas las dependencias listadas en `requirements.txt`.

### 4. Verificar el entorno
Cuando veas `(.venv)` al inicio de la línea en la terminal, significa que el entorno está activo y listo.

### 5. Ejecutar el chatbot con `app.py`
Corre la aplicación con este comando:
```bash
python app.py
```
- Se abrirá tu navegador automáticamente con la interfaz del chatbot.
- Si no se abre, copia la URL que aparece en la terminal (como `http://localhost:8501`) y pégala en tu navegador.

### 6. Usar el chatbot
- **Subir documentos**: Haz clic en "Sube tus documentos" y selecciona archivos CSV, JSON, XLSX, DOCX, PDF y TXT desde tu computadora.
- **Chatear**: Escribe una pregunta en el campo de texto (ej. "¿Qué dice el archivo sobre ventas?") y presiona Enter.
- **Reiniciar**: Usa el botón "Reiniciar chat y documentos" para empezar de nuevo.

## Solución de problemas

- **"Python no encontrado"**: Asegúrate de que Python 3.11 esté instalado y en tu PATH. Prueba `python3 --version` si `python --version` no funciona.
- **Errores de dependencias**: Verifica que el entorno esté activo (`(.venv)`) y vuelve a ejecutar `python setup.py`.
- **"API key inválida"**: Abre el archivo `.env` con un editor de texto, revisa que la clave sea correcta y no tenga espacios.

## Personalización

- Cambia el modelo en `app.py` (línea con `client.chat.completions.create`) si quieres usar otro modelo de OpenAI.
- Añade más formatos de archivo editando la función `read_file` en `app.py`.

¡Disfruta de tu chatbot!
```