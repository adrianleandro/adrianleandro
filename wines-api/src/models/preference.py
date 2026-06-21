from src.models.preference_category import PreferenceCategory

class Preference:
    id: int
    category: PreferenceCategory | None
    option: str
    description: str

    def __init__(self, id: int, option: str, description: str, value: float):
        self.id = id
        self.option = option
        self.description = description
        self.value = value

    def set_category(self, category):
        self.category = category

    def get_option_and_description(self):
        if self.description is None:
            return self.option
        return f"{self.option} - {self.description}"

    def has_category(self, category):
        if self.category is None:
            return False
        return category == self.category.name  # Cambiado de .category a .name

    def get_preferences(self, user_id):
        """Obtiene las preferencias del usuario"""
        try:
            # Código existente para obtener preferencias...
            
            # Si no hay preferencias, devolver lista vacía en lugar de error
            if not user_preferences_data:  # O como sea que verifiques si hay datos
                return []
                
            # Resto del código...
        except Exception as e:
            print(f"Error al obtener preferencias: {str(e)}")
            # Devolver lista vacía en caso de error
            return []