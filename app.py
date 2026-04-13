from flask import Flask, render_template, request, redirect, url_for
import requests

app = Flask(__name__)

# Ta clé API Google Books
API_KEY = "AIzaSyDXu4Ye5TJ0NiW725teWG7w_xoLDokL7WU"

# Notre mémoire : Une liste vide au démarrage
my_library = []

@app.route('/')
def home():
    return render_template('index.html', library=my_library)

@app.route('/search', methods=['POST'])
def search():
    query = request.form.get('user_book')
    print(f"DEBUG: Recherche reçue : {query}")
    
    if not query:
        return redirect(url_for('home'))
    
    # On demande les résultats bruts de Google
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&printType=books&maxResults=15&key={API_KEY}"
    
    response = requests.get(api_url)
    data = response.json()
    
    # Ton HTML boucle sur 'results'
    results = data.get('items', [])
    
    # Ton HTML utilise 'entry' pour afficher le titre de la recherche
    return render_template('index.html', results=results, entry=query)

@app.route('/add', methods=['POST'])
def add():
    selection = request.form.get('book_info')
    if selection and "|" in selection:
        # On sépare le titre et l'auteur (format : Titre|Auteur)
        parts = selection.split('|')
        new_book = {'title': parts[0], 'author': parts[1]}
        my_library.append(new_book)
    
    # Redirection vers la page bibliothèque après l'ajout
    return redirect(url_for('show_library'))

@app.route('/library')
def show_library():
    return render_template('library.html', library=my_library)

if __name__ == '__main__':
    # use_reloader=False est crucial pour éviter les bugs dans Spyder
    app.run(debug=True, use_reloader=False)