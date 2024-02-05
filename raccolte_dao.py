# interroga il database richiedendo i dati sulle varie raccolte

import sqlite3

# estrai tutte le raccolte, indipendentemente dal fatto che siano ancora valide o no
def get_raccolte():
    conn = sqlite3.connect('db/raccolte_fondi.db')

    # specify that returned data have to stored into a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    '''The query must select all the data necessary to display the posts together with the
    data of the respective profiles. Thus we need a JOIN operation where posts.id_utente = utenti.id.
    Posts are then ordered depending on publication date in ascending order'''

    sql = 'SELECT raccolte.id_raccolta, raccolte.nome_raccolta, raccolte.descrizione, raccolte.immagine, raccolte.data_creazione, raccolte.data_termine, raccolte.cifra_attuale, raccolte.cifra_da_raggiungere, raccolte.tipo_raccolta, raccolte.organizzatore_raccolta, raccolte.importo_minimo, utenti.nome, utenti.cognome FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente ORDER BY data_creazione DESC'
    cursor.execute(sql)
    raccolte = cursor.fetchall()

    cursor.close()
    conn.close()

    return raccolte

# aggiungi raccolta al database
def add_raccolta(raccolta):
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    if 'immagine_post' in raccolta:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,immagine,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo) VALUES(?,?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, (raccolta['titolo_raccolta'],
                             raccolta['descrizione'], 
                             raccolta['immagine_raccolta'],
                             raccolta['data_creazione'],
                             raccolta['data_termine'],
                             raccolta['cifra_attuale'],
                             raccolta['cifra_da_raggiungere'],
                             raccolta['tipo_raccolta'],
                             raccolta['organizzatore_raccolta'],
                             raccolta['importo_minimo']
                             ))
    else:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo) VALUES(?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, (raccolta['titolo_raccolta'],
                             raccolta['descrizione'], 
                             raccolta['data_creazione'],
                             raccolta['data_termine'],
                             raccolta['cifra_attuale'],
                             raccolta['cifra_da_raggiungere'],
                             raccolta['tipo_raccolta'],
                             raccolta['organizzatore_raccolta'],
                             raccolta['importo_minimo']
                             ))
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