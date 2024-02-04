# import module
from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime

from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

import utenti_dao
#import raccolte_dao
#import donazioni_dao

from models import User

from PIL import Image
#import PIL.Image

PROFILE_IMG_HEIGHT = 130
POST_IMG_WIDTH = 300

# create the application
app = Flask(__name__)

app.config['SECRET_KEY'] = 'Secret key del sito'

login_manager = LoginManager()
login_manager.init_app(app)

# define the homepage
@app.route('/')
def home():
    
    # interroga il database, richiedi tutte le raccolte attive con le rispettive informazioni,
    # ordinale mostrando prima quelle più vicine alla scadenza


    #return render_template('home.html', posts=posts_db)
    return render_template('home.html')

# restituisci solo la pagina per iscriversi
@app.route('/iscriviti')
def iscriviti():
    return render_template('iscriviti.html')

# ricevi i dati dal form di iscrizione, controlla se l'utente esiste già, se non
# esiste aggiungi i dati al database
@app.route('/iscriviti', methods=['POST'])
def iscriviti_post():

    # dati del nuovo utente compilati nel form da essere inseriti nel database
    nuovo_utente_form = request.form.to_dict()

    # controlla se l'utente esiste già
    user_in_db = utenti_dao.get_user_by_email(nuovo_utente_form.get('email'))

    # se l'utente esiste già reindirizza alla stessa pagine per iscriversi
    if user_in_db:
        flash('C\'è già un utente registrato con questa email', 'danger')
        return redirect(url_for('iscriviti'))
    else:
        img_profilo = ''
        usr_image = request.files['immagine_utente']
        if usr_image:
            # Open the user-provided image using the Image module
            img = Image.open(usr_image)

            # Get the width and height of the image
            width, height = img.size

            # Calculate the new width while maintaining the aspect ratio
            new_width = PROFILE_IMG_HEIGHT * width / height

            # Define the size for thumbnail creation with the desired height and calculated width
            size = new_width, PROFILE_IMG_HEIGHT
            img.thumbnail(size, Image.Resampling.LANCZOS)

            # Calculate the coordinates for cropping the image to a square shape
            left = (new_width/2 - PROFILE_IMG_HEIGHT/2)
            top = 0
            right = (new_width/2 + PROFILE_IMG_HEIGHT/2)
            bottom = PROFILE_IMG_HEIGHT

            # Crop the image using the calculated coordinates to create a square image
            img = img.crop((left, top, right, bottom))

            # Extracting file extension from the image filename
            ext = usr_image.filename.split('.')[-1]

            # Saving the image with a unique filename in the 'static' directory
            img.save('static/' + nuovo_utente_form.get('nome').lower() + '_' + nuovo_utente_form.get('cognome').lower() + '.' + ext)

            img_profilo = nuovo_utente_form.get('nome').lower() + '_' + nuovo_utente_form.get('cognome').lower() + '.' + ext

        nuovo_utente_form['password'] = generate_password_hash(nuovo_utente_form.get('password'))
        # Updating the 'immagine_utnete' field in the user dictionary with the image filename
        nuovo_utente_form['immagine_utente'] = img_profilo

        success = utenti_dao.add_user(nuovo_utente_form)

        if success:
            flash('Utente creato correttamente', 'success')
            return redirect(url_for('home'))
        else:
            flash('Errore nella creazione del utente: riprova!', 'danger')

    return redirect(url_for('iscriviti'))

# ricevi i dati dal form per  il login situato nella homepage
#se l'utente è già registrato e i dati coincidono consenti l'accesso

@app.route('/login', methods=['POST'])
def login():

  utente_form = request.form.to_dict()

  utente_db = utenti_dao.get_user_by_email(utente_form['email'])

    # se in fase di login l'email o la password sono sbagliati printare errore
  if not utente_db or not check_password_hash(utente_db['password'], utente_form['password']):
    flash('Credenziali non valide, riprova', 'danger')
    return redirect(url_for('home'))
  else:
    new = User(id_utente=utente_db['id_utente'], nome=utente_db['nome'], cognome=utente_db['cognome'], email=utente_db['email'], password=utente_db['password'], immagine_utente=utente_db['immagine_utente'] )
    login_user(new, True)
    flash('Bentornato ' + utente_db['nome'] + ' ' + utente_db['cognome'] + '!', 'success')

    return redirect(url_for('home'))

# define the current user
@login_manager.user_loader
def load_user(user_id):

    db_user = utenti_dao.get_user_by_id(user_id)
    if db_user is not None:
        user = User(id_utente=db_user['id_utente'], nome=db_user['nome'], cognome=db_user['cognome'], email=db_user['email'], password=db_user['password'], immagine_utente=db_user['immagine_utente'])
    else:
        user = None

    return user

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# pagina con le raccolte terminate
@app.route('/raccolte_terminate')
def raccolte_terminate():
    
    # interroga il database e richiedi tutte le raccolte con lo status "terminata", ordina in ordine
    # decrescente di data, quindi mostrando prima quelle finite più di recente
  
    return render_template('raccolte_terminate.html')

# pagina con tutte le raccolte dell'utente
@app.route('/le_mie_raccolte')
def le_mie_raccolte():

    return render_template('le_mie_raccolte.html')


@app.route('/about')
def about():

    return render_template('about.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)