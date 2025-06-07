import os
from typing import Optional

class Config:
    # Azure AI Foundry settings
    AZURE_AI_ENDPOINT = os.getenv("AZURE_AI_ENDPOINT", "https://ucuhackathon.services.ai.azure.com")
    AZURE_AI_KEY = os.getenv("AZURE_AI_KEY", "5DP6sQynq2A3kkwfI1CzrGRF5oql9bnkBDimRIuEIRlyuvGFHY5jJQQJ99BFACYeBjFXJ3w3AAAAACOG405s")
    
    # Azure Search settings (for vector store)
    AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
    AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
    AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME", "hackaton")
    
    # Vector store configuration
    USE_AZURE_VECTOR_STORE = os.getenv("USE_AZURE_VECTOR_STORE", "false").lower() == "true"
    
    # Embedding model
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    @classmethod
    def get_azure_search_endpoint(cls) -> Optional[str]:
        """Get Azure Search endpoint from environment or construct from AI endpoint"""
        if cls.AZURE_SEARCH_ENDPOINT:
            return cls.AZURE_SEARCH_ENDPOINT
        
        # Try to construct from AI endpoint
        if cls.AZURE_AI_ENDPOINT:
            # Replace the services.ai.azure.com with search.windows.net
            base_url = cls.AZURE_AI_ENDPOINT.replace("https://", "").replace(".services.ai.azure.com", "")
            return f"https://{base_url}.search.windows.net"
        
        return None 