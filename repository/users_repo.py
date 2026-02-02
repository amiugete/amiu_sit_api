

def check_user_db(username: str) -> bool:
    """Query per il controllo dell'esistenza di un utente nel sistema"""
    return """SELECT id_user, name FROM util_ns.sys_users u where u.name = :name"""