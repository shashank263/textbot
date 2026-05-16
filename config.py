# TestBot Configuration

# Paths
FAISS_INDEX_PATH = "vectorstore/faiss.index"
METADATA_PATH = "vectorstore/metadata.pkl"
CATALOG_PATH = "data/processed_catalog.json"
RAW_CATALOG_PATH = "data/shl_catalog.json"

# LLM Configuration
LLM_MODEL = "llama3"
LLM_BASE_URL = "http://localhost:11434"
LLM_TIMEOUT = 30  # seconds
LLM_TEMPERATURE = 0.7

# Embedding Configuration
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_BATCH_SIZE = 32

# Recommendation Configuration
MAX_RECOMMENDATIONS = 5
MIN_SCORE_THRESHOLD = 0.2
SEARCH_TOP_K = 15

# Ranking Weights (must sum to 1.0)
RANKING_WEIGHTS = {
    "semantic_similarity": 0.5,
    "skill_overlap": 0.3,
    "role_match": 0.2
}

# API Configuration
API_HOST = "0.0.0.0"
API_PORT = 8000
DEBUG = True

# CORS
CORS_ORIGINS = ["*"]

# Rate Limiting
ENABLE_RATE_LIMIT = False
RATE_LIMIT_REQUESTS = 100
RATE_LIMIT_WINDOW = 60  # seconds

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "testbot.log"
