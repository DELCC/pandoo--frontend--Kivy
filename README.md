# Pandoo Frontend Kivy

Application mobile/desktop développée avec **Python** et **Kivy**.  
Pandoo permet de scanner un produit alimentaire, récupérer ses données nutritionnelles depuis OpenFoodFacts, afficher un verdict adapté à un enfant, gérer les profils enfants et envoyer les produits scannés vers un backend.

Source analysée : branche `main_002`.

## Fichiers du projet

### `main.py`

Fichier principal de l’application.

Il configure la fenêtre Kivy, lance l’application `PandooApp`, initialise les propriétés utilisées par l’interface `.kv`, récupère les données produit depuis OpenFoodFacts, calcule les indicateurs nutritionnels, génère les couleurs d’alerte et envoie les données au backend.

Rôles principaux :

- lancement de l’application Kivy ;
- configuration de la fenêtre ;
- stockage des données affichées dans l’interface ;
- récupération produit via code-barres ;
- analyse sucre, sel, fibres, protéines, lipides, glucides ;
- affichage du conseil Pandoo ;
- détection des allergènes ;
- envoi du produit scanné vers le backend ;
- gestion du compteur de scans et des récompenses.

### `pandoo.kv`

Fichier d’interface Kivy.

Il définit l’apparence visuelle de l’application : écrans, boutons, champs de formulaire, cartes nutritionnelles, arrière-plans, scan caméra, historique et page de détails produit.

Écrans définis :

- `StartScreen` : écran d’accueil ;
- `CreateUserScreen` : création de compte ;
- `LoginScreen` : connexion ;
- `AddChildScreen` : ajout d’un enfant/Pandoo ;
- `ChildListScreen` : sélection d’un enfant ;
- `ScanScreen` : scan produit ;
- `DetailsScreen` : verdict nutritionnel ;
- `HistoryScreen` : historique des produits.

### `scanner.py`

Module de scan de code-barres.

Il utilise :

- `cv2` pour manipuler l’image caméra ;
- `pyzbar` pour détecter et lire les codes-barres.

La classe `BarcodeScanner` contient une méthode statique `scan(frame)` qui reçoit une image, cherche un code-barres, puis retourne son contenu sous forme de texte.

### `gemini.py`

Module lié à l’intelligence artificielle Gemini.

Il utilise l’API Google Gemini pour générer :

- une histoire courte personnalisée pour l’enfant ;
- un quiz nutritionnel adapté à son âge.

Fonctions principales :

- `generate_story(...)` : crée une histoire magique autour du produit scanné ;
- `generate_quiz(...)` : génère trois questions simples sur le produit et la nutrition.

### `api.py`

Ancien module d’intégration OpenFoodFacts/backend.

Tout le code est actuellement commenté.  
Il servait à :

- récupérer un produit depuis OpenFoodFacts ;
- extraire ses données nutritionnelles ;
- formater les données ;
- envoyer le produit vers le backend FastAPI.

Ce fichier semble être une ancienne version ou un brouillon remplacé en grande partie par la logique présente dans `main.py`.

### `nutrition.py`

Ancien module de formatage nutritionnel.

Tout le code est actuellement commenté.  
Il devait contenir une classe `NutritionFormatter` capable de :

- récupérer les nutriments principaux ;
- préparer un texte lisible pour l’interface.

Ce fichier semble conservé comme référence mais n’est pas actif.

### `requirements.txt`

Liste des dépendances Python du projet.

Principales bibliothèques :

- `Kivy` : interface graphique ;
- `opencv-python` : gestion image/caméra ;
- `pyzbar` : lecture de codes-barres ;
- `requests` : appels HTTP ;
- `pillow`, `numpy`, `pygame` : dépendances graphiques et image.

Installation :

```bash
pip install -r requirements.txt
