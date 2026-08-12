import os
import json
import base64
from typing import Optional, Dict, Any, Tuple
import google.generativeai as genai
from schemas import StructuredQuery
from playwright.async_api import async_playwright

SYSTEM_PROMPT = """You are an expert HTML5 Canvas Game Developer. Your task is to generate a fully contained, single-file HTML game based on the user's prompt.
The game must:
- Be entirely contained in a single HTML string (HTML, CSS in <style>, JS in <script>).
- Use no external assets (no images or sounds, unless base64 encoded or drawn via canvas).
- Handle user input (keyboard or mouse).
- Be a playable, simple 2D game loop (e.g. requestAnimationFrame).
- DO NOT wrap the output in markdown code blocks like ```html. Output raw HTML only!
"""

def check_feasibility(query: StructuredQuery) -> Tuple[bool, str]:
    """Check if the requested game is feasible for LLM generation."""
    unfeasible_genres = ["mmo", "rpg", "3d", "multiplayer", "fps", "vr"]
    prompt_lower = query.intent_summary.lower()
    
    if query.multiplayer_support:
        return False, "Complex multiplayer games are out of scope for simple generation."
        
    for genre in query.genres:
        if genre.lower() in unfeasible_genres:
            return False, f"The genre '{genre}' is too complex for generation."
            
    for mechanic in query.mechanics:
        if "3d" in mechanic.lower():
            return False, "3D mechanics are out of scope."
            
    return True, "Feasible"

async def generate_game_code(prompt: str) -> str:
    """Generate the HTML5 game using Gemini."""
    model = genai.GenerativeModel(
        model_name="gemini-flash-lite-latest",
        system_instruction=SYSTEM_PROMPT
    )
    
    print(f"Generating game for prompt: {prompt}")
    response = await model.generate_content_async(
        f"Generate a single-file HTML5 canvas game matching this description: {prompt}. OUTPUT ONLY RAW HTML, starting with <!DOCTYPE html>."
    )
    print("Game generation model response received!")
    
    code = response.text.strip()
    # Strip markdown if model mistakenly added it
    if code.startswith("```html"):
        code = code[7:]
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
        
    return code.strip()

async def validate_game(html_content: str) -> Tuple[bool, Optional[str]]:
    """Run the HTML in headless chromium and check for JS errors."""
    try:
        # Check basic structure
        if "<canvas" not in html_content and "<html" not in html_content:
             return False, "Output does not look like HTML."
             
        # Encode HTML to data URI
        encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        data_uri = f"data:text/html;base64,{encoded_html}"
        
        errors = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Listen for JS errors
            page.on("pageerror", lambda exc: errors.append(str(exc)))
            page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)
            
            # Load the page and wait 1 second
            await page.goto(data_uri, wait_until="networkidle")
            await page.wait_for_timeout(1000)
            
            await browser.close()
            
        if errors:
            return False, "; ".join(errors)
            
        return True, None
        
    except Exception as e:
        return False, f"Validation framework error: {str(e)}"

async def generate_game_pipeline(prompt: str, query: StructuredQuery) -> Dict[str, Any]:
    """Orchestrates feasibility check, generation, and validation with 1 retry."""
    is_feasible, reason = check_feasibility(query)
    if not is_feasible:
        return {
            "playable": False,
            "html_content": None,
            "reason_if_not_playable": reason
        }
        
    # Attempt 1
    html_code = await generate_game_code(prompt)
    is_valid, validation_error = await validate_game(html_code)
    
    if is_valid:
        return {
            "playable": True,
            "html_content": html_code,
            "reason_if_not_playable": None
        }
        
    # Attempt 2 (Retry with error feedback)
    retry_prompt = f"{prompt}\n\nThe previous code had this JS error: {validation_error}\nPlease fix it."
    html_code_retry = await generate_game_code(retry_prompt)
    is_valid_retry, validation_error_retry = await validate_game(html_code_retry)
    
    if is_valid_retry:
        return {
            "playable": True,
            "html_content": html_code_retry,
            "reason_if_not_playable": None
        }
        
    return {
        "playable": False,
        "html_content": None,
        "reason_if_not_playable": f"Failed validation after retry. Errors: {validation_error_retry}"
    }
