from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from document_manager import DocumentManager, format_sources
from report_generator import ReportGenerator
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
        
        print(f"\n🔗 GENERANDO URL DE CONTEXTO:")
        print(f"   Respuesta completa: {len(answer_text.split())} palabras")
        print(f"   URL generada: {context_url}")
        print(f"   Puerto frontend: {FRONTEND_PORT}")
        
        # Prepare response with full answer
        response = {
            "answer": answer_text,
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

@app.post("/generate-report")
async def generate_report(request: Request):
    """Generate a PDF report from conversation data"""
    try:
        # Get conversation data
        data = await request.json()
        print("\n=== Generate Report Request ===")
        print(f"Received data keys: {list(data.keys())}")
        
        if "conversation" not in data:
            raise HTTPException(status_code=400, detail="'conversation' field is required")
        
        conversation_data = data["conversation"]
        print(f"Conversation messages count: {len(conversation_data.get('messages', []))}")
        
        # Generate PDF report
        report_generator = ReportGenerator()
        pdf_data = report_generator.generate_conversation_report(conversation_data)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"COMPANY_NAME_Reporte_Incidente_{timestamp}.pdf"
        
        print(f"✅ PDF generated successfully: {filename}")
        print(f"PDF size: {len(pdf_data)} bytes")
        
        # Return PDF as response
        return Response(
            content=pdf_data,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_data))
            }
        )
        
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"\nError generating report: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")
