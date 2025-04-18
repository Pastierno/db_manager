import mysql.connector as sq

class Database:
    def __init__(self, host: str, user: str, password: str, database: str):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.conn = None # connessione settata a None per evitare errori di connessione
        self.cursor = None # cursore settato a None per evitare errori di connessione
    
    
    def create_db(self):
        try:
            temp_conn = sq.connect(
                host = self.host,
                user = self.user,
                password = self.password,
                autocommit=True
            )
            temp_cursor = temp_conn.cursor()
            temp_cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            temp_cursor.close()
            temp_conn.close()
            print(f"Database {self.database} creato con successo.")
        except sq.Error as e:
            print(f"Errore nella creazione del database: {e}")
            raise    
    
    def connect(self):
        try:
            # Connettiti solo se non c'è una connessione o se la connessione è chiusa
            if self.conn is None or not self.conn.is_connected():
                self.conn = sq.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    autocommit=False
                )
                self.cursor = self.conn.cursor(dictionary=True)
                print("Connessione al database avvenuta con successo.")
        except sq.Error as e:
            print(f"Errore: {e}")
            raise
            
    def close(self):
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.conn and self.conn.is_connected():
            self.conn.close()
            self.conn = None
        print("Connessione chiusa.")
        
        
    def execute(self, query: str, params: tuple = None):
        try:
            self.connect()
            self.cursor.execute(query, params or ())
            self.conn.commit()    
            print("Query eseguita con successo.")
        except sq.Error as e:
            print(f"Errore nell'esecuzione della query: {e}")
            raise
        
            
    def fetchall(self, query: str, params: tuple = None) -> list: # -> list per indicare che la funzione restituisce una lista di risultati
        try:
            self.connect()
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            return results
            
        except sq.Error as e:
            print(f"Errore nel recupero dei dati: {e}")
            raise
    
    def __enter__(self):
        self.connect()
        return self # permette di usare il costrutto with per gestire la connessione in modo automatico
    
    def __exit__(self, exc_type, exc_value, traceback): # gestisce la chiusura della connessione in caso di errore
        if self.conn:
            if exc_type:
                self.conn.rollback() # rollback in caso di errore
            else:
                self.conn.commit()
        self.close()

