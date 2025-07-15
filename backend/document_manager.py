from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.chat_models import ChatOllama
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.prompts import PromptTemplate
import os
import glob

class DocumentManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DocumentManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance
    
    def __init__(self):
        if not self.initialized:
            self.documents = {}  # Store document name -> vectorstore mapping
            self.combined_vectorstore = None
            self.llm = None
            self.embeddings = None
            self.initialized = True
    
    def setup_llm(self, model_name="llama3:8b", streaming=True, temperature=0.1):
        """Initialize the LLM with specified parameters"""
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        self.llm = ChatOllama(
            model=model_name,
            streaming=streaming,
            callbacks=callbacks,
            base_url="http://host.docker.internal:11434",  # Connect to host machine Ollama
            temperature=temperature,  # Lower = more deterministic/cold
            system="Eres un asistente que SIEMPRE responde en español. Sin importar el idioma de entrada, tu respuesta debe estar completamente en español. Eres un ingeniero químico de COMPANY_NAME especializado en seguridad industrial y alertas de incidentes."
        )
        print(f"LLM initialized - Model: {model_name}, Temperature: {temperature}, Language: Español")
        return self.llm
    
    def load_documents(self, pdf_dir="./pdfs"):
        """Load all PDFs from a directory and create vector stores"""
        if not os.path.exists(pdf_dir):
            os.makedirs(pdf_dir)
            print(f"Created directory {pdf_dir}")
            return False
            
        pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))
        
        if not pdf_files:
            print(f"No PDF files found in {pdf_dir}")
            return False
            
        print(f"\nFound {len(pdf_files)} PDF files:")
        for pdf in pdf_files:
            print(f"- {os.path.basename(pdf)}")
            
        all_docs = []
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        for pdf_path in pdf_files:
            doc_name = os.path.basename(pdf_path)
            print(f"\nProcessing {doc_name}...")
            
            # Load and split document
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            
            # Add document source to metadata
            for doc in docs:
                doc.metadata["source_file"] = doc_name
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=30)
            chunks = splitter.split_documents(docs)
            
            # Store individual document vectorstore
            self.documents[doc_name] = FAISS.from_documents(chunks, embedding=self.embeddings)
            
            # Collect all chunks for combined vectorstore
            all_docs.extend(chunks)
        
        # Create combined vectorstore
        print("\nCreating combined vector store...")
        self.combined_vectorstore = FAISS.from_documents(all_docs, embedding=self.embeddings)
        
        return True
    
    def get_document_names(self):
        """Get list of loaded document names"""
        return list(self.documents.keys())
    
    def get_vectorstore(self, doc_name=None):
        """Get vectorstore for a specific document or combined store"""
        if doc_name is None:
            return self.combined_vectorstore
        return self.documents.get(doc_name)
    
    def create_company_name_engineer_prompt(self):
        """Create a custom prompt for COMPANY_NAME chemical engineer persona"""
        template = """Eres un ingeniero químico experimentado de COMPANY_NAME especializado en alertas de incidentes y respuestas rápidas.

INSTRUCCIONES CRÍTICAS:
- SIEMPRE responde en ESPAÑOL, sin excepción
- Responde en MÁXIMO 3-4 frases cortas
- Sé directo, conciso y específico
- Enfócate solo en lo más importante y urgente
- Usa viñetas si es necesario para claridad
- No agregues información de contexto innecesaria
- Independientemente del idioma de la pregunta, tu respuesta debe ser en español

Contexto de documentos:
{context}

Alerta/Pregunta:
{question}

Respuesta breve y específica como ingeniero de COMPANY_NAME (en español):"""

        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def create_qa_chain(self, doc_name=None, streaming=True, temperature=0.1):
        """Create a QA chain for a specific document or all documents"""
        if self.llm is None:
            self.setup_llm(streaming=streaming, temperature=temperature)
            
        vectorstore = self.get_vectorstore(doc_name)
        if vectorstore is None:
            raise ValueError(f"Document '{doc_name}' not found")
        
        # Create custom prompt for COMPANY_NAME engineer persona
        custom_prompt = self.create_company_name_engineer_prompt()
            
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
            chain_type="stuff",
            return_source_documents=True,
            chain_type_kwargs={"prompt": custom_prompt}
        )
    
    def query_document(self, query, doc_name=None, streaming=True, temperature=0.1):
        """Query a specific document or all documents"""
        print("\n=== Document Manager Query ===")
        print(f"Received query: {query}")
        print(f"Document name: {doc_name}")
        print(f"Streaming: {streaming}")
        print(f"Temperature: {temperature}")
        
        try:
            print("\nCreating QA chain...")
            qa_chain = self.create_qa_chain(doc_name, streaming, temperature)
            print("QA chain created successfully")
            
            print("\nInvoking QA chain...")
            result = qa_chain.invoke({"query": query})
            print("QA chain invoked successfully")
            
            print(f"\nResult: {result}")
            return result
            
        except Exception as e:
            print(f"\nError in query_document: {str(e)}")
            print(f"Error type: {type(e)}")
            return {"error": str(e)}

def format_sources(source_documents):
    """Format source documents for display"""
    sources = []
    for i, doc in enumerate(source_documents, 1):
        source = {
            "number": i,
            "document": doc.metadata.get('source_file', 'Unknown'),
            "page": doc.metadata.get('page', 'Unknown'),
            "excerpt": doc.page_content[:200]
        }
        sources.append(source)
    return sources