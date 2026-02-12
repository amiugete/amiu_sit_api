

def check_user_db(username: str) -> str:
    """Query per il controllo dell'esistenza di un utente nel sistema"""
    return """SELECT u.id_user, u.name, u.email, sr.name AS role_name
    FROM util_ns.sys_users u 
    JOIN util_ns.sys_roles sr on sr.id_role= u.id_role
    WHERE u.name ILIKE :name
    """

def get_lista_permessi_endpoint() -> str:
    """Query per il recupero dei permessi associati ai ruoli per endpoint"""
    return """
    select unnest(string_to_array(permessi, ',')) AS permesso
    FROM util_ns.sys_ws
    WHERE endpoint  = :endpoint
    """

def get_user_roles() -> str:
    """Query per il recupero dei ruoli associati a un utente"""
    return """
           select * from util_ns.sys_users_ws  where id_user = :id_user
        """