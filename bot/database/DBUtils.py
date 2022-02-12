from bot.database.DBStructure import User, Token, db_session, delete, select


class DBUtils:
    def __init__(self):
        pass

    def is_admin(self, chat_id: int) -> bool:
        with db_session:
            return User.exists(chat_id=chat_id, is_admin=True)

    def is_user(self, chat_id: int) -> bool:
        with db_session:
            return User.exists(chat_id=chat_id)

    def is_valid_token(self, token: str):
        with db_session:
            t: Token = Token.get(token=token)
            if t:
                if t.single_use:
                    delete(t)
                return True
            return False

    def get_user_info(self, chat_id: int) -> tuple:
        with db_session:
            u = User.get(chat_id=chat_id)
            if not u:
                return "", ""
            return u.name, u.username

    def add_user(self, chat_id: int, name: str, username: str):
        with db_session:
            if not self.is_user(chat_id):
                if not username:
                    username = "---"
                User(chat_id=chat_id, name=name, username=username)

    def update_broadcast_message(self, chat_id: int, message: str):
        with db_session:
            u = User.get(chat_id=chat_id)
            u.broadcast_text = message

    def get_broadcast_message(self, chat_id: int):
        with db_session:
            return User.get(chat_id=chat_id).broadcast_text

    def list_users_chat_id(self, stopped=None, is_admin=None, was_notified=None):
        chat_ids = []
        with db_session:
            users = select(user for user in User)

            if stopped is not None:
                users = select(x for x in users if x.stopped == stopped)
            if is_admin is not None:
                users = select(x for x in users if x.is_admin == is_admin)
            if was_notified is not None:
                users = select(x for x in users if x.was_notifies == was_notified)

            for x in users:
                chat_ids.append(x.chat_id)

        return chat_ids

    def stop(self, chat_id: int):
        with db_session:
            u = User.get(chat_id=chat_id)
            u.stopped = True

    def start(self, chat_id: int):
        with db_session:
            u = User.get(chat_id=chat_id)
            u.stopped = False

    def is_stopped(self, chat_id: int):
        with db_session:
            u = User.get(chat_id=chat_id)
            return u.stopped

    def gm_status(self, chat_id: int):
        with db_session:
            u = User.get(chat_id=chat_id)
            return not u.stop_gm

    def set_gm(self, chat_id: int, status: bool):
        with db_session:
            u = User.get(chat_id=chat_id)
            u.stop_gm = not status
