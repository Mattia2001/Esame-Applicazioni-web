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
    status_terminata = 'terminata'

    sql = 'SELECT * FROM raccolte WHERE status = ? ORDER BY data_creazione DESC'
    cursor.execute(sql, (status_terminata,))
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

    sql = 'SELECT raccolte.id_raccolta,raccolte.nome_raccolta,raccolte.descrizione,raccolte.immagine,raccolte.data_creazione,raccolte.data_termine,raccolte.cifra_attuale,raccolte.cifra_da_raggiungere,raccolte.tipo_raccolta,raccolte.organizzatore_raccolta,raccolte.importo_minimo,raccolte.status,aggiornata,utenti.nome,utenti.cognome,utenti.immagine_utente FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente WHERE raccolte.id_raccolta = ?'
    cursor.execute(sql, (id,))
    #retrieve one record at a time from the result set.
    post = cursor.fetchone()

    cursor.close()
    conn.close()

    return post

# necessaria per la pagina raccolte utente, dove id_utente è uguale all'id del current user
def get_raccolta_by_id_utente(id_utente):

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM raccolte WHERE raccolte.organizzatore_raccolta = ?'
    cursor.execute(sql, (id_utente,))
    #retrieve one record at a time from the result set.
    raccolte_utente = cursor.fetchall()

    cursor.close()
    conn.close()

    return raccolte_utente
    


# aggiungi raccolta al database
def add_raccolta(raccolta):
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    now = datetime.now()
    data_oggi = now.strftime("%Y-%m-%d %H:%M")

    # Imposta lo status in base alla data di termine
    #raccolta['status'] = 'attiva' if raccolta['data_termine'] > data_oggi else 'terminata'

    if 'immagine_raccolta' in raccolta:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,immagine,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status,aggiornata) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)'
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
                             raccolta['status'],
                             raccolta['aggiornata']
                             ))
    else:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status,aggiornata) VALUES(?,?,?,?,?,?,?,?,?,?,?)'
        cursor.execute(sql, (raccolta['titolo_raccolta'],
                             raccolta['descrizione'], 
                             raccolta['data_creazione'],
                             raccolta['data_termine'],
                             raccolta['cifra_attuale'],
                             raccolta['cifra_da_raggiungere'],
                             raccolta['tipo_raccolta'],
                             raccolta['organizzatore_raccolta'],
                             raccolta['importo_minimo'],
                             raccolta['status'],
                             raccolta['aggiornata']
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

'''Questa funzione verrà invocata ad ogni richiesta http per mezzo dell'apposito decoratore nell'app.py .
Lo scopo di questa funzione è controllare quali raccolte sono scadute ed eventualmente aggioranre il portafoglio.
Le raccolte possono terminare o perchè è trascorso il tempo massimo e quindi l'obiettivo non è stato raggiunto o
perchè hanno raggiunto l'obiettivo. Nel primo caso lo status viene cambiato in "terminata" e i soldi non vengono trasferiti.
Nel secondo caso lo status viene cambiato in "terminata", i soldi trasferiti e il campo "aggioranta" cambiato da "no" a "si".
L'ultimo campo è necessario per evitare che nuovi soldi vengano trasferiti ad ogni richiesta http.
'''
def update_status_e_portafoglio():

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    now = datetime.now()
    data_oggi = now.strftime("%Y-%m-%d %H:%M")

    # Aggiorna lo status delle raccolte se la data odierna è maggiore di quella di scadenza
    # o la raccolta ha superato l'obiettivo
    sql_update_status = 'UPDATE raccolte SET status = "terminata" WHERE strftime("%Y-%m-%d %H:%M", data_termine) <= ? AND status = "attiva" OR (cifra_attuale >= cifra_da_raggiungere AND status = "attiva")'
    cursor.execute(sql_update_status, (data_oggi, ))

    # Seleziona le raccolte che necessitano di aggiornamento del portafoglio
    raccolte_da_aggiornare = cursor.execute('''
    SELECT id_raccolta, organizzatore_raccolta, cifra_attuale
    FROM raccolte
    WHERE status = "terminata" AND aggiornata = "no"
    ''').fetchall()

    # Aggiorna il portafoglio per ogni raccolta
    for raccolta in raccolte_da_aggiornare:
        cursor.execute('''
        UPDATE utenti
        SET portafoglio = COALESCE(portafoglio, 0) + ?
        WHERE id_utente = ?
        ''', (raccolta['cifra_attuale'], raccolta['organizzatore_raccolta']))

        # Segna la raccolta come aggiornata
        cursor.execute('''
        UPDATE raccolte
        SET aggiornata = "si"
        WHERE id_raccolta = ?
        ''', (raccolta['id_raccolta'],))


    try:
        conn.commit()
        success = True
    except Exception as e:
        print('Error during portafoglio update:', str(e))
        conn.rollback()

    conn.close()

    return success
