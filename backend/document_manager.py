from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from azure.ai.inference import ChatCompletionsClient
from azure.core.credentials import AzureKeyCredential
from langchain.llms.base import LLM
from typing import Any, List, Mapping, Optional
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import os
import glob

class AzureDeepSeekLLM(LLM):
    """Custom LangChain LLM wrapper for Azure DeepSeek"""
    
    client: Any
    
    def __init__(self, endpoint: str, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version="2024-05-01-preview"
        )
    
    @property
    def _llm_type(self) -> str:
        return "azure_deepseek"
    
    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any,
    ) -> str:
        try:
            response = self.client.complete(
                messages=[
                    {"role": "system", "content": "Eres un asistente especializado de BASF. Responde de manera profesional y precisa sobre química, sostenibilidad y productos de BASF."},
                    {"role": "user", "content": prompt}
                ],
                model="DeepSeek-R1",  # Specify the model explicitly
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling Azure DeepSeek: {e}")
            return "Lo siento, no pude procesar tu consulta en este momento."
    
    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        return {"endpoint": "Azure DeepSeek"}

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
    
    def setup_llm(self, model_name="deepseek-chat", streaming=True):
        """Initialize the LLM with Azure DeepSeek"""
        callbacks = [StreamingStdOutCallbackHandler()] if streaming else []
        self.llm = AzureDeepSeekLLM(
            endpoint="https://ucuhackathon.services.ai.azure.com/models",
            api_key="5DP6sQynq2A3kkwfI1CzrGRF5oql9bnkBDimRIuEIRlyuvGFHY5jJQQJ99BFACYeBjFXJ3w3AAAAACOG405s",
            callbacks=callbacks
        )
        print(f"llm: {self.llm}")
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
            
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
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
    
    def create_qa_chain(self, doc_name=None, streaming=True):
        """Create a QA chain for a specific document or all documents"""
        if self.llm is None:
            self.setup_llm(streaming=streaming)
            
        vectorstore = self.get_vectorstore(doc_name)
        if vectorstore is None:
            raise ValueError(f"Document '{doc_name}' not found")
            
        return RetrievalQA.from_chain_type(
            llm=self.llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            chain_type="stuff",
            return_source_documents=True
        )
    
    def query_document(self, query, doc_name=None, streaming=True):
        """Query a specific document or all documents"""
        print("\n=== Document Manager Query ===")
        print(f"Received query: {query}")
        print(f"Document name: {doc_name}")
        print(f"Streaming: {streaming}")
        
        try:
            print("\nCreating QA chain...")
            qa_chain = self.create_qa_chain(doc_name, streaming)
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