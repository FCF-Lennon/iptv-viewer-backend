"""
Script de migración única.
Descifra las contraseñas de xtream_credentials con la clave vieja (derivada de jwt_secret)
y las vuelve a cifrar con la nueva FERNET_KEY independiente.

Uso:
    python migrate_fernet_key.py <JWT_SECRET_ACTUAL> <NUEVA_FERNET_KEY>
"""
import sys
import base64
import sqlite3
from cryptography.fernet import Fernet

def old_cipher(jwt_secret: str) -> Fernet:
    """Replicar exactamente la lógica vieja de get_cipher()."""
    key = base64.urlsafe_b64encode(jwt_secret.encode().ljust(32)[:32])
    return Fernet(key)

def new_cipher(fernet_key: str) -> Fernet:
    return Fernet(fernet_key.encode())

def migrate(jwt_secret: str, new_fernet_key: str, db_path: str = "iptv.db"):
    old = old_cipher(jwt_secret)
    new = new_cipher(new_fernet_key)

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute("SELECT id, password_encrypted FROM xtream_credentials")
    rows = cur.fetchall()

    print(f"Migrando {len(rows)} credenciales...")

    for cred_id, encrypted in rows:
        try:
            plaintext = old.decrypt(encrypted.encode()).decode()
            re_encrypted = new.encrypt(plaintext.encode()).decode()
            cur.execute(
                "UPDATE xtream_credentials SET password_encrypted = ? WHERE id = ?",
                (re_encrypted, cred_id)
            )
            print(f"  OK ID {cred_id} migrado")
        except Exception as e:
            print(f"  ERROR ID {cred_id}: {e}")
            conn.rollback()
            conn.close()
            sys.exit(1)

    conn.commit()
    conn.close()
    print("Migracion completada.")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python migrate_fernet_key.py <JWT_SECRET> <NUEVA_FERNET_KEY>")
        sys.exit(1)

    migrate(sys.argv[1], sys.argv[2])
