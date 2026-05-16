
from fastapi import APIRouter, HTTPException
from typing import List, Dict
import os
import pickle
import json
import faiss
from sentence_transformers import SentenceTransformer

from app.models.schemas import ChatRequest, ChatResponse, Recommendation
from app.services.parser import RequirementParser
from app.services.retrieval import CatalogProcessor
from app.services.ranking import RankingService
from app.services.recommender import RecommenderService
from app.services.comparison import ComparisonService
from app.services.guardrails import GuardrailsService
from app.services.llm_service import LLMService
from app.utils.helpers import extract_latest_user_message, extract_conversation_context


router = APIRouter()

# Global service instances
parser = RequirementParser()
guardrails = GuardrailsService()
comparison_service = ComparisonService()
llm_service = LLMService()
recommender_service = RecommenderService()
ranking_service = RankingService()

# FAISS index and metadata
faiss_index = None
metadata = None
embeddings_model = None


def _load_vectorstore():
    """Load FAISS index and metadata on first use."""
    global faiss_index, metadata, embeddings_model
    
    if faiss_index is not None:
        return True
    
    try:
        # Load FAISS index
        index_path = "vectorstore/faiss.index"
        metadata_path = "vectorstore/metadata.pkl"
        
        if not os.path.exists(index_path) or not os.path.exists(metadata_path):
            print("WARNING: Vectorstore not found. Please run scraper and generate embeddings first.")
            return False
        
        faiss_index = faiss.read_index(index_path)
        
        with open(metadata_path, 'rb') as f:
            metadata = pickle.load(f)
        
        embeddings_model = SentenceTransformer("all-MiniLM-L6-v2")
        
        return True
        
    except Exception as e:
        print(f"Error loading vectorstore: {e}")
        return False


def _search_assessments(query: str, top_k: int = 10) -> List[tuple]:
    """
    Search FAISS index for similar assessments.
    
    Returns: List of (assessment_dict, distance)
    """
    if not _load_vectorstore():
        return []
    
    try:
        # Embed query
        query_embedding = embeddings_model.encode([query])[0]
        
        # Search FAISS
        distances, indices = faiss_index.search(
            query_embedding.reshape(1, -1).astype('float32'),
            top_k
        )
        
        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx < len(metadata["assessments"]):
                assessment = metadata["assessments"][idx]
                results.append((assessment, distance))
        
        return results
        
    except Exception as e:
        print(f"Search error: {e}")
        return []


def _build_search_query(parsed_intent) -> str:
    parts = []

    if parsed_intent.role:
        parts.append(parsed_intent.role)

    if parsed_intent.experience:
        parts.append(parsed_intent.experience)

    if parsed_intent.skills:
        parts.extend([s.lower() for s in parsed_intent.skills])

    if parsed_intent.traits:
        parts.extend(parsed_intent.traits)

    if parsed_intent.personality_required:
        parts.append("personality")

    return " ".join(parts) if parts else "assessment"


@router.post("/chat")
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        latest_message = extract_latest_user_message(
            [msg.dict() for msg in request.messages]
        )

        if not latest_message:
            raise HTTPException(status_code=400, detail="No user message provided")

        # STEP 1: Safety check
        is_safe, refusal_reason = guardrails.check_safety(latest_message)
        if not is_safe:
            return ChatResponse(
                reply=guardrails.generate_refusal(refusal_reason),
                recommendations=[],
                end_of_conversation=False
            )

        # STEP 2: Comparison
        if guardrails.is_comparison_request(latest_message):
            comparison_intent = comparison_service.extract_comparison_intent(latest_message)
            if comparison_intent:
                comparison_result = comparison_service.compare(
                    comparison_intent[0],
                    comparison_intent[1]
                )
                return ChatResponse(
                    reply=comparison_result,
                    recommendations=[],
                    end_of_conversation=False
                )

        # STEP 3: Parse
        context = extract_conversation_context([msg.dict() for msg in request.messages])
        parsed_intent = parser.parse([msg.dict() for msg in request.messages])

        # STEP 4: Clarification fix
        missing_role = parsed_intent.role is None
        missing_exp = parsed_intent.experience is None

        if missing_role and missing_exp:
            questions = parser.suggest_clarification_questions(parsed_intent)

            return ChatResponse(
                reply="To help you find the best assessment, " + " ".join(questions),
                recommendations=[],
                end_of_conversation=False
            )

        # STEP 5: Search
        search_query = _build_search_query(parsed_intent)
        search_results = _search_assessments(search_query, top_k=15)

        if not search_results:
            fallback_query = parsed_intent.role or " ".join(parsed_intent.skills) if parsed_intent.skills else "assessment"
            search_results = _search_assessments(fallback_query, top_k=10)

        if not search_results:
            return ChatResponse(
                reply="No suitable assessments found. Please provide more details.",
                recommendations=[],
                end_of_conversation=False
            )

        # STEP 6: Rank
        assessments = [item[0] for item in search_results]
        distances = [item[1] for item in search_results]

        ranked = ranking_service.rank_assessments(
            assessments,
            parsed_intent,
            distances
        )

        # STEP 7: Clean
        if ranked:
            ranked = ranking_service.remove_duplicates(ranked)
            ranked = ranking_service.filter_low_scoring(ranked, min_score=0.2)

        if not ranked:
            return ChatResponse(
                reply="I found some assessments, but none strongly match your requirements. Try adding more details like skills or experience level.",
                recommendations=[],
                end_of_conversation=False
    )

        # STEP 8: Recommend
        recommendations = recommender_service.create_recommendations(
            ranked,
            max_recommendations=5
        )

        if not recommendations:
            return ChatResponse(
                reply="No matching SHL assessments found. Please refine your requirements.",
                recommendations=[],
                end_of_conversation=False
        )

        # STEP 9: Response
        final_reply = recommender_service.format_recommendations_text(recommendations)

        return ChatResponse(
            reply=final_reply,
            recommendations=recommendations,
            end_of_conversation=False
        )
    
    except Exception as e:
        print(f"Error in /chat: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")