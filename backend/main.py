from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from document_manager import DocumentManager, format_sources
import json
import os
import mail_sender
import urllib.parse

app = FastAPI(
    title="My FastAPI App",
    description="A simple FastAPI application",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize document manager
doc_manager = DocumentManager()

# Configuration
FRONTEND_PORT = 3000

def generate_context_url(message: str) -> str:
    """Generate a URL with the LLM response encoded as a parameter"""
    encoded_message = urllib.parse.quote(message)
    context_url = f"http://localhost:{FRONTEND_PORT}?data={encoded_message}"
    return context_url

def truncate_response(text: str, max_words: int = 50) -> str:
    """Truncate response to maximum number of words"""
    words = text.split()
    if len(words) > max_words:
        truncated = ' '.join(words[:max_words])
        return f"{truncated}... [Respuesta truncada. Ver completa en chatbot]"
    return text

@app.on_event("startup")
async def startup_event():
    """Load documents when the API starts"""
    if not doc_manager.load_documents():
        print("Warning: No documents loaded. Please add PDFs to the 'pdfs' directory.")

@app.get("/")
async def read_root():
    return {"message": "Hello World", "status": "success"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q} 

##PRUEBA USO DE RAG HANDLER
@app.post("/query")
async def query_documents(request: Request):
    """Query documents and get response"""
    try:
        # Get raw request data
        data = await request.json()
        print("\n=== Raw Request Data ===")
        print(json.dumps(data, indent=2))

        # Validate required fields
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="Request body must be a JSON object")
        
        if "text" not in data:
            raise HTTPException(status_code=400, detail="'text' field is required")
        
        query_text = str(data["text"])
        doc_name = data.get("document_name")
        temperature = data.get("temperature", 0.1)  # Default: very cold/deterministic

        if not query_text.strip():
            raise HTTPException(status_code=400, detail="'text' field cannot be empty")

        print(f"\nProcessing query:")
        print(f"text: {query_text}")
        print(f"document_name: {doc_name}")
        print(f"temperature: {temperature}")

        # Query the document
        result = doc_manager.query_document(
            query=query_text,
            doc_name=doc_name,
            streaming=False,
            temperature=temperature,
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Generate context URL with full response
        answer_text = str(result["result"])
        context_url = generate_context_url(answer_text)
        
        # Truncate response for better UX 
        truncated_answer = truncate_response(answer_text, max_words=40)
        
        print(f"\n🔗 GENERANDO URL DE CONTEXTO:")
        print(f"   Respuesta original: {len(answer_text.split())} palabras")
        print(f"   Respuesta truncada: {len(truncated_answer.split())} palabras")
        print(f"   URL generada: {context_url}")
        print(f"   Puerto frontend: {FRONTEND_PORT}")
        
        # Prepare response with truncated answer
        response = {
            "answer": truncated_answer,
            "sources": format_sources(result["source_documents"]),
            "context_url": context_url
        }
        
        # Only send email for alert/incident scenarios (when answer contains "Alerta" or "Protocolo")
        if "alerta" in answer_text.lower() or "protocolo" in answer_text.lower() or "emergencia" in answer_text.lower():
            print("🚨 Detectada alerta/protocolo de emergencia - Enviando email")
            mail_res = mail_sender.enviar_correo(query_text, context_url)
            print(f"Email sent successfully: {mail_res}")
        else:
            print("💬 Consulta normal - No se envía email")
            mail_res = True  # No error for normal queries
        print("\n=== Processed Query ===")

        print("\n=== Response Data ===")
        print(json.dumps(response, indent=2))
        print(f"\n=== Context URL Generated ===")
        print(f"URL: {context_url}")
        
        return response

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"\nError processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
