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
    entry = request.form.get('user_book')
    # On récupère l'ID spécifique si    l'utilisateur a cliqué sur une suggestion
    selected_id = request.form.get('selected_book_id') 

    if not entry:
        return redirect(url_for('homeme'))

    params = {'q': entry, 'key': API_KEY}
    response = requests.get("https://www.googleapis.com/books/v1/volumes", params=params)
    data = response.json()

    if 'items' in data:
        book_list = data['items']
        
        # LOGIQUE "AMAZON" : Si l'utilisateur a cliqué sur un livre précis dans la liste, 
        # on le remonte en 1ère position.
        if selected_id:
            book_list.sort(key=lambda x: 0 if x.get('id') == selected_id else 1)

        return render_template('index.html', results=book_list, entry=entry, library=my_library)
    
    return render_template('index.html', error="Aucun résultat", library=my_library)

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