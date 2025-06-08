from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from document_manager import DocumentManager, format_sources
import json
import os
import mail_sender

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

        if not query_text.strip():
            raise HTTPException(status_code=400, detail="'text' field cannot be empty")

        print(f"\nProcessing query:")
        print(f"text: {query_text}")
        print(f"document_name: {doc_name}")

        # Query the document
        result = doc_manager.query_document(
            query=query_text,
            doc_name=doc_name,
            streaming=False
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        # Prepare response
        response = {
            "answer": str(result["result"]),
            "sources": format_sources(result["source_documents"])
        }
        mail_res = mail_sender.enviar_correo(response.get)
        print(f"Email sent successfully: {mail_res}")
        if not mail_res:
            raise HTTPException(status_code=500, detail="Failed to send email")
        print("\n=== Processed Query ===")

        print("\n=== Response Data ===")
        print(json.dumps(response, indent=2))
        
        return response

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON in request body")
    except Exception as e:
        print(f"\nError processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
