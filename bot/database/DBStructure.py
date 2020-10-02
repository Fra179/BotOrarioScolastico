from pony.orm import Database, db_session, Required, commit, select, PrimaryKey, Set, delete

db = Database("sqlite", "vps.db", create_db=True)


class User(db.Entity):
    chat_id = PrimaryKey(int)
    name = Required(str)
    username = Required(str, default="---")
    stopped = Required(bool, default=False)
    stop_gm = Required(bool, default=False)
    was_notified = Required(bool, default=False)

    # only for admins
    is_admin = Required(bool, default=False)
    tokens = Set('Token')
    broadcast_text = Required(str, default="None")


class Token(db.Entity):
    user = Required(User)
    token = Required(str)
    single_use = Required(bool, default=True)


db.generate_mapping(create_tables=True)
