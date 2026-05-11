import requests
import openfoodfacts

class OpenFoodFactsAPI:
    # Initialisation de l'API OpenFoodFacts avec ton User-Agent
    api = openfoodfacts.API(user_agent="PandooApp/1.0")

    @staticmethod
    def get_product_data(barcode):
        """
        Récupère les informations brutes d'un produit depuis OpenFoodFacts.
        """
        try:
            # Utilise la méthode de la bibliothèque pour obtenir le produit
            result = OpenFoodFactsAPI.api.product.get(barcode)
            if result and result.get('status') == 1:
                return result
            return None
        except Exception as e:
            print(f"Erreur lors de la récupération OFF : {e}")
            return None

    @staticmethod
    def send_to_backend(product_data):
        """
        Formate et envoie les données du produit vers le backend DELCC.
        """
        # URL de ta route POST définie dans routers/products.py
        url = "http://127.0.0.1:8000/products/"
        
        # Extraction sécurisée des données
        product_info = product_data.get('product', {})
        nutriments = product_info.get('nutriments', {})
        
        # Préparation du JSON pour correspondre à ton schéma ProductCreate
        # On utilise float() et int() pour garantir les types attendus par la BDD
        payload = {
            "barcode": int(product_data.get('code', 0)),
            "type": "Alimentation", # Valeur par défaut pour ton champ String obligatoire
            "name": product_info.get('product_name', 'Produit inconnu'),
            "brand": product_info.get('brands', 'Marque inconnue'),
            "calories": float(nutriments.get('energy-kcal_100g', 0.0)),
            "calcium": float(nutriments.get('calcium_100g', 0.0)),
            "proteins": float(nutriments.get('proteins_100g', 0.0)),
            "lipids": float(nutriments.get('fat_100g', 0.0)),
            "salt": float(nutriments.get('salt_100g', 0.0))
        }

        try:
            # Envoi vers le backend avec id_child=1 (requis par ta route routers/products.py)
            params = {"id_child": 1}
            response = requests.post(url, json=payload, params=params)

            if response.status_code == 200:
                print(f"✅ Synchronisation réussie : {payload['name']} enregistré.")
                return response.json()
            else:
                print(f"❌ Erreur Backend ({response.status_code}) : {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            print("⚠️ Erreur : Le backend DELCC n'est pas lancé (uvicorn).")
            return None
        except Exception as e:
            print(f"⚠️ Erreur lors de l'envoi au backend : {e}")
            return None

# Pour tester le fichier indépendamment (optionnel)
if __name__ == "__main__":
    test_code = "3254381058694"
    data = OpenFoodFactsAPI.get_product_data(test_code)
    if data:
        OpenFoodFactsAPI.send_to_backend(data)