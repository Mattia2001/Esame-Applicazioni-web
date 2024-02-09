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

    # this is required because I defined id_user in the database rather than "id"
    def get_id(self):
        # Return the user identifier as a unicode string
        return str(self.id_utente)