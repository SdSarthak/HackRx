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
import logging
from datetime import datetime
from colorama import init, Fore, Style

# Suppress NumPy/SciPy warnings
warnings.filterwarnings("ignore", message="A NumPy version.*is required for this version of SciPy")

# Initialize colorama for colored terminal output
init(autoreset=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global metrics tracking with weighted scoring
class MetricsTracker:
    def __init__(self):
        self.total_requests = 0
        self.successful_requests = 0
        self.total_questions = 0
        self.successful_answers = 0
        self.response_times = []
        self.total_weighted_score = 0.0
        self.max_possible_score = 0.0
        self.question_details = []  # Store detailed question results
        
    def record_request(self, success: bool, num_questions: int, successful_questions: int, response_time: float, 
                      weighted_score: float = 0.0, max_score: float = 0.0, question_results: list = None):
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        self.total_questions += num_questions
        self.successful_answers += successful_questions
        self.response_times.append(response_time)
        self.total_weighted_score += weighted_score
        self.max_possible_score += max_score
        
        if question_results:
            self.question_details.extend(question_results)
        
    def get_overall_accuracy(self) -> float:
        if self.total_questions == 0:
            return 0.0
        return (self.successful_answers / self.total_questions) * 100
    
    def get_weighted_score_percentage(self) -> float:
        if self.max_possible_score == 0:
            return 0.0
        return (self.total_weighted_score / self.max_possible_score) * 100
    
    def get_request_success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def get_average_response_time(self) -> float:
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_document_breakdown(self) -> dict:
        """Get breakdown by document type"""
        known_score = 0.0
        unknown_score = 0.0
        known_max = 0.0
        unknown_max = 0.0
        
        for result in self.question_details:
            if result['doc_type'] == 'known':
                known_score += result['score_contribution']
                known_max += result['max_contribution']
            else:
                unknown_score += result['score_contribution']
                unknown_max += result['max_contribution']
        
        return {
            'known': {'score': known_score, 'max': known_max, 'percentage': (known_score/known_max*100) if known_max > 0 else 0},
            'unknown': {'score': unknown_score, 'max': unknown_max, 'percentage': (unknown_score/unknown_max*100) if unknown_max > 0 else 0}
        }

# Global metrics instance
metrics_tracker = MetricsTracker()

# Global metrics instance
metrics_tracker = MetricsTracker()

def classify_document_type(doc_url: str) -> tuple:
    """
    Classify document as known or unknown based on URL patterns
    Returns (doc_type, weight)
    """
    # Known document patterns (adjust as needed)
    known_patterns = [
        'arogya-sanjeevani',
        'policy-document',
        'standard-terms',
        'common-clauses'
    ]
    
    doc_url_lower = doc_url.lower()
    for pattern in known_patterns:
        if pattern in doc_url_lower:
            return ('known', 0.5)
    
    # Unknown documents get higher weight
    return ('unknown', 2.0)

def calculate_question_weight(question: str) -> float:
    """
    Calculate question weight based on complexity indicators
    """
    question_lower = question.lower()
    
    # High complexity indicators (weight 2.0)
    high_complexity = [
        'calculate', 'computation', 'formula', 'percentage', 'amount',
        'premium', 'deductible', 'co-payment', 'sum insured',
        'compare', 'difference', 'analysis', 'evaluate'
    ]
    
    # Medium complexity indicators (weight 1.5)
    medium_complexity = [
        'explain', 'describe', 'define', 'process', 'procedure',
        'requirements', 'conditions', 'eligibility', 'coverage'
    ]
    
    # Check for high complexity
    for indicator in high_complexity:
        if indicator in question_lower:
            return 2.0
    
    # Check for medium complexity
    for indicator in medium_complexity:
        if indicator in question_lower:
            return 1.5
    
    # Default weight for simple questions
    return 1.0

def print_weighted_score_breakdown(request_score: float, max_request_score: float, question_results: list):
    """Print detailed weighted score breakdown"""
    weighted_percentage = (request_score / max_request_score * 100) if max_request_score > 0 else 0
    
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}🧮 WEIGHTED SCORING BREAKDOWN{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")
    
    # Document type breakdown
    known_score = sum(r['score_contribution'] for r in question_results if r['doc_type'] == 'known')
    unknown_score = sum(r['score_contribution'] for r in question_results if r['doc_type'] == 'unknown')
    known_max = sum(r['max_contribution'] for r in question_results if r['doc_type'] == 'known')
    unknown_max = sum(r['max_contribution'] for r in question_results if r['doc_type'] == 'unknown')
    
    print(f"{Fore.WHITE}📄 Known Documents Contribution: {known_score:.1f}/{known_max:.1f} ({(known_score/known_max*100) if known_max > 0 else 0:.1f}%){Style.RESET_ALL}")
    print(f"{Fore.WHITE}🔒 Unknown Documents Contribution: {unknown_score:.1f}/{unknown_max:.1f} ({(unknown_score/unknown_max*100) if unknown_max > 0 else 0:.1f}%){Style.RESET_ALL}")
    print(f"{Fore.WHITE}{'='*40}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}🎯 Total Weighted Score: {request_score:.1f}/{max_request_score:.1f} ({weighted_percentage:.1f}%){Style.RESET_ALL}")
    
    # Question-level breakdown
    print(f"{Fore.CYAN}📝 Question Breakdown:{Style.RESET_ALL}")
    for i, result in enumerate(question_results, 1):
        status = "✅" if result['correct'] else "❌"
        print(f"{Fore.WHITE}   Q{i}: {status} Weight: {result['question_weight']:.1f} × Doc: {result['doc_weight']:.1f} = {result['score_contribution']:.1f}/{result['max_contribution']:.1f}{Style.RESET_ALL}")
    
    print(f"{Fore.YELLOW}{'='*80}{Style.RESET_ALL}")

def print_accuracy_indicator(accuracy: float, context: str = "", weighted_score: float = None):
    """Print colored accuracy indicator based on score"""
    if accuracy >= 90:
        color = Fore.GREEN
        rating = "EXCELLENT"
    elif accuracy >= 75:
        color = Fore.CYAN
        rating = "GOOD"
    elif accuracy >= 60:
        color = Fore.YELLOW
        rating = "FAIR"
    else:
        color = Fore.RED
        rating = "NEEDS IMPROVEMENT"
    
    print(f"{color}{'='*60}{Style.RESET_ALL}")
    print(f"{color}📊 ACCURACY INDICATOR {context}{Style.RESET_ALL}")
    print(f"{color}Simple Accuracy: {accuracy:.1f}% ({rating}){Style.RESET_ALL}")
    if weighted_score is not None:
        print(f"{color}Weighted Score: {weighted_score:.1f}% ({rating}){Style.RESET_ALL}")
    print(f"{color}{'='*60}{Style.RESET_ALL}")

def print_session_metrics():
    """Print comprehensive session metrics"""
    overall_accuracy = metrics_tracker.get_overall_accuracy()
    weighted_score_percentage = metrics_tracker.get_weighted_score_percentage()
    request_success_rate = metrics_tracker.get_request_success_rate()
    avg_response_time = metrics_tracker.get_average_response_time()
    doc_breakdown = metrics_tracker.get_document_breakdown()
    
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}📈 COMPREHENSIVE SESSION METRICS DASHBOARD{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}🎯 Simple Accuracy: {overall_accuracy:.1f}% ({metrics_tracker.successful_answers}/{metrics_tracker.total_questions}){Style.RESET_ALL}")
    print(f"{Fore.WHITE}🧮 Weighted Score: {weighted_score_percentage:.1f}% ({metrics_tracker.total_weighted_score:.1f}/{metrics_tracker.max_possible_score:.1f}){Style.RESET_ALL}")
    print(f"{Fore.WHITE}✅ Request Success Rate: {request_success_rate:.1f}% ({metrics_tracker.successful_requests}/{metrics_tracker.total_requests}){Style.RESET_ALL}")
    print(f"{Fore.WHITE}⏱️  Average Response Time: {avg_response_time:.2f}s{Style.RESET_ALL}")
    print(f"{Fore.WHITE}📊 Total Requests Processed: {metrics_tracker.total_requests}{Style.RESET_ALL}")
    
    if doc_breakdown['known']['max'] > 0 or doc_breakdown['unknown']['max'] > 0:
        print(f"{Fore.WHITE}{'─'*40}{Style.RESET_ALL}")
        print(f"{Fore.WHITE}📄 Known Docs: {doc_breakdown['known']['percentage']:.1f}% ({doc_breakdown['known']['score']:.1f}/{doc_breakdown['known']['max']:.1f}){Style.RESET_ALL}")
        print(f"{Fore.WHITE}🔒 Unknown Docs: {doc_breakdown['unknown']['percentage']:.1f}% ({doc_breakdown['unknown']['score']:.1f}/{doc_breakdown['unknown']['max']:.1f}){Style.RESET_ALL}")
    
    print(f"{Fore.MAGENTA}{'='*80}{Style.RESET_ALL}")
    
    # Print color-coded overall performance based on weighted score
    primary_score = weighted_score_percentage if weighted_score_percentage > 0 else overall_accuracy
    print_accuracy_indicator(primary_score, "- OVERALL SESSION PERFORMANCE")

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

@app.post("/hackrx/run")
async def run_hackrx(request: HackRxRequest, authorization: str = Header(None, alias="Authorization")):
    """Main HackRX endpoint with simple response format"""
    start_time = time.time()
    
    # Print request start indicator
    print(f"{Fore.BLUE}{'='*80}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}🚀 NEW REQUEST RECEIVED - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}📄 Documents: {len(request.documents if isinstance(request.documents, list) else [request.documents])}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}❓ Questions: {len(request.questions)}{Style.RESET_ALL}")
    print(f"{Fore.BLUE}{'='*80}{Style.RESET_ALL}")
    
    # Validate token
    if not authorization:
        raise HTTPException(status_code=401, detail="Unauthorized: Missing Authorization header")
    
    # Extract token from Bearer format
    if authorization.startswith("Bearer "):
        token = authorization[7:]  # Remove "Bearer " prefix
    else:
        token = authorization
    
    if token != api_key:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API key")

    if not google_api_key:
        raise HTTPException(status_code=500, detail="Google API key not configured")

    if not LANGCHAIN_AVAILABLE:
        raise HTTPException(status_code=503, detail="Service temporarily unavailable - LangChain dependencies missing")

    successful_questions = 0
    request_success = False
    request_weighted_score = 0.0
    max_request_score = 0.0
    question_results = []

    try:
        # Handle both single document and multiple documents
        document_urls = request.documents if isinstance(request.documents, list) else [request.documents]
        
        # Classify documents and calculate weights
        document_info = []
        for doc_url in document_urls:
            doc_type, doc_weight = classify_document_type(doc_url)
            document_info.append({
                'url': doc_url,
                'type': doc_type,
                'weight': doc_weight
            })
            print(f"{Fore.MAGENTA}📄 Document: {doc_type.upper()} (Weight: {doc_weight}x) - {doc_url[:60]}...{Style.RESET_ALL}")
        
        all_chunks = []
        
        # Process each document
        for doc_info in document_info:
            # Download PDF from URL
            pdf_path = download_pdf_from_url(doc_info['url'])
            
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

        # Process each question with individual tracking and weighted scoring
        for i, q in enumerate(questions):
            question_start_time = time.time()
            question_weight = calculate_question_weight(q)
            
            # For simplicity, assign questions to documents in round-robin fashion
            # In a real system, you'd determine which document each question pertains to
            doc_info = document_info[i % len(document_info)]
            doc_weight = doc_info['weight']
            max_contribution = question_weight * doc_weight
            max_request_score += max_contribution
            
            print(f"{Fore.CYAN}📝 Processing Question {i+1}/{len(questions)} (Weight: {question_weight:.1f}x, Doc: {doc_info['type']}):{Style.RESET_ALL}")
            print(f"{Fore.CYAN}   {q[:70]}{'...' if len(q) > 70 else ''}{Style.RESET_ALL}")
            
            retry_count = 0
            question_success = False
            while retry_count < max_retries:
                try:
                    response = chatlm.invoke(q)
                    answers.append(response["answer"])
                    question_success = True
                    successful_questions += 1
                    break
                except Exception as e:
                    retry_count += 1
                    print(f"{Fore.YELLOW}⚠️  Retry {retry_count}/{max_retries} for question {i+1}: {str(e)[:100]}{Style.RESET_ALL}")
                    if retry_count >= max_retries:
                        answers.append(f"Unable to process question due to: {str(e)}")
                        break
                    await asyncio.sleep(2)  # Wait before retry
            
            # Calculate weighted score contribution
            score_contribution = max_contribution if question_success else 0.0
            request_weighted_score += score_contribution
            
            # Store question result for detailed breakdown
            question_results.append({
                'question': q,
                'correct': question_success,
                'question_weight': question_weight,
                'doc_type': doc_info['type'],
                'doc_weight': doc_weight,
                'score_contribution': score_contribution,
                'max_contribution': max_contribution
            })
            
            # Print individual question result
            question_time = time.time() - question_start_time
            if question_success:
                print(f"{Fore.GREEN}✅ Question {i+1} completed successfully in {question_time:.2f}s (Score: +{score_contribution:.1f}){Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}❌ Question {i+1} failed after {max_retries} retries in {question_time:.2f}s (Score: +0.0){Style.RESET_ALL}")
            
            # Add delay between questions to respect rate limits
            if i < len(questions) - 1:  # Don't delay after the last question
                await asyncio.sleep(question_delay)
        
        request_success = True
        
        # Calculate and display request-level metrics
        total_response_time = time.time() - start_time
        request_accuracy = (successful_questions / len(questions)) * 100
        weighted_accuracy = (request_weighted_score / max_request_score * 100) if max_request_score > 0 else 0
        
        # Print request completion summary
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🎉 REQUEST COMPLETED SUCCESSFULLY{Style.RESET_ALL}")
        print(f"{Fore.GREEN}✅ Questions Answered: {successful_questions}/{len(questions)}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}⏱️  Total Response Time: {total_response_time:.2f}s{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🧮 Weighted Score: {request_weighted_score:.1f}/{max_request_score:.1f} ({weighted_accuracy:.1f}%){Style.RESET_ALL}")
        print(f"{Fore.GREEN}{'='*80}{Style.RESET_ALL}")
        
        # Show detailed weighted score breakdown
        print_weighted_score_breakdown(request_weighted_score, max_request_score, question_results)
        
        # Show accuracy indicator for this request
        print_accuracy_indicator(request_accuracy, f"- REQUEST PERFORMANCE", weighted_accuracy)
        
        # Record metrics with weighted scoring
        metrics_tracker.record_request(
            request_success, len(questions), successful_questions, total_response_time,
            request_weighted_score, max_request_score, question_results
        )
        
        # Print updated session metrics
        print_session_metrics()
        
        return {"answers": answers}
    
    except requests.RequestException as e:
        # Record failed request
        total_response_time = time.time() - start_time
        metrics_tracker.record_request(False, len(request.questions), successful_questions, total_response_time,
                                     0.0, max_request_score, question_results)
        
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ REQUEST FAILED - DOCUMENT DOWNLOAD ERROR{Style.RESET_ALL}")
        print(f"{Fore.RED}⏱️  Failed after: {total_response_time:.2f}s{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print_session_metrics()
        
        raise HTTPException(status_code=400, detail=f"Failed to download document: {str(e)}")
    except Exception as e:
        # Record failed request
        total_response_time = time.time() - start_time
        metrics_tracker.record_request(False, len(request.questions), successful_questions, total_response_time,
                                     0.0, max_request_score, question_results)
        
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print(f"{Fore.RED}❌ REQUEST FAILED - PROCESSING ERROR{Style.RESET_ALL}")
        print(f"{Fore.RED}⏱️  Failed after: {total_response_time:.2f}s{Style.RESET_ALL}")
        print(f"{Fore.RED}📝 Error: {str(e)[:100]}...{Style.RESET_ALL}")
        print(f"{Fore.RED}{'='*80}{Style.RESET_ALL}")
        print_session_metrics()
        
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
@app.post("hackrx/run")
async def run_hackrx_legacy(request: HackRxRequest, authorization: str = Header(None, alias="Authorization")):
    """Legacy endpoint for backward compatibility"""
    return await run_hackrx(request, authorization)

# === Run Application ===
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)