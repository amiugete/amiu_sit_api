# Query per la tabella security_logs

def get_security_log_by_ip():
    """Restituisce la query per recuperare il record di un IP."""
    return "SELECT * FROM security_logs WHERE ip_address = :ip_address"

def insert_security_log():
    """Restituisce la query per inserire un nuovo record per un IP."""
    return (
        "INSERT INTO security_logs (ip_address, attempts, ban_count, last_failure, blocked_until) "
        "VALUES (:ip_address, 0, 0, NULL, NULL)"
    )

def update_attempts0_block_30min():
    """Mette attempts a 0 e blocca l'IP per 30 minuti. Imposta ban_count a 1."""
    return (
        """
        UPDATE security_logs 
        SET 
        attempts = 0, 
        last_failure = datetime('now','localtime'),
        blocked_until = datetime('now','localtime', '+30 minutes'),
        ban_count = 1
        WHERE ip_address = :ip_address
        """
    )

def update_attempts0_block_24h():
    """Mette attempts a 0 e blocca l'IP per 24 ore. Imposta ban_count a 2."""
    return (
        """
        UPDATE security_logs 
        SET 
        attempts = 0, 
        last_failure = datetime('now','localtime'),
        blocked_until = datetime('now','localtime', '+24 hours'),
        ban_count = 2
        WHERE ip_address = :ip_address
        """
    )
def update_attempts0_block_permanent():
    """Mette attempts a 0 e blocca l'IP in modo permanente. Imposta ban_count a 3."""
    return (
        """
        UPDATE security_logs 
        SET 
        attempts = 0, 
        last_failure = datetime('now','localtime'),
        blocked_until = '9999-12-31 23:59:59',
        ban_count = 3
        WHERE ip_address = :ip_address
        """
    )

def update_attempts_only():
    """Mette solo attempts a un valore specificato per un IP."""
    return (
        "UPDATE security_logs SET attempts = :attempts "
        "WHERE ip_address = :ip_address"
    )

def reset_attempts_and_ban_count():
    """Mette attempts e ban_count a 0 e sblocca l'IP dopo login riuscito."""
    return (
        "UPDATE security_logs SET attempts = 0, ban_count = 0, blocked_until = NULL "
        "WHERE ip_address = :ip_address"
    )


