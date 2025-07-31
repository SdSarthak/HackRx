from fastapi import FastAPI, Request, Header, HTTPException
from pydantic import BaseModel
from typing import List, Union
import os
import re
import fitz
import tempfile
import asyncio
import time
import warnings

# Suppress NumPy/SciPy warnings
warnings.filterwarnings("ignore", message="A NumPy version.*is required for this version of SciPy")

# Try to import NLTK with fallback
try:
    import nltk
    from nltk.tokenize import sent_tokenize
    NLTK_AVAILABLE = True
    try:
        nltk.download("punkt", quiet=True)
    except:
        pass
except ImportError:
    NLTK_AVAILABLE = False
    print("Warning: NLTK not available, using basic sentence splitting")

from dotenv import load_dotenv
import requests

# Try to import LangChain with fallbacks for different versions
try:
    from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
    from langchain.chains import ConversationalRetrievalChain
    from langchain.vectorstores import FAISS
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"LangChain import error: {e}")
    try:
        # Try alternative imports for newer versions
        from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
        from langchain_community.chains import ConversationalRetrievalChain
        from langchain_community.vectorstores import FAISS
        from langchain.memory import ConversationBufferMemory
        LANGCHAIN_AVAILABLE = True
    except ImportError:
        try:
            # Try even newer version structure
            from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
            from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
            from langchain_community.vectorstores.faiss import FAISS
            from langchain.memory.buffer import ConversationBufferMemory
            LANGCHAIN_AVAILABLE = True
        except ImportError:
            LANGCHAIN_AVAILABLE = False
            print("Warning: LangChain not properly configured")

# === FastAPI App ===
app = FastAPI(
    title="HackRX Policy QA API",
    description="AI-powered Q&A system for insurance policy documents",
    version="1.0.0"
)

# === Load env variables ===
load_dotenv()
google_api_key = os.getenv("GEMINI_API_KEY")
api_key = os.getenv("API_KEY", "d229e5eb06d6a264c4cebecd4fb0dc33e6a81c7bfa1f01945f751424fcac1e3a")
environment = os.getenv("ENVIRONMENT", "development")
question_delay = int(os.getenv("QUESTION_PROCESSING_DELAY", "8"))
max_retries = int(os.getenv("MAX_RETRIES", "3"))

# === Config ===
MODEL = "gemini-2.5-flash"
DB_NAME = "vector_db"

# === Embeddings + LLM ===
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=google_api_key)


# === Text Preprocessing ===
def download_pdf_from_url(url):
    """Download PDF from URL and return the file path"""
    response = requests.get(url)
    response.raise_for_status()
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.write(response.content)
    temp_file.close()
    
    return temp_file.name

def extract_clean_text_from_pdf(pdf_path):
    document = fitz.open(pdf_path)
    all_text = ""
    for page in document:
        all_text += page.get_text()
    clean_text = re.sub(r"\s+", " ", all_text).strip()
    return clean_text


def basic_sentence_split(text):
    """Basic sentence splitting fallback when NLTK is not available"""
    # Split on common sentence endings
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]

def sentence_chunker(text, max_words=500):
    if NLTK_AVAILABLE:
        sentences = sent_tokenize(text)
    else:
        sentences = basic_sentence_split(text)
    
    chunks = []
    current_chunk = []
    current_len = 0
    for sentence in sentences:
        words = sentence.split()
        if current_len + len(words) > max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0
        current_chunk.append(sentence)
        current_len += len(words)
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def rag_pipeline(chunks):
    if not LANGCHAIN_AVAILABLE:
        raise HTTPException(status_code=500, detail="LangChain dependencies not available")
    
    if os.path.exists(DB_NAME):
        try:
            # Clean up existing vector store
            import shutil
            shutil.rmtree(DB_NAME)
        except:
            pass

    try:
        vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
        
        llm = ChatGoogleGenerativeAI(
            temperature=0.7, 
            model=MODEL, 
            google_api_key=google_api_key,
            convert_system_message_to_human=True
        )
        memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 15})

        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm, retriever=retriever, memory=memory
        )
        return conversation_chain
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create RAG pipeline: {str(e)}")

# === API Models ===
class HackRxRequest(BaseModel):
    documents: Union[str, List[str]]
    questions: List[str]

# === Health Check Endpoint ===
@app.get("/")
async def health_check():
    """Health check endpoint for Render deployment"""
    return {
        "status": "healthy",
        "message": "HackRX Policy QA API is running",
        "endpoint": "/hackrx/run",
        "environment": environment
    }

@app.get("/health")
async def health():
    """Alternative health check endpoint"""
    return {"status": "ok", "service": "hackrx-api"}

# === Main HackRX Endpoint ===
@app.post("/hackrx/run")
async def run_hackrx(request: HackRxRequest, authorization: str = Header(None)):
    """Main HackRX endpoint with simple response format"""
    # Validate token
    if authorization != f"Bearer {api_key}":
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key")

    if not google_api_key:
        raise HTTPException(status_code=500, detail="Google API key not configured")

    if not LANGCHAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - LangChain dependencies missing")

    try:
        # Handle both single document and multiple documents
        document_urls = request.documents if isinstance(request.documents, list) else [request.documents]
        
        all_chunks = []
        
        # Process each document
        for doc_url in document_urls:
            # Download PDF from URL
            pdf_path = download_pdf_from_url(doc_url)
            
            # Process PDF
            clean_text = extract_clean_text_from_pdf(pdf_path)
            chunks = sentence_chunker(clean_text)
            all_chunks.extend(chunks)
            
            # Clean up temporary file
            os.unlink(pdf_path)
        
        # Create RAG pipeline with all chunks
        chatlm = rag_pipeline(all_chunks)
        
        questions = request.questions
        answers = []

        for i, q in enumerate(questions):
            retry_count = 0
            while retry_count < max_retries:
                try:
                    response = chatlm.invoke(q)
                    answers.append(response["answer"])
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count >= max_retries:
                        answers.append(f"Unable to process question due to: {str(e)}")
                        break
                    await asyncio.sleep(2)  # Wait before retry
            
            # Add delay between questions to respect rate limits
            if i < len(questions) - 1:  # Don't delay after the last question
                await asyncio.sleep(question_delay)
        
        return {"answers": answers}
    
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")
    except Exception as e:
        # Clean up any remaining temporary files
        import glob
        temp_files = glob.glob("/tmp/tmp*.pdf")
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except:
                pass
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

# === Legacy Endpoint Support ===
@app.post("/api/v1/hackrx/run")
async def run_hackrx_legacy(request: HackRxRequest, authorization: str = Header(None)):
    """Legacy endpoint for backward compatibility"""
    return await run_hackrx(request, authorization)

# === Run Application ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)