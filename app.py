from flask import Flask, render_template, request, redirect, url_for
import requests
import sqlite3

QUESTIONS_BANK = {
    "9782070360420": [  # L'ISBN du Petit Prince (exemple)
        {"q": "Qui est le narrateur ?", "r": "L'aviateur", "options": ["L'aviateur", "Le roi", "La rose"]}
    ],
    "9782253003021": [  # L'ISBN de La Peste
        {"q": "Où se passe l'action ?", "r": "Oran", "options": ["Oran", "Alger", "Paris"]}
    ],
    "9782268075631": [  # L'ISBN de La Peste
        {"q": "Qui est le meilleur ami Argentin de Reb ?", "r": "Diego Haas", "options": ["Gomez Lorenz", "Juan Carlos", "Diego Haas"]}
    ]
}

app = Flask(__name__) 
app.jinja_env.globals.update(enumerate=enumerate)
API_KEY = "AIzaSyDXu4Ye5TJ0NiW725teWG7w_xoLDokL7WU"

def get_db_connection():
    conn = sqlite3.connect('bibliotheque.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS livres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titre TEXT NOT NULL,
                auteur TEXT NOT NULL,
                isbn TEXT -- On ajoute cette colonne
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
            isbns = info.get('industryIdentifiers', [])
            isbn_val = isbns[0].get('identifier') if isbns else "Pas d'ISBN"
            
            results.append({
                'title': info.get('title'),
                'author': info.get('authors', ['Inconnu'])[0],
                'isbn': isbn_val, 
            })
    return render_template('index.html', results=results, entry=query)

@app.route('/add', methods=['POST'])
def add():
    selection = request.form.get('book_info')
    if selection and "|" in selection:
        titre, auteur, isbn = selection.split('|')
        
        with get_db_connection() as conn:
            conn.execute('INSERT INTO livres (titre, auteur, isbn) VALUES (?, ?, ?)', 
                         (titre, auteur, isbn))
    return redirect(url_for('show_library'))

@app.route('/library')
def show_library():
    with get_db_connection() as conn:
        mes_livres = conn.execute('SELECT * FROM livres').fetchall()
    return render_template('library.html', library=mes_livres)

@app.route('/delete/<int:book_id>', methods=['POST'])
def delete(book_id):
    with get_db_connection() as conn:
        conn.execute('DELETE FROM livres WHERE id = ?', (book_id,))
    return redirect(url_for('show_library'))

@app.route('/quiz/<int:book_id>', methods=['GET', 'POST'])
def quiz(book_id):
    with get_db_connection() as conn:
        book = conn.execute('SELECT * FROM livres WHERE id = ?', (book_id,)).fetchone()
    
    questions = QUESTIONS_BANK.get(book['isbn'])
    
    if not questions:
        return f"<h1>Pas de quiz pour l'ISBN {book['isbn']} !</h1><a href='/library'>Retour</a>"
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
    