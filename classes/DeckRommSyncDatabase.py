import sqlite3
from typing import List, Tuple, Any

class DeckRommSyncDatabase:
    def __init__(self, db_name: str):
        """
        Initialisiert die Verbindung zur SQLite-Datenbank.
        """
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def execute_query(self, query: str, params: Tuple = ()) -> None:
        """
        Führt eine SQL-Abfrage ohne Rückgabewert aus (INSERT, UPDATE, DELETE).
        """
        try:
            self.cursor.execute(query, params)
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"SQLite Fehler: (0) {e}")
    
    def insert(self, table: str, columns: List[str], values: Tuple) -> None:
        """
        Führt einen INSERT in die Datenbank aus.
        """
        cols = ', '.join(columns)
        placeholders = ', '.join(['?' for _ in columns])
        query = f"INSERT INTO {table} ({cols}) VALUES ({placeholders})"
        # print(query)
        self.execute_query(query, values)
    
    def update(self, table: str, updates: dict, condition: str, condition_values: Tuple) -> None:
        """
        Führt ein UPDATE in der Datenbank aus.
        """
        set_clause = ', '.join([f"{key} = ?" for key in updates.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {condition}"
        values = tuple(updates.values()) + condition_values
        self.execute_query(query, values)
    
    def fetch_query(self, query: str, params: Tuple = ()) -> List[Tuple]:
        """
        Führt eine SELECT-Abfrage aus und gibt die Ergebnisse zurück.
        """
        try:
            self.cursor.execute(query, params)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"SQLite Fehler: (1) {e}")
            return []
        
    def select(self, table: str, columns: List[str] = ['*'], condition: str = '', condition_values: Tuple = ()) -> List[Tuple]:
        """
        Führt ein SELECT in der Datenbank aus und gibt die Ergebnisse zurück.
        """
        cols = ', '.join(columns)
        query = f"SELECT {cols} FROM {table}"
        if condition:
            query += f" WHERE {condition}"
        return self.fetch_query(query, condition_values)
    
    def select_as_dict(self, table: str, columns: List[str] = ['*'], condition: str = '', condition_values: Tuple = ()) -> List[dict]:
        """
        Führt ein SELECT in der Datenbank aus und gibt die Ergebnisse als Liste von Dictionaries zurück.
        """
        cols = ', '.join(columns)
        query = f"SELECT {cols} FROM {table}"
        if condition:
            query += f" WHERE {condition}"

        try:
            self.cursor.execute(query, condition_values)
            rows = self.cursor.fetchall()
            column_names = [desc[0] for desc in self.cursor.description]  # Holt die Spaltennamen
            return [dict(zip(column_names, row)) for row in rows]  # Erstellt Dicts
        except sqlite3.Error as e:
            print(f"SQLite Fehler: (2) {e}")
            return []