from db import DatabaseHandler

class UserController:
    def __init__(self, db_handler: DatabaseHandler):
        self.db = db_handler
        self.user_id: int | None = None  # Track authenticated user

    def signup(self, username: str, password: str) -> bool:
        """Returns True if signup successful"""
        if not username or not password:
            return False
            
        if self.db.user_exists(username):
            return False
            
        user_id = self.db.create_user(username, password)
        if user_id:
            self.user_id = user_id
            return True
        return False

    def login(self, username: str, password: str) -> bool:
        """Returns True if login successful"""
        if not username or not password:
            return False
            
        user_id = self.db.verify_user(username, password)
        if user_id:
            self.user_id = user_id
            return True
        return False

    def set_preferences(self, user_id: int, title: str, location: str) -> bool:
        """
        Set user's job preferences
        Returns True if successful, False otherwise
        """
        if not user_id or not title or not location:
            return False
            
        return self.db.update_preferences(user_id, title, location)

    def get_preferences(self, user_id: int) -> Dict[str, str | None]:
        """
        Get user's current preferences
        Returns dict with 'preferred_title' and 'preferred_location'
        """
        if not user_id:
            return {'preferred_title': None, 'preferred_location': None}
            
        return self.db.get_user_preferences(user_id)