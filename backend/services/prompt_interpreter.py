import os
import json
import google.generativeai as genai
from schemas import StructuredQuery
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """You are an expert game recommendation assistant. Your task is to extract structured information from a user's prompt about the kind of game they want to play.

Return a JSON object with the following fields:
- "genres": Array of strings (e.g. ["RPG", "Shooter"]). Empty array if none.
- "sub_genres": Array of strings (e.g. ["Metroidvania", "Soulslike"]). Empty array if none.
- "mechanics": Array of strings (e.g. ["Turn-based", "Crafting"]). Empty array if none.
- "platform_preference": String or null. (e.g. "PC", "Mobile", "Switch").
- "multiplayer_support": Boolean or null. (true if multiplayer/co-op requested, false if singleplayer requested, null if not mentioned).
- "tone": String or null (e.g. "dark", "relaxing", "funny").
- "intent_summary": A concise, normalized string summarizing the user's core intent.
- "needs_clarification": Boolean. Set to true ONLY if the prompt is extremely vague, contradictory, or lacks any gaming context (e.g. "a fun game", "weather today").
- "suggested_question": String or null. If needs_clarification is true, provide a follow-up question to ask the user.

Ensure your output is ONLY valid JSON without any markdown formatting.
"""

import asyncio

def _sync_embed(text: str):
    return genai.embed_content(
        model="models/gemini-embedding-2",
        content=text,
        task_type="retrieval_query",
        output_dimensionality=768,
    )

async def interpret_prompt(text: str) -> StructuredQuery:
    if not text or not text.strip():
        return StructuredQuery(
            intent_summary="Empty prompt",
            needs_clarification=True,
            suggested_question="Please describe the kind of game you want to play."
        )

    try:
        # 1. Generate Structured Query (using gemini-3.5-flash for speed)
        model = genai.GenerativeModel(
            model_name="gemini-flash-lite-latest",
            system_instruction=SYSTEM_PROMPT,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
            )
        )
        
        response = await model.generate_content_async(text)
        response_text = response.text
        print(f"RAW LLM RESPONSE: {response_text}")
        
        try:
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            structured_data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback if somehow not valid JSON despite mime type
            return StructuredQuery(
                intent_summary="Error parsing intent",
                needs_clarification=True,
                suggested_question="I couldn't quite understand that. Could you describe the game you're looking for in a different way?"
            )

        query = StructuredQuery(**structured_data)
        
        # If it doesn't need clarification, get the embedding
        if not query.needs_clarification:
            # 2. Generate Embedding (using asyncio.to_thread for safety)
            embedding_result = await asyncio.to_thread(_sync_embed, text)
            query.embedding = embedding_result['embedding']
            
        return query

    except Exception as e:
        import traceback
        print("ERROR IN PROMPT INTERPRETER:", e)
        traceback.print_exc()
        
        # General fallback error path
        return StructuredQuery(
            intent_summary=f"Failed to process prompt",
            needs_clarification=True,
            suggested_question=f"I encountered an error processing your request: {str(e)}. Please try again."
        )
