# interroga il database richiedendo i dati utente

import sqlite3

def get_users():
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT id_utente, email FROM utenti'
    cursor.execute(sql)
    users = cursor.fetchall()

    cursor.close()
    conn.close()

    return users

def get_user_by_id(id):
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE id_utente = ?'
    cursor.execute(sql, (id,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

# find the user by looking at the email, used to verify whether the user already exists
def get_user_by_email(email):
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    sql = 'SELECT * FROM utenti WHERE email = ?'
    cursor.execute(sql, (email,))
    user = cursor.fetchone()

    cursor.close()
    conn.close()

    return user

# add a new user to database
def add_user(user):

    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    success = False
    sql = 'INSERT INTO utenti(nome,cognome,email,password,immagine_utente,portafoglio) VALUES(?,?,?,?,?,?)'

    try:
        cursor.execute(
            sql, (user['nome'], user['cognome'], user['email'], user['password'], user['immagine_utente'], user['portafoglio']))
        conn.commit()
        success = True
    except Exception as e:
        print('ERROR', str(e))
        # if something goes wrong: rollback
        conn.rollback()

    cursor.close()
    conn.close()

    return success

# se una raccolta è andata a buon fine, modifica il portafoglio dell'utente che ha iniziato la raccolta
def modifica_portafoglio(raccolta, utente):
     
    conn = sqlite3.connect('db/raccolte_fondi.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    success = False

    # Aggiorna il portafoglio dell'utente che ha completato la raccolta
    # Se la raccolta ha avuto successo allora cifra_attuale >= cifra_da_raggiungere
    sql_update_portafoglio = 'UPDATE utenti SET portafoglio = portafoglio + ? WHERE id_utente = ?'
    cursor.execute(sql_update_portafoglio, (raccolta['cifra_attuale'], raccolta['organizzatore_raccolta']))

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
