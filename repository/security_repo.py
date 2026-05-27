# Query per la tabella log_auth.security_logs (PostgreSQL)

def get_security_log_by_ip():
    """Restituisce la query per recuperare il record di un IP."""
    return "SELECT * FROM log_auth.security_logs WHERE ip_address = :ip_address"

def insert_security_log():
    """Restituisce la query per inserire un nuovo record per un IP."""
    return (
        """
        INSERT INTO log_auth.security_logs (ip_address, attempts, ban_count, last_failure, blocked_until, last_access, count_access)
        VALUES (:ip_address, 0, 0, NULL, NULL, NULL, 0)
        """
    )

def update_attempts0_block_30min():
    """Mette attempts a 0 e blocca l'IP per 30 minuti. Imposta ban_count a 1."""
    return (
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

def update_attempts0_block_24h():
    """Mette attempts a 0 e blocca l'IP per 24 ore. Imposta ban_count a 2."""
    return (
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

def update_attempts0_block_permanent():
    """Mette attempts a 0 e blocca l'IP in modo permanente. Imposta ban_count a 3."""
    return (
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

def update_attempts_only():
    """Mette solo attempts a un valore specificato per un IP."""
    return (
        "UPDATE log_auth.security_logs SET attempts = :attempts "
        "WHERE ip_address = :ip_address"
    )

def reset_attempts_and_ban_count():
    """Mette attempts e ban_count a 0 e sblocca l'IP dopo login riuscito."""
    return (
        "UPDATE log_auth.security_logs SET attempts = 0, ban_count = 0, blocked_until = NULL "
        "WHERE ip_address = :ip_address"
    )

def update_access_log():
    """Aggiorna last_access e incrementa count_access dopo login riuscito."""
    return (
        """
        UPDATE log_auth.security_logs
        SET last_access = NOW() AT TIME ZONE 'Europe/Rome', count_access = count_access + 1
        WHERE ip_address = :ip_address
        """
    )


# Query per la tabella log_auth.security_logs_user (PostgreSQL)

def get_security_log_by_user():
    """Restituisce la query per recuperare il record di un user."""
    return 'SELECT * FROM log_auth.security_logs_user WHERE "user" = :user'

def insert_security_log_user():
    """Restituisce la query per inserire un nuovo record per un user."""
    return (
        """
        INSERT INTO log_auth.security_logs_user ("user", attempts, ban_count, last_failure, blocked_until, last_access, count_access)
        VALUES (:user, 0, 0, NULL, NULL, NULL, 0)
        """
    )

def update_attempts0_block_30min_user():
    """Mette attempts a 0 e blocca l'user per 30 minuti. Imposta ban_count a 1."""
    return (
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

def update_attempts0_block_24h_user():
    """Mette attempts a 0 e blocca l'user per 24 ore. Imposta ban_count a 2."""
    return (
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

def update_attempts0_block_permanent_user():
    """Mette attempts a 0 e blocca l'user in modo permanente. Imposta ban_count a 3."""
    return (
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

def update_attempts_only_user():
    """Mette solo attempts a un valore specificato per un user."""
    return (
        'UPDATE log_auth.security_logs_user SET attempts = :attempts '
        'WHERE "user" = :user'
    )

def reset_attempts_and_ban_count_user():
    """Mette attempts e ban_count a 0 e sblocca l'user dopo login riuscito."""
    return (
        'UPDATE log_auth.security_logs_user SET attempts = 0, ban_count = 0, blocked_until = NULL '
        'WHERE "user" = :user'
    )

def update_access_log_user():
    """Aggiorna last_access e incrementa count_access dopo login riuscito per user."""
    return (
        """
        UPDATE log_auth.security_logs_user
        SET last_access = NOW() AT TIME ZONE 'Europe/Rome', count_access = count_access + 1
        WHERE "user" = :user
        """
    )
