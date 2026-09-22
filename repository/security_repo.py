# Query per la tabella log_auth.security_logs (PostgreSQL)

# Restituisce la query per recuperare il record di un IP
pst_security_log_by_ip: str = "SELECT * FROM log_auth.security_logs WHERE ip_address = :ip_address"

# Restituisce la query per inserire un nuovo record per un IP
pst_insert_security_log: str = (
    """
        INSERT INTO log_auth.security_logs (ip_address, attempts, ban_count, last_failure, blocked_until, last_access, count_access)
        VALUES (:ip_address, 0, 0, NULL, NULL, NULL, 0)
        """
)

# Mette attempts a 0 e blocca l'IP per 30 minuti. Imposta ban_count a 1
pst_update_attempts0_block_30min: str = (
    """
        UPDATE log_auth.security_logs 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = NOW() AT TIME ZONE 'Europe/Rome' + INTERVAL '30 minutes',
        ban_count = 1
        WHERE ip_address = :ip_address
        """
)

# Mette attempts a 0 e blocca l'IP per 24 ore. Imposta ban_count a 2
pst_update_attempts0_block_24h: str = (
    """
        UPDATE log_auth.security_logs 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = NOW() AT TIME ZONE 'Europe/Rome' + INTERVAL '24 hours',
        ban_count = 2
        WHERE ip_address = :ip_address
        """
)

# Mette attempts a 0 e blocca l'IP in modo permanente. Imposta ban_count a 3
pst_update_attempts0_block_permanent: str = (
    """
        UPDATE log_auth.security_logs 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = '9999-12-31 23:59:59'::TIMESTAMP,
        ban_count = 3
        WHERE ip_address = :ip_address
        """
)

# Mette solo attempts a un valore specificato per un IP
pst_update_attempts_only: str = (
    "UPDATE log_auth.security_logs SET attempts = :attempts "
    "WHERE ip_address = :ip_address"
)

# Mette attempts e ban_count a 0 e sblocca l'IP dopo login riuscito
pst_reset_attempts_and_ban_count: str = (
    "UPDATE log_auth.security_logs SET attempts = 0, ban_count = 0, blocked_until = NULL "
    "WHERE ip_address = :ip_address"
)

# Aggiorna last_access e incrementa count_access dopo login riuscito
pst_update_access_log: str = (
    """
        UPDATE log_auth.security_logs
        SET last_access = NOW() AT TIME ZONE 'Europe/Rome', count_access = count_access + 1
        WHERE ip_address = :ip_address
        """
)


# Query per la tabella log_auth.security_logs_user (PostgreSQL)

# Restituisce la query per recuperare il record di un user
pst_security_log_by_user: str = 'SELECT * FROM log_auth.security_logs_user WHERE "user" = :user'

# Restituisce la query per inserire un nuovo record per un user
pst_insert_security_log_user: str = (
    """
        INSERT INTO log_auth.security_logs_user ("user", attempts, ban_count, last_failure, blocked_until, last_access, count_access)
        VALUES (:user, 0, 0, NULL, NULL, NULL, 0)
        """
)

# Mette attempts a 0 e blocca l'user per 30 minuti. Imposta ban_count a 1
pst_update_attempts0_block_30min_user: str = (
    """
        UPDATE log_auth.security_logs_user 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = NOW() AT TIME ZONE 'Europe/Rome' + INTERVAL '30 minutes',
        ban_count = 1
        WHERE "user" = :user
        """
)

# Mette attempts a 0 e blocca l'user per 24 ore. Imposta ban_count a 2
pst_update_attempts0_block_24h_user: str = (
    """
        UPDATE log_auth.security_logs_user 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = NOW() AT TIME ZONE 'Europe/Rome' + INTERVAL '24 hours',
        ban_count = 2
        WHERE "user" = :user
        """
)

# Mette attempts a 0 e blocca l'user in modo permanente. Imposta ban_count a 3
pst_update_attempts0_block_permanent_user: str = (
    """
        UPDATE log_auth.security_logs_user 
        SET 
        attempts = 0, 
        last_failure = NOW() AT TIME ZONE 'Europe/Rome',
        blocked_until = '9999-12-31 23:59:59'::TIMESTAMP,
        ban_count = 3
        WHERE "user" = :user
        """
)

# Mette solo attempts a un valore specificato per un user
pst_update_attempts_only_user: str = (
    'UPDATE log_auth.security_logs_user SET attempts = :attempts '
    'WHERE "user" = :user'
)

# Mette attempts e ban_count a 0 e sblocca l'user dopo login riuscito
pst_reset_attempts_and_ban_count_user: str = (
    'UPDATE log_auth.security_logs_user SET attempts = 0, ban_count = 0, blocked_until = NULL '
    'WHERE "user" = :user'
)

# Aggiorna last_access e incrementa count_access dopo login riuscito per user
pst_update_access_log_user: str = (
    """
        UPDATE log_auth.security_logs_user
        SET last_access = NOW() AT TIME ZONE 'Europe/Rome', count_access = count_access + 1
        WHERE "user" = :user
        """
)
