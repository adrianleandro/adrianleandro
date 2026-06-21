from typing import Any

from src.utilities.supabase_client import supabase
from src.models.schemas.wine import WineSchema, WineFilters
import uuid
import logging

class WinesRepository:
    table_name = "wines"

    @staticmethod
    def get_by_id(wine_id: int):
        response = supabase.table(WinesRepository.table_name).select("*").eq("wine_id", wine_id).maybe_single().execute()
        if not getattr(response, "data", None):
            raise KeyError('Wine not found')
        return WineSchema(**response.data)

    @staticmethod
    def get_by_filters(filters: WineFilters, limit: int = None, offset: int = None) -> tuple[list[WineSchema], int] | list[WineSchema]:
        # Build base query for filtering (removed count='exact' for performance)
        query = supabase.table(WinesRepository.table_name).select("*")

        text_filters = {
            'wine_name': filters.wine_name,
            'type': filters.wine_type,
            'winery': filters.winery,
            'country': filters.country,
            'region': filters.region
        }

        for field, value in text_filters.items():
            if value:
                query = query.ilike(field, f"%{value}%")

        if filters.min_abv is not None:
            query = query.gte("abv", filters.min_abv)
        if filters.max_abv is not None:
            query = query.lte("abv", filters.max_abv)

        # Add ordering - prioritize exact matches first, then alphabetical
        query = query.order("wine_name", desc=False)

        # Apply pagination if limit and offset are provided
        # Query one extra row to determine if there are more results
        if limit is not None and offset is not None:
            query = query.range(offset, offset + limit)  # Request limit + 1 rows

        response = query.execute()

        if not getattr(response, "data", None):
            # Return empty results with has_more flag
            return ([], 0) if limit is not None else []

        wines = [WineSchema(**item) for item in response.data]

        # If pagination is used, return tuple with approximate count
        if limit is not None:
            # Check if we got more results than requested (means there's a next page)
            has_more = len(wines) > limit

            # Remove the extra row if we got it
            if has_more:
                wines = wines[:limit]

            # Estimate total: we know there are at least offset + len(wines) rows
            # If has_more is True, add at least 'limit' more to the estimate
            estimated_total = offset + len(wines) + (limit if has_more else 0)

            return wines, estimated_total

        # Legacy behavior: sort in memory if no pagination and wine_name filter exists
        if filters.wine_name:
            search_term = filters.wine_name.lower()
            wines.sort(key=lambda w: (
                not w.wine_name.lower().startswith(search_term),
                w.wine_name.lower()
            ))

        return wines

    @staticmethod
    def create(wine: WineSchema):
        wine_dict = wine.dict()
        # Genera el UUID si no está presente o es None
        wine_dict["id"] = str(uuid.uuid4())
        response = supabase.table(WinesRepository.table_name).insert(wine_dict).execute()
        if not getattr(response, "data", None):
            return None
        return WineSchema(**response.data[0])

    @staticmethod
    def update_by_id(wine_id: int, wine_data: dict):
        # Si el campo 'id' es UUID, conviértelo a string
        if "id" in wine_data and isinstance(wine_data["id"], uuid.UUID):
            wine_data["id"] = str(wine_data["id"])
        response = supabase.table(WinesRepository.table_name).update(wine_data).eq("wine_id", wine_id).execute()
        if not getattr(response, "data", None):
            return None
        return WineSchema(**response.data[0])

    @staticmethod
    def delete_by_id(wine_id: int):
        response = supabase.table(WinesRepository.table_name).delete().eq("wine_id", wine_id).execute()
        return bool(getattr(response, "data", None))

    @staticmethod
    def put_summary(wine_id: int, summary: str):
        try:
            response = supabase.table(WinesRepository.table_name).update({"summary": summary}).eq("wine_id", wine_id).execute()
            if response.data:
                logging.info(f"Resumen del vino {wine_id} actualizado exitosamente.")
                return True
            else:
                logging.warning(f"No se encontró el vino {wine_id} para actualizar (0 filas afectadas).")
                return False
        except Exception as e:
            logging.error(f"Error inesperado al llamar a Supabase: {e}", exc_info=True)
            return False