import json
from flask import Flask,render_template,request,redirect,flash,url_for
from datetime import datetime

def loadClubs():
    with open('clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs

    
def loadCompetitions():
    with open('competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

app.competitions = competitions
app.clubs = clubs
app.competitions = competitions


@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form.get('email', '').strip()
    club = next((c for c in clubs if c.get('email') == email), None)


    if not club:
        flash("Adresse email invalide. Veuillez entrer un email valide.")
        return redirect(url_for('index'))

    # Passer toujours un dict complet au template pour éviter les erreurs
    return render_template('welcome.html', club=club, competitions=competitions)

   

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    if not foundClub:
        flash("Club introuvable.")
        return redirect(url_for('index'))

    if not foundClub or not foundCompetition:
        flash("Club ou compétition introuvable.")
        return redirect(url_for('index'))

    # Vérifier si la compétition est passée
    competition_date = datetime.strptime(foundCompetition['date'], "%Y-%m-%d %H:%M:%S")
    if competition_date < datetime.now():
        flash("Vous ne pouvez pas reserver pour une compétition passee.")
        return render_template('welcome.html', club=foundClub, competitions=competitions)

    return render_template('booking.html', club=foundClub, competition=foundCompetition)



@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = next((c for c in competitions if c['name'] == request.form['competition']), None)
    club = next((c for c in clubs if c['name'] == request.form['club']), None)

    if not competition or not club:
        flash("Compétition ou club introuvable.")
        return redirect(url_for('index'))

    try:
        placesRequired = int(request.form['places'])
        if placesRequired <= 0:
            flash("Le nombre de places doit être supérieur à 0.")
            return render_template('booking.html', club=club, competition=competition)
    except ValueError:
        flash("Veuillez entrer un nombre valide.")
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > int(competition['numberOfPlaces']):
        flash(f"Seulement {competition['numberOfPlaces']} places disponibles.")
        return render_template('booking.html', club=club, competition=competition)

    if placesRequired > 12:
        flash("Vous ne pouvez pas reserver plus de 12 places.")
        return render_template('booking.html', club=club, competition=competition)
    
    # Vérifier si le club a assez de points
    if placesRequired > int(club.get('points', 0)):
        flash(f"Vous n'avez que {club.get('points',0)} points disponibles.")
        return render_template('booking.html', club=club, competition=competition)

    # Déduire les points du club
    club['points'] = int(club.get('points',0)) - placesRequired

    # Déduire les places de la compétition
    competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired


    flash("Réservation réussie !")
    return render_template('welcome.html', club=club, competitions=competitions)

# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))