import logging
import json
from typing import List, Dict, Optional
from src.utilities.gemini_service import GeminiAIService

class MenuRecommendationService:
    def __init__(self):
        self.gemini_service = GeminiAIService()
        logging.info("Menu Recommendation Service initialized with Gemini AI")
    
    async def get_menu_recommendations(
        self, 
        menu_text: str,
        user_top_wines: List[Dict],
    ) -> Dict:
        """
        Use LLM to match menu wines with user preferences
        
        Args:
            menu_text: Raw OCR text from menu
            user_top_wines: List of user's top recommended wines
            
        Returns:
            Dict with 'summary' and 'recommendations' keys
        """
        try:
            # Format user's top wines for the prompt
            top_wines_text = "\n".join([
                f"- {wine.get('name', 'Unknown')} ({wine.get('type', 'Unknown type')}) - "
                f"Body: {wine.get('body', 'N/A')}, "
                f"Region: {wine.get('region', 'N/A')}, "
                f"ABV: {wine.get('abv', 'N/A')}%"
                for wine in user_top_wines
            ])
            
            prompt = f"""
You are a wine sommelier assistant. A user is at a restaurant and wants wine recommendations based on their preferences.

**User's Top Recommended Wines (based on their taste profile):**
{top_wines_text}

**Restaurant Menu (OCR extracted text):**
{menu_text}

Based on the user's wine preferences (reflected in their top recommended wines) and the restaurant's wine menu, provide:

1. A brief summary (2-3 sentences) about what the top three, and only the top three wines from the menu would suit the user best
2. Top 3-5 wine recommendations from the menu that match the user's taste profile

Return your response in the following JSON format:
{{
    "summary": "Brief summary explaining the recommendations and why they match the user's preferences...",
    "recommendations": [
        {{
            "wine_name": "Exact name of wine from menu",
            "reason": "Why this matches user's preferences (reference similar characteristics from their top picks)",
            "wine_type": "Type: tinto/blanco/rosado/espumoso"
        }}
    ]
}}

Important guidelines:
- Be humble and concise, avoiding overly complex language and telling the user "I know exactly what you like"
- Avoid making assumptions about the user's preferences beyond what is provided in their top wine picks
- The top picks are not necessarily the user preferences: Always talk about "based on our general recommendations" instead of preferences
- Focus on matching wine characteristics like type, body, region, and style
- Be specific about why each wine matches
- Only recommend wines that are actually on the menu
- Limit to 3 recommendations maximum
- Write in Rioplatense Spanish for better user experience
"""
            
            logging.info("Sending request to Gemini AI for menu recommendations")
            response_text = await self.gemini_service.get_response(prompt)
            
            # Parse JSON from response
            response_text = response_text.strip()
            logging.debug(f"Raw LLM response: {response_text[:200]}...")
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif response_text.startswith("```"):
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Validate response structure
            if "summary" not in result or "recommendations" not in result:
                raise ValueError("LLM response missing required fields")
            
            logging.info(f"Successfully generated {len(result.get('recommendations', []))} recommendations")
            return result
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse LLM response as JSON: {str(e)}")
            logging.error(f"Response text: {response_text[:500]}...")
            # Fallback response
            return {
                "summary": "No se pudieron generar recomendaciones en este momento. Por favor, intenta de nuevo.",
                "recommendations": []
            }
        except Exception as e:
            logging.error(f"Menu recommendation generation failed: {str(e)}")
            raise Exception(f"Failed to generate recommendations: {str(e)}")