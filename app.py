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
    
    # On demande 40 résultats pour avoir un "bac à sable" suffisant pour trier
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{query}&printType=books&maxResults=40&key={API_KEY}"
    
    import requests
    response = requests.get(api_url)
    data = response.json()
    
    books = []
    if 'items' in data:
        for item in data['items']:
            info = item.get('volumeInfo', {})
            
            # --- LE FILTRE DE QUALITÉ ---
            # 1. On vérifie s'il y a un ISBN (preuve que c'est un vrai livre commercial)
            isbns = info.get('industryIdentifiers', [])
            has_isbn = any(id_type['type'] in ['ISBN_10', 'ISBN_13'] for id_type in isbns)
            
            # 2. On vérifie s'il y a un auteur et une image (élimine les archives vides)
            has_author = 'authors' in info
            has_image = 'imageLinks' in info
            
            # On n'ajoute que si c'est du "solide"
            if has_isbn and has_author and has_image:
                books.append({
                    'title': info['title'],
                    'author': info['authors'][0],
                    'description': info.get('description', 'Pas de description disponible.')[:300] + "...",
                    'thumbnail': info['imageLinks'].get('thumbnail', ''),
                    'year': info.get('publishedDate', 'N/A')[:4]
                })

    # On trie pour mettre les titres les plus courts (souvent les originaux) en premier
    books.sort(key=lambda x: len(x['title']))
    
    return render_template('index.html', books=books[:12], query=query)

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