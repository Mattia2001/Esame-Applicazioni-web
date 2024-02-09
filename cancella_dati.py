import sqlite3

'''Programma che, se eseguito, cancella tutti i dati nel database'''

# Connettiti al tuo database SQLite
conn = sqlite3.connect('db/raccolte_fondi.db')
cursor = conn.cursor()

# Lista delle tue tabelle da svuotare
tabelle = ['raccolte', 'utenti', 'donazioni'] # Aggiungi o rimuovi nomi di tabelle a seconda del tuo schema

# Esegue la cancellazione dei dati per ogni tabella
for tabella in tabelle:
    cursor.execute(f'DELETE FROM {tabella};')
    # Resetta gli autoincrement se necessario
    cursor.execute(f"DELETE FROM sqlite_sequence WHERE name = '{tabella}';")

# Salva le modifiche
conn.commit()

# Chiudi la connessione
conn.close()

print("Dati eliminati con successo.")