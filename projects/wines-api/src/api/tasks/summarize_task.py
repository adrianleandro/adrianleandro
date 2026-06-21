from fastapi import BackgroundTasks, Depends
from src.utilities.gemini_service import GeminiAIService
from src.repository.wines_repository import WinesRepository
import logging

class SummarizeTask:
    MIN_REVIEWS_TO_SUMMARIZE = 3
    def __init__(self, background_tasks: BackgroundTasks):
        self.background_tasks = background_tasks
        logging.info('SummarizeTask ready')

    async def _run_actual_task(self, wine_id: int, ratings: list):
        reviews = [r.review for r in ratings if r.review and r.review.strip()]
        logging.info(f'Found {len(reviews)} reviews for wine with id {wine_id}. Minimum reviews should be {self.MIN_REVIEWS_TO_SUMMARIZE}')

        if len(reviews) < self.MIN_REVIEWS_TO_SUMMARIZE:
            logging.info(f'Not enough reviews for wine with id {wine_id}. Stopping task.')
            return

        logging.info(f'Starting to summarize wine with id {wine_id}')

        prompt = f"""
        Eres un sommelier experto y un excelente escritor.
        Tu tarea es analizar la siguiente lista de reseñas de usuarios para un vino específico 
        y generar un resumen conciso y atractivo de 4 o 5 frases, con lenguaje ideal
        para ser entendido por todos los públicos consumidores de vinos, de principiantes a expertos.

        El resumen debe capturar el sentimiento general, los sabores y aromas 
        más mencionados, y la impresión general del vino.
        
        **Instrucciones Importantes:**
        - Tu respuesta debe ser *únicamente* el párrafo del resumen.
        - NO incluyas frases introductorias, saludos o preámbulos (ej: "Aquí tienes el resumen:", "Claro:", "Este vino es...", etc.).
        - Comienza la respuesta directamente con el texto del resumen.

        Reseñas de los usuarios:
        {reviews}
        """
        try:
            gemini_service = GeminiAIService()
        except Exception as e:
            logging.error('Task could not be completed, error when initializing AI service.')
            return

        summary = await gemini_service.get_response(prompt)
        wines_repo = WinesRepository()
        logging.info(f'New wine summary for id {wine_id} ready: {summary}')
        if wines_repo.put_summary(wine_id, summary):
            logging.info(f'Summary saved for wine with id {wine_id}')
        else:
            logging.error(f'Error saving summary for wine with id {wine_id}')

    def schedule_summary(self, wine_id: int, ratings: list):
        self.background_tasks.add_task(
            self._run_actual_task,
            wine_id,
            ratings
        )