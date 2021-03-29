from data import users, db_session


class Session:

    def __init__(self):
        db_session.global_init('db/db.db')
        self.session = db_session.create_session()

    def insert_new_user(self, user_id):
        user = users.User(id=user_id)
        self.session.add(user)
        self.session.commit()

    def get_user(self, user_id):
        user = self.session.query(users.User).filter(users.User.id == user_id).first()
        return user

    def commit(self):
        self.session.commit()

    def get_user_by_login(self, login):
        user = self.session.query(users.User).filter(users.User.login == login).first()
        return user

    def set_token(self, login, token, time):
        user = self.get_user_by_login(login)
        user.token = token
        user.time_token = time
        self.session.commit()

    def add_new_user(self, login, password):