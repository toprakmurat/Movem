from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.first_name = user_data.get('first_name')
        self.last_name = user_data.get('last_name')
        self.bio = user_data.get('bio')
        self.password_hash = user_data.get('password_hash')
        self.role = user_data.get('role')
        self.avatar = user_data.get('profile_picture')
        self.game_score = user_data.get('game_score', 0)

    def get_id(self):
        return str(self.id)