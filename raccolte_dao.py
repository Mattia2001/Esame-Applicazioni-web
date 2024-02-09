# interroga il database richiedendo i dati sulle varie raccolte

import sqlite3
from datetime import date, datetime, timedelta

# estrai tutte le raccolte, indipendentemente dal fatto che siano ancora valide o no
def get_raccolte():
    conn = sqlite3.connect('db/raccolte_fondi.db')

    # specify that returned data have to stored into a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    '''The query must select all the data necessary to display the posts together with the
    data of the respective profiles. Thus we need a JOIN operation where posts.id_utente = utenti.id.
    Posts are then ordered depending on publication date in ascending order'''

    sql = 'SELECT raccolte.id_raccolta, raccolte.nome_raccolta, raccolte.descrizione, raccolte.immagine, raccolte.data_creazione, raccolte.data_termine, raccolte.cifra_attuale, raccolte.cifra_da_raggiungere, raccolte.tipo_raccolta, raccolte.organizzatore_raccolta, raccolte.importo_minimo, raccolte.status, utenti.nome, utenti.cognome FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente ORDER BY data_creazione DESC'
    cursor.execute(sql)
    raccolte = cursor.fetchall()

    cursor.close()
    conn.close()

    return raccolte


# estrai tutte le raccolte terminate, quindi con status = 'terminata'
def get_raccolte_terminate():

    conn = sqlite3.connect('db/raccolte_fondi.db')

    # specify that returned data have to stored into a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM raccolte WHERE raccolte.status = ? ORDER BY data_creazione DESC'
    cursor.execute(sql, ('terminata',))
    raccolte_terminate = cursor.fetchall()

    cursor.close()
    conn.close()

    return raccolte_terminate


# dato l'id della raccolta, estrai tutti i dati
# utilizzato nell'indirizzamento alla pagina della singola raccolta
def get_raccolta_by_id(id):

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT raccolte.id_raccolta,raccolte.nome_raccolta,raccolte.descrizione,raccolte.immagine,raccolte.data_creazione,raccolte.data_termine,raccolte.cifra_attuale,raccolte.cifra_da_raggiungere,raccolte.tipo_raccolta,raccolte.organizzatore_raccolta,raccolte.importo_minimo,raccolte.status,utenti.nome,utenti.cognome,utenti.immagine_utente FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente WHERE raccolte.id_raccolta = ?'
    cursor.execute(sql, (id,))
    #retrieve one record at a time from the result set.
    post = cursor.fetchone()

    cursor.close()
    conn.close()

    return post
    


# aggiungi raccolta al database
def add_raccolta(raccolta):
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    now = datetime.now()
    data_oggi = now.strftime("%Y-%m-%d %H:%M")

    # Imposta lo status in base alla data di termine
    raccolta['status'] = 'attiva' if raccolta['data_termine'] > data_oggi else 'terminata'

    if 'immagine_raccolta' in raccolta:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,immagine,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status) VALUES(?,?,?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, (raccolta['titolo_raccolta'],
                             raccolta['descrizione'], 
                             raccolta['immagine_raccolta'],
                             raccolta['data_creazione'],
                             raccolta['data_termine'],
                             raccolta['cifra_attuale'],
                             raccolta['cifra_da_raggiungere'],
                             raccolta['tipo_raccolta'],
                             raccolta['organizzatore_raccolta'],
                             raccolta['importo_minimo'],
                             raccolta['status']
                             ))
    else:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status) VALUES(?,?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, (raccolta['titolo_raccolta'],
                             raccolta['descrizione'], 
                             raccolta['data_creazione'],
                             raccolta['data_termine'],
                             raccolta['cifra_attuale'],
                             raccolta['cifra_da_raggiungere'],
                             raccolta['tipo_raccolta'],
                             raccolta['organizzatore_raccolta'],
                             raccolta['importo_minimo'],
                             raccolta['status']
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

# se data_scadenza > data_oggi and status = 'attiva' allora cambia status in 'terminata'
def update_status_e_portafoglio():

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    now = datetime.now()
    data_oggi = now.strftime("%Y-%m-%d %H:%M")

    # Aggiorna lo status delle raccolte
    sql_update_status = 'UPDATE raccolte SET status = "terminata" WHERE strftime("%Y-%m-%d %H:%M", data_termine) > ? AND status = "attiva" '
    cursor.execute(sql_update_status, (data_oggi, ))

    try:
        conn.commit()
        success = True
    except Exception as e:
        print('Error during status update:', str(e))
        conn.rollback()

    # Lo status è stato aggiornato, se la cifra attuale è superiore alla cifra da raggiungere, aggiorna il portafoglio
    sql_update_portafoglio = 'UPDATE utenti SET portafoglio = portafoglio + raccolte.cifra_attuale ' \
                             'FROM utenti INNER JOIN raccolte ON utenti.id_utente = raccolte.organizzatore_raccolta ' \
                             'WHERE raccolte.cifra_attuale >= raccolte.cifra_da_raggiungere'
    cursor.execute(sql_update_portafoglio)

    try:
        conn.commit()
        success = True
    except Exception as e:
        print('Error during portafoglio update:', str(e))
        conn.rollback()

    conn.close()

    return success
