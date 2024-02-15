from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id_utente, nome, cognome, email, password,
                 immagine_utente, portafoglio):
        self.id_utente = id_utente
        self.nome = nome
        self.cognome = cognome
        self.email = email
        self.password = password
        self.immagine_utente = immagine_utente
        self.portafoglio = portafoglio

    '''Nel database ho definito chiave primaria "id_utente" invece di "id" come richiesto da flask login.
       Con questa funzione ci assicuriamo che l'identificatore univoco dell'utente sia ugualmente individuato
       seppur con un nome diverso'''

    def get_id(self):
        # Return the user identifier as a unicode string
        return str(self.id_utente)