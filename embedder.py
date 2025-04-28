import logging
from sentence_transformers import SentenceTransformer
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
from langchain.embeddings.base import Embeddings  # Import LangChain's Embeddings base class

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SentenceTransformerEmbeddings(Embeddings):  # Inherit from Embeddings
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)

    def embed_documents(self, texts):
        """Embed a list of documents."""
        return self.model.encode(texts, convert_to_tensor=False).tolist()

    def embed_query(self, text):
        """Embed a single query."""
        return self.model.encode([text], convert_to_tensor=False).tolist()[0]

def create_embeddings(resume_text, ats_results, persist_directory="./data/faiss_db"):
    try:
        if not resume_text or not ats_results:
            logger.error("Resume text or ATS results missing")
            raise ValueError("Resume text and ATS results are required")
        
        # Initialize the embeddings
        embeddings = SentenceTransformerEmbeddings('all-MiniLM-L6-v2')
        
        # Prepare texts for embedding
        texts = [resume_text] + [
            f"{key}: {', '.join(value) if isinstance(value, list) else value}"
            for key, value in ats_results.items() if key != "ats_compatibility_score"
        ]
        documents = [Document(page_content=text, metadata={"source": "resume" if i == 0 else "ats"}) for i, text in enumerate(texts)]
        
        # Create FAISS vector store
        vectorstore = FAISS.from_documents(documents, embeddings)
        vectorstore.save_local(persist_directory)
        logger.debug(f"Created FAISS embeddings, stored in {persist_directory}")
        return vectorstore
    except Exception as e:
        logger.error(f"Embedding error: {str(e)}")
        raise RuntimeError(f"Failed to create embeddings: {str(e)}")