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
    query = request.form.get('q')
    if not query:
        return redirect(url_for('home'))
    
    # On force 'intitle:' pour que Python cherche comme le JavaScript
    # On demande 20 résultats pour avoir du choix
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&maxResults=20&key={API_KEY}"
    
    response = requests.get(api_url)
    data = response.json()
    
    books = []
    if 'items' in data:
        for item in data['items']:
            info = item.get('volumeInfo', {})
            # On ne garde que les livres qui ont un titre et un auteur
            if 'title' in info and 'authors' in info:
                books.append({
                    'title': info['title'],
                    'author': info['authors'][0],
                    'description': info.get('description', 'Pas de description disponible.'),
                    'thumbnail': info.get('imageLinks', {}).get('thumbnail', '')
                })
    
    return render_template('index.html', books=books, query=query)

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