# interroga il database richiedendo i dati sulle varie raccolte

import sqlite3
from datetime import date, datetime, timedelta

# estrai tutte le raccolte, indipendentemente dal fatto che siano ancora valide o no
def get_raccolte():
    conn = sqlite3.connect('db/raccolte_fondi.db')

    # specify that returned data have to stored into a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT raccolte.id_raccolta, raccolte.nome_raccolta, raccolte.descrizione, raccolte.immagine, raccolte.data_creazione, raccolte.data_termine, raccolte.cifra_attuale, raccolte.cifra_da_raggiungere, raccolte.tipo_raccolta, raccolte.organizzatore_raccolta, raccolte.importo_minimo, raccolte.status, raccolte.aggiornata, raccolte.importo_massimo, raccolte.tipo_modificabile, utenti.nome, utenti.cognome FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente ORDER BY data_creazione DESC'
    cursor.execute(sql)
    raccolte = cursor.fetchall()

    cursor.close()
    conn.close()

    return raccolte


# estrai tutte le raccolte terminate, quindi con status = 'terminata'
# estrai anche nome, cognome e immagine utente degli organizzatori
def get_raccolte_terminate():

    conn = sqlite3.connect('db/raccolte_fondi.db')

    # specify that returned data have to stored into a dictionary
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    status_terminata = 'terminata'

    sql = 'SELECT raccolte.id_raccolta,raccolte.nome_raccolta,raccolte.descrizione,raccolte.immagine,raccolte.data_creazione,raccolte.data_termine,raccolte.cifra_attuale,raccolte.cifra_da_raggiungere,raccolte.tipo_raccolta,raccolte.organizzatore_raccolta,raccolte.importo_minimo,raccolte.status,raccolte.aggiornata,raccolte.importo_massimo,utenti.nome,utenti.cognome,utenti.immagine_utente FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente WHERE status = ? ORDER BY data_creazione DESC'
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

    sql = 'SELECT raccolte.id_raccolta,raccolte.nome_raccolta,raccolte.descrizione,raccolte.immagine,raccolte.data_creazione,raccolte.data_termine,raccolte.cifra_attuale,raccolte.cifra_da_raggiungere,raccolte.tipo_raccolta,raccolte.organizzatore_raccolta,raccolte.importo_minimo,raccolte.status,raccolte.aggiornata,raccolte.importo_massimo,utenti.nome,utenti.cognome,utenti.immagine_utente FROM raccolte LEFT JOIN utenti ON raccolte.organizzatore_raccolta = utenti.id_utente WHERE raccolte.id_raccolta = ?'
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
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,immagine,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status,aggiornata,importo_massimo,tipo_modificabile) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)'
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
                             raccolta['aggiornata'],
                             raccolta['importo_massimo'],
                             raccolta['tipo_modificabile']
                             ))
    else:
        sql = 'INSERT INTO raccolte(nome_raccolta,descrizione,data_creazione,data_termine,cifra_attuale,cifra_da_raggiungere,tipo_raccolta,organizzatore_raccolta,importo_minimo,status,aggiornata,importo_massimo,tipo_modificabile) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)'
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
                             raccolta['aggiornata'],
                             raccolta['importo_massimo'],
                             raccolta['tipo_modificabile']
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

# modifica la raccolta in corso con nuovi dati forniti dall'utente
def modifica_raccolta_by_id_raccolta(id_raccolta, nuovi_dati):

    success = False

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # l'istruzione UPDATE non supporta la stessa sintassi di INSERT
    if 'nuova_immagine_raccolta' in nuovi_dati:
        sql = 'UPDATE raccolte SET nome_raccolta = ?, descrizione = ?, immagine = ?, cifra_da_raggiungere = ?, tipo_raccolta = ?, importo_minimo = ?, importo_massimo=?, data_termine=? WHERE id_raccolta = ?'
        cursor.execute(sql, (nuovi_dati['nuovo_titolo_raccolta'],
                            nuovi_dati['nuova_descrizione'], 
                            nuovi_dati['nuova_immagine_raccolta'],
                            nuovi_dati['nuova_cifra_da_raggiungere'],
                            nuovi_dati['nuovo_tipo_raccolta'],
                            nuovi_dati['nuovo_importo_minimo'], 
                            nuovi_dati['nuovo_importo_massimo'],
                            nuovi_dati['nuova_data_termine'],
                            id_raccolta))
        
    else:
        sql = 'UPDATE raccolte SET nome_raccolta = ?, descrizione = ?, cifra_da_raggiungere = ?, tipo_raccolta = ?, importo_minimo = ?, importo_massimo = ?, data_termine=? WHERE id_raccolta = ?'
        cursor.execute(sql, (nuovi_dati['nuovo_titolo_raccolta'],
                            nuovi_dati['nuova_descrizione'], 
                            nuovi_dati['nuova_cifra_da_raggiungere'],
                            nuovi_dati['nuovo_tipo_raccolta'],
                            nuovi_dati['nuovo_importo_minimo'],
                            nuovi_dati['nuovo_importo_massimo'], 
                            nuovi_dati['nuova_data_termine'],
                            id_raccolta))
    
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

def cancella_raccolta_e_donazioni(id_raccolta):

    success = False

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Prima cancella tutte le donazioni associate alla raccolta
    cursor.execute('DELETE FROM donazioni WHERE raccolta = ?', (id_raccolta,))
    
    # Poi cancella la raccolta stessa
    cursor.execute('DELETE FROM raccolte WHERE id_raccolta = ?', (id_raccolta,))
    
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
    sql_raccolte_da_aggiornare = 'SELECT id_raccolta, organizzatore_raccolta, cifra_attuale FROM raccolte WHERE status = "terminata" AND aggiornata = "no"'
    raccolte_da_aggiornare = cursor.execute(sql_raccolte_da_aggiornare).fetchall()

    # Aggiorna il portafoglio per ogni raccolta
    for raccolta in raccolte_da_aggiornare:
        sql_aggiorna_portafoglio = 'UPDATE utenti SET portafoglio = COALESCE(portafoglio, 0) + ? WHERE id_utente = ?'
        cursor.execute(sql_aggiorna_portafoglio, (raccolta['cifra_attuale'], raccolta['organizzatore_raccolta']))

        # Ora che il portafoglio è aggiornato, segna la raccolta come aggiornata=si
        sql_aggiornata_si = 'UPDATE raccolte SET aggiornata = "si" WHERE id_raccolta = ?'
        cursor.execute(sql_aggiornata_si, (raccolta['id_raccolta'],))

    try:
        conn.commit()
        success = True
    except Exception as e:
        print('Errore durante l\'aggiornamento del portafoglio:', str(e))
        conn.rollback()

    conn.close()

    return success

'''Come la precedente, anche questa funzione viene invocata ad ogni richiesta http'''

def update_tipo_modificabile():
     
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False

    now = datetime.now()
    cinque_minuti_fa = now - timedelta(minutes=5)
    
    try:
        # Aggiorna direttamente le raccolte dove la data_creazione è minore di "cinque_minuti_fa"
        sql_aggiorna_tipo_modificabile = '''
            UPDATE raccolte
            SET tipo_modificabile = "no"
            WHERE data_creazione <= ? AND tipo_modificabile = "si"
        '''
        cursor.execute(sql_aggiorna_tipo_modificabile, (cinque_minuti_fa.strftime("%Y-%m-%d %H:%M"),))
        conn.commit()
        success = True
        print("Aggiornamento 'tipo_modificabile' completato con successo.")
    except Exception as e:
        print('Errore durante l\'aggiornamento del campo "tipo_modificabile":', e)
        conn.rollback()
    finally:
        conn.close()

    return success