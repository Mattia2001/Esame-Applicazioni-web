# interroga il database richiedendo i dati sulle donazioni eseguite dagli utenti

import sqlite3
import datetime

# aggiungi donazione al database
def add_donazione(donazione):

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    x = datetime.datetime.now()

    sql = 'INSERT INTO donazioni(importo,id_donatore,raccolta,testo_donazione,data_donazione,nome_donatore,cognome_donatore) VALUES(?,?,?,?,?,?,?)'
    cursor.execute(sql, (
                        donazione['importo'],
                        donazione['id_donatore'],
                        donazione['id_raccolta'],
                        donazione['testo_donazione'],
                        donazione['data_donazione'],
                        donazione['nome_donatore'],
                        donazione['cognome_donatore']))
    
    # Aggiorna cifra_attuale nella tabella raccolta
    sql_update_cifra_attuale = 'UPDATE raccolte SET cifra_attuale = cifra_attuale + ? WHERE id_raccolta = ?'
    cursor.execute(sql_update_cifra_attuale, (donazione['importo'], donazione['id_raccolta']))

    try:
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

def get_donazione_by_id(id):

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    '''ricevi l'id della raccolta, seleziona tutte le donazioni effettuate a quella raccolta, ovvero
    dove raccolta (donazioni) = id_raccolta (raccolte)'''

    sql = 'SELECT donazioni.id_donazione,donazioni.importo,donazioni.id_donatore,donazioni.raccolta,donazioni.testo_donazione,donazioni.data_donazione,donazioni.nome_donatore,donazioni.cognome_donatore FROM donazioni WHERE donazioni.raccolta = ? ORDER BY data_donazione DESC'
    cursor.execute(sql, (id,))
    donazioni = cursor.fetchall()

    cursor.close()
    conn.close()

    return donazioni