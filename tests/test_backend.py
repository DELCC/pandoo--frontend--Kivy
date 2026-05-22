# tests/test_backend.py
import pytest
import requests_mock
from datetime import datetime
import backend_client

# ==========================================
# 1. TESTS DE LA LOGIQUE DE CALCUL D'ÂGE
# ==========================================

def test_calculate_age_valide():
    """Vérifie le calcul exact de l'âge pour une date valide."""
    annee_actuelle = datetime.today().year
    # On simule un enfant né il y a 5 ans le 1er janvier
    birthdate_str = f"{annee_actuelle - 5}-01-01"
    
    age = backend_client.calculate_age(birthdate_str)
    assert age == 5

def test_calculate_age_invalide():
    """Vérifie que la fonction gère l'erreur et renvoie 0 sans crasher

    si le format de la date est complètement faux.
    """
    age = backend_client.calculate_age("date-incroyable-2020")
    assert age == 0


# ==========================================
# 2. TESTS DES REQUÊTES VERS LE BACKEND
# ==========================================

def test_check_user_by_email_success():
    """Vérifie le comportement si l'utilisateur existe en base de données."""
    email = "amaury.jacobe1@gmail.com"
    url_cible = f"{backend_client.BACKEND_URL}/users/by-email/{email}"
    mock_response = {"id": 42, "name": "Amaury", "email": email}

    with requests_mock.Mocker() as mock:
        # On simule une réponse positive du serveur FastAPI (200 OK)
        mock.get(url_cible, json=mock_response, status_code=200)

        result = backend_client.check_user_by_email(email)

        assert result is not None
        assert result["id"] == 42
        assert result["name"] == "Amaury"

def test_check_user_by_email_not_found():
    """Vérifie le comportement si l'utilisateur n'existe pas (Erreur 404)."""
    email = "inconnu@gmail.com"
    url_cible = f"{backend_client.BACKEND_URL}/users/by-email/{email}"

    with requests_mock.Mocker() as mock:
        # Le serveur répond que l'utilisateur n'existe pas
        mock.get(url_cible, status_code=404)

        result = backend_client.check_user_by_email(email)
        
        # Ton code intercepte et doit renvoyer None
        assert result is None

def test_create_user_request():
    """Vérifie l'envoi d'un POST pour la création d'un utilisateur."""
    url_cible = f"{backend_client.BACKEND_URL}/users/"
    payload = {"name": "Test", "username": "testuser", "email": "test@pandoo.fr", "password": "SecurePassword123"}

    with requests_mock.Mocker() as mock:
        # On simule une création réussie (201 Created)
        mock.post(url_cible, json={"status": "created"}, status_code=201)

        res = backend_client.create_user_request(payload)

        assert res.status_code == 201
        # On vérifie que la fonction a bien transmis les données à l'API
        assert mock.last_request.json() == payload