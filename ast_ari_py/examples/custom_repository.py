import sqlite3
from ast_ari_py.resources.user import User, UserRole

class SQLiteUserRepository:
    """
    Contoh implementasi Repository User yang terhubung ke Database SQLite.
    Menggantikan UserManager in-memory bawaan library.
    """
    def __init__(self, db_path="users.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                name TEXT,
                extension TEXT,
                endpoint_tech TEXT,
                endpoint_resource TEXT,
                role TEXT
            )
        ''')
        self.conn.commit()

    def add_user(self, id, name, extension, endpoint_tech, endpoint_resource, role=UserRole.AGENT):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO users (id, name, extension, endpoint_tech, endpoint_resource, role)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (id, name, extension, endpoint_tech, endpoint_resource, role))
        self.conn.commit()
        print(f"User {name} saved to DB.")

    def get_user_by_extension(self, extension):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE extension = ?', (extension,))
        row = cursor.fetchone()
        if row:
            return self._row_to_user(row)
        return None

    def _row_to_user(self, row):
        # Mapping baris DB ke objek User library
        return User(
            id=row[0],
            name=row[1],
            extension=row[2],
            endpoint_tech=row[3],
            endpoint_resource=row[4],
            role=row[5]
        )

# Contoh Penggunaan
if __name__ == "__main__":
    repo = SQLiteUserRepository()
    
    # Tambah User
    repo.add_user("1", "John DB", "5001", "PJSIP", "5001", "agent")
    
    # Ambil User
    user = repo.get_user_by_extension("5001")
    print(f"Retrieved from DB: {user}")
