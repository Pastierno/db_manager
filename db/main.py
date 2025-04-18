from connection import Database

def main():
    db_name = "prodottiDB"
    # Connessione al database
    db = Database(host="localhost", user="root", password="", database=db_name)
    db.create_db()
    with db:
        db.execute("""CREATE TABLE IF NOT EXISTS supermercati(
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            città VARCHAR(255) NOT NULL
        )""")
    
        db.execute("""CREATE TABLE IF NOT EXISTS prodotti(
            id INT AUTO_INCREMENT PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            prezzo DECIMAL(10, 2) NOT NULL,
            offerta BOOLEAN DEFAULT FALSE,
            id_supermercato INT,
            FOREIGN KEY (id_supermercato) REFERENCES supermercati(id) ON DELETE CASCADE
        )""")
    while True:
        print("Benvenuto nel gestore dei supermercati e prodotti!")
        print("Scegli un'operazione:")
        print("1. Aggiungi un supermercato")
        print("2. Aggiungi un prodotto")
        print("3. Dove fare la spesa?")
        print("4. Esci")
        scelta = int(input("Inserisci il numero dell'operazione: "))
        
        if scelta == 1:
            nome = input("Inserisci il nome del supermercato: ")
            città = input("Inserisci la città del supermercato: ")
            db.execute("INSERT INTO supermercati (nome, città) VALUES (%s, %s)", (nome, città))
            print(f"Supermercato '{nome}' aggiunto con successo.")
            
        elif scelta == 2:
            nome = input("Inserisci il nome del prodotto: ")
            prezzo = float(input("Inserisci il prezzo del prodotto: "))
            offerta = input("Il prodotto è in offerta? (s/n): ").lower() == 's'
            id_supermercato = int(input("Inserisci l'ID del supermercato: "))
            db.execute("INSERT INTO prodotti (nome, prezzo, offerta, id_supermercato) VALUES (%s, %s, %s, %s)", (nome, prezzo, offerta, id_supermercato))
            print(f"Prodotto '{nome}' aggiunto con successo.")
            
        elif scelta == 3:
            lista_spesa = input("Inserisci la lista della spesa (separata da virgole): ").split(",")
            lista_spesa = [prodotto.strip() for prodotto in lista_spesa if prodotto.strip()]
            
            if not lista_spesa:
                print("Lista della spesa vuota. Tornando al menu principale.")
                continue
            
            # Trova il miglior supermercato (con più prodotti al prezzo minimo)
            placeholders = ', '.join(['%s'] * len(lista_spesa))
            query = f"""
            SELECT 
                s.id AS id_supermercato,
                s.nome AS nome_supermercato,
                s.città AS città_supermercato,
                COUNT(*) AS num_prodotti_prezzo_minimo
            FROM 
                supermercati s
            JOIN 
                prodotti p ON s.id = p.id_supermercato
            JOIN (
                SELECT 
                    nome,
                    MIN(prezzo) AS prezzo_minimo
                FROM 
                    prodotti
                WHERE 
                    nome IN ({placeholders})
                GROUP BY 
                    nome
            ) pm ON p.nome = pm.nome AND p.prezzo = pm.prezzo_minimo
            WHERE 
                p.nome IN ({placeholders})
            GROUP BY 
                s.id, s.nome, s.città
            ORDER BY 
                num_prodotti_prezzo_minimo DESC, s.nome
            LIMIT 1
            """
            
            params = lista_spesa + lista_spesa
            risultati = db.fetchall(query, params)
            
            if not risultati:
                print("Nessun supermercato trovato con i prodotti richiesti.")
                continue
            
            miglior_supermercato = risultati[0]
            
            # Ottieni i dettagli dei prodotti nel miglior supermercato
            query_prodotti = f"""
            SELECT 
                p.nome,
                p.prezzo,
                p.offerta,
                CASE WHEN p.prezzo = pm.prezzo_minimo THEN 1 ELSE 0 END AS is_prezzo_minimo
            FROM 
                prodotti p
            JOIN (
                SELECT 
                    nome,
                    MIN(prezzo) AS prezzo_minimo
                FROM 
                    prodotti
                WHERE 
                    nome IN ({placeholders})
                GROUP BY 
                    nome
            ) pm ON p.nome = pm.nome
            WHERE 
                p.id_supermercato = %s AND p.nome IN ({placeholders})
            ORDER BY 
                p.nome
            """
            
            params_prodotti = lista_spesa + [miglior_supermercato['id_supermercato']] + lista_spesa
            dettagli_prodotti = db.fetchall(query_prodotti, params_prodotti)
            
            # Visualizza i risultati
            print(f"\nMiglior supermercato: {miglior_supermercato['nome_supermercato']} ({miglior_supermercato['città_supermercato']})")
            print(f"Prodotti al prezzo minimo: {miglior_supermercato['num_prodotti_prezzo_minimo']}")
            
            print("\nDettagli prodotti:")
            for prodotto in dettagli_prodotti:
                status = "IN OFFERTA!" if prodotto['offerta'] else ""
                prezzo_minimo = " (prezzo minimo)" if prodotto['is_prezzo_minimo'] else ""
                print(f"  - {prodotto['nome']}: €{prodotto['prezzo']:.2f} {status}{prezzo_minimo}")
            
            # Mostra prodotti non disponibili
            prodotti_trovati = {p['nome'] for p in dettagli_prodotti}
            prodotti_mancanti = set(lista_spesa) - prodotti_trovati
            
            if prodotti_mancanti:
                print("\nProdotti non disponibili in questo supermercato:")
                for p in prodotti_mancanti:
                    print(f"  - {p}")
        
        elif scelta == 4:
            print("Arrivederci!")
            break

if __name__ == "__main__":
    main()
