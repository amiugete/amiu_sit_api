

# Query per il controllo dell'esistenza di un utente nel sistema
pst_check_user_db: str = """
    SELECT id, username FROM config.users where username = :username;
    """

# Query per il recupero dei permessi associati ai ruoli per endpoint
pst_endpoint_permissions: str = """
        SELECT p.perm as permesso
        FROM config.ws_permessi ws
        inner join config.perm p on p.id = ws.id_perm  
        where endpoint = :endpoint;
    """

# Query per il recupero dei ruoli associati a un utente
pst_user_roles: str = """
            select up.id_user , u.username ,up.id_perm ,p.perm as permesso  from config.users_perm up
            inner join config.users u on u.id = up.id_user 
            inner join config.perm p  on p.id = up.id_perm
            where up.id_user = :id_user
        """