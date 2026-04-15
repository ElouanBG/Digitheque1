from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

QUESTIONS_BANK = {
    "La Peste": [
        {"q": "Dans quelle ville se déroule l'intrigue ?", "r": "Oran", "options": ["Paris", "Oran", "Alger"]},
        {"q": "Qui est le personnage principal ?", "r": "Dr Rieux", "options": ["Dr Rieux", "Tarrou", "Cottard"]}
    ],
    "Le Petit Prince": [
        {"q": "Quel animal le Petit Prince demande-t-il de dessiner ?", "r": "Un mouton", "options": ["Un chat", "Un mouton", "Un éléphant"]},
        {"q": "Sur quelle planète vit-il ?", "r": "Astéroïde B 612", "options": ["Astéroïde B 612", "Mars", "Pluton"]}
    ]
}


app = Flask(__name__) 
app.jinja_env.globals.update(enumerate=enumerate)
API_KEY = "AIzaSyDXu4Ye5TJ0NiW725teWG7w_xoLDokL7WU"

# --- FONCTION POUR LA BASE DE DONNÉES ---
def get_db_connection():
    # Connexion au fichier de la base de données
    conn = sqlite3.connect('bibliotheque.db')
    conn.row_factory = sqlite3.Row  # Permet d'accéder aux colonnes par nom
    return conn

# Création de la table si elle n'existe pas au lancement
def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL
            )
        ''')
init_db()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('user_book')
    if not query: return redirect(url_for('home'))
    
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&printType=books&maxResults=10&key={API_KEY}"
    data = requests.get(url).json()
    
    results = []
    if "items" in data:
        for item in data['items']:
            info = item.get('volumeInfo', {})
            results.append({
                'title': info.get('title'),
                'author': info.get('authors', ['Inconnu'])[0],
                'description': info.get('description', 'Pas de résumé')[:200] + "...",
                'image': info.get('imageLinks', {}).get('thumbnail', '')
            })
    return render_template('index.html', results=results, entry=query)

@app.route('/add', methods=['POST'])
def add():
    selection = request.form.get('book_info')
    if selection and "|" in selection:
        titre, auteur = selection.split('|')
        with get_db_connection() as conn:
            conn.execute('INSERT INTO livres (titre, auteur) VALUES (?, ?)', (titre, auteur))
    return redirect(url_for('show_library'))

@app.route('/library')
def show_library():
    with get_db_connection() as conn:
        mes_livres = conn.execute('SELECT * FROM livres').fetchall()
    return render_template('library.html', library=mes_livres)

# --- LA NOUVELLE ROUTE POUR SUPPRIMER ---
@app.route('/delete/<int:book_id>', methods=['POST'])
def delete(book_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM livres WHERE id = ?', (book_id,))
    return redirect(url_for('show_library'))

# --- DEPLACE LA ROUTE QUIZ ICI (AVANT LE RUN) ---
@app.route('/quiz/<int:book_id>', methods=['GET', 'POST'])
def quiz(book_id):
    with get_db_connection() as conn:
        book = conn.execute('SELECT * FROM livres WHERE id = ?', (book_id,)).fetchone()
    
    questions = QUESTIONS_BANK.get(book['titre'])
    
    if not questions:
        return f"<h1>Désolé, pas encore de quiz pour {book['titre']} !</h1><a href='/library'>Retour</a>"

    if request.method == 'POST':
        score = 0
        for i, q in enumerate(questions):
            user_answer = request.form.get(f"question_{i}")
            if user_answer == q['r']:
                score += 1
        return render_template('quiz_result.html', score=score, total=len(questions), book=book)

    return render_template('quiz.html', book=book, questions=questions)

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    