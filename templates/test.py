import requests

# Remplace par ta clé si celle-là ne marche plus
API_KEY = "AIzaSyDXu4Ye5TJ0NiW725teWG7w_xoLDokL7WU"

def tester_google_books():
    livre_cherche = input("Entrez le nom d'un livre ou auteur : ")
    
    # On simule la requête exacte que fait ton site
    # intitle: pour la précision, printType=books pour éviter les archives
    url = f"https://www.googleapis.com/books/v1/volumes?q=intitle:{livre_cherche}&printType=books&maxResults=5&key={API_KEY}"
    
    print(f"\n--- Requête envoyée à Google ---\n{url}\n")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if "items" in data:
            print(f"✅ Succès ! {len(data['items'])} résultats trouvés :\n")
            
            for i, item in enumerate(data['items'], 1):
                info = item.get('volumeInfo', {})
                titre = info.get('title', 'Pas de titre')
                auteurs = ", ".join(info.get('authors', ['Auteur inconnu']))
                description = info.get('description', 'Pas de résumé')[:100] + "..."
                has_image = "OUI" if "imageLinks" in info else "NON"
                
                print(f"Livre {i}:")
                print(f"  - Titre : {titre}")
                print(f"  - Auteur : {auteurs}")
                print(f"  - Image dispo : {has_image}")
                print(f"  - Résumé : {description}")
                print("-" * 30)
        else:
            print("❌ Google n'a rien trouvé pour cette recherche.")
            print("Réponse brute :", data)

    except Exception as e:
        print(f"💥 Erreur lors de l'appel : {e}")

if __name__ == "__main__":
    tester_google_books()