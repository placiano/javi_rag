import gradio as gr
import pandas as pd
import json
import os
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import PyPDF2
from docx import Document
import tempfile
import shutil

# Cargar variables de entorno
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Modelo de embeddings - usando un modelo multilingüe más potente
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# Carpeta para documentos
UPLOAD_FOLDER = "documentos"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Función para leer diferentes tipos de archivos
def read_file(file_path):
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path).to_string()
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.dumps(json.load(f), ensure_ascii=False)
        elif file_path.endswith('.xlsx'):
            return pd.read_excel(file_path).to_string()
        elif file_path.endswith('.pdf'):
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text
        elif file_path.endswith('.docx'):
            doc = Document(file_path)
            text = ""
            for para in doc.paragraphs:
                text += para.text + "\n"
            return text
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            return None
    except Exception as e:
        print(f"Error al leer {file_path}: {e}")
        return None

# Fragmentar documentos largos para mejor procesamiento
def chunk_text(text, chunk_size=1000, overlap=200):
    chunks = []
    if not text:
        return chunks
    
    text_len = len(text)
    for i in range(0, text_len, chunk_size - overlap):
        end = min(i + chunk_size, text_len)
        chunks.append(text[i:end])
        if end == text_len:
            break
    return chunks

# Cargar y procesar documentos
def load_documents(folder_path):
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        content = read_file(file_path)
        if content:
            # Fragmentar documentos largos
            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                documents.append({
                    "filename": filename,
                    "chunk_id": i,
                    "content": chunk
                })
    return documents

# Generar embeddings de los documentos
def generate_embeddings(documents):
    if not documents:
        return None, []
    contents = [doc['content'] for doc in documents]
    
    # Calcular embeddings por lotes para manejar documentos grandes
    batch_size = 32
    all_embeddings = []
    
    for i in range(0, len(contents), batch_size):
        batch = contents[i:i+batch_size]
        batch_embeddings = embedder.encode(batch, convert_to_numpy=True)
        all_embeddings.append(batch_embeddings)
    
    if all_embeddings:
        embeddings = np.vstack(all_embeddings)
        return embeddings, documents
    return None, []

# Buscar documentos relevantes y devolver los top_k más similares
def retrieve_relevant_docs(query, embeddings, documents, top_k=3):
    if embeddings is None or not documents:
        return "No hay documentos cargados para buscar."
    
    query_embedding = embedder.encode(query, convert_to_numpy=True)
    similarities = cosine_similarity([query_embedding], embeddings)[0]
    
    # Obtener los top_k documentos más similares
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    context = ""
    for idx in top_indices:
        if similarities[idx] > 0.3:  # Umbral de similitud mínima
            doc = documents[idx]
            context += f"\n--- {doc['filename']} (Parte {doc['chunk_id']+1}) ---\n"
            context += doc['content'] + "\n"
    
    if not context:
        return "No se encontraron documentos relevantes para tu consulta."
    
    return context

# Generar respuesta con GPT-4o-mini
def generate_response(query, context):
    prompt = f"""
Utiliza únicamente la siguiente información para responder a la pregunta del usuario.
Si la información no es suficiente, indica claramente que no puedes responder basándote en los documentos proporcionados.
No inventes información que no esté presente en el contexto.

Contexto:
{context}

Pregunta: {query}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un asistente de documentación preciso que responde basándose únicamente en la información proporcionada."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al generar respuesta: {str(e)}"

# Variables globales para embeddings y documentos
embeddings = None
documents = []

# Función para cargar documentos
def upload_files(files):
    global embeddings, documents
    
    if not files:
        return "No se subieron archivos."
    
    # Limpiar la carpeta de documentos antes de cargar nuevos
    for existing_file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, existing_file)
        if os.path.isfile(file_path):
            os.remove(file_path)
    
    uploaded_files = []
    
    for file in files:
        # Manejar correctamente el objeto file de Gradio
        try:
            file_name = os.path.basename(file.name)
            dest_path = os.path.join(UPLOAD_FOLDER, file_name)
            
            # Copiar el archivo al directorio de destino
            shutil.copy2(file.name, dest_path)
            uploaded_files.append(file_name)
        except Exception as e:
            return f"Error al procesar el archivo {getattr(file, 'name', 'desconocido')}: {str(e)}"
    
    if uploaded_files:
        documents = load_documents(UPLOAD_FOLDER)
        embeddings, documents = generate_embeddings(documents)
        return f"Archivos cargados exitosamente: {', '.join(uploaded_files)}. Se procesaron {len(documents)} fragmentos de texto."
    else:
        return "No se pudo cargar ningún archivo."

# Función para manejar el chat
def chat(message, history):
    global embeddings, documents
    
    if not message.strip():
        return history, ""
        
    # Verificar si hay documentos cargados
    if embeddings is None or len(documents) == 0:
        response = "No hay documentos cargados. Por favor, sube algunos documentos primero."
    else:
        context = retrieve_relevant_docs(message, embeddings, documents)
        response = generate_response(message, context)
    
    history.append((message, response))
    return history, ""

# Función para reiniciar
def reset():
    global embeddings, documents
    embeddings = None
    documents = []
    
    for file in os.listdir(UPLOAD_FOLDER):
        file_path = os.path.join(UPLOAD_FOLDER, file)
        if os.path.isfile(file_path):
            os.remove(file_path)
            
    return [], "Chat y documentos reiniciados"

# Interfaz de Gradio con CSS personalizado
with gr.Blocks(title="Chatbot RAG con GPT-4o-mini", css="""
    .chatbot-container {height: 500px;}
    .small-button {width: 80px !important; height: 30px !important;}
""") as demo:
    gr.Markdown("# Chatbot RAG con GPT-4o-mini")
    gr.Markdown("Sube documentos a la derecha y haz preguntas sobre ellos a la izquierda")
    
    with gr.Row():
        # Columna izquierda: Chatbot
        with gr.Column(scale=2):
            chatbot = gr.Chatbot(label="Chat", height=500)
            msg = gr.Textbox(label="Escribe tu mensaje", placeholder="Haz una pregunta sobre los documentos...", submit_btn=False)
            
            with gr.Row():
                submit = gr.Button("Enviar", variant="primary")
                clear = gr.Button("Reiniciar", variant="stop", elem_classes="small-button")
            
            # Enviar con Enter y con el botón
            msg.submit(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
            submit.click(chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
            clear.click(reset, outputs=[chatbot, msg])
        
        # Columna derecha: Carga de archivos
        with gr.Column(scale=1):
            file_input = gr.File(label="Sube tus documentos", file_types=['.csv', '.json', '.xlsx', '.pdf', '.docx', '.txt'], file_count="multiple")
            upload_button = gr.Button("Cargar documentos", variant="primary")
            upload_status = gr.Textbox(label="Estado de carga", interactive=False)
            
            docs_info = gr.Textbox(label="Documentos cargados", value="No hay documentos cargados", interactive=False)
            
            def update_docs_info():
                global documents
                if documents:
                    unique_files = set(doc['filename'] for doc in documents)
                    return f"Documentos cargados: {', '.join(unique_files)} ({len(documents)} fragmentos)"
                return "No hay documentos cargados"
            
            upload_button.click(upload_files, inputs=file_input, outputs=upload_status)
            upload_button.click(update_docs_info, outputs=docs_info)
            clear.click(lambda: "No hay documentos cargados", outputs=docs_info)

demo.launch()