import cv2
import urllib.request
import numpy as np
import requests
import re
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from pyzbar.pyzbar import decode
from kivy.lang import Builder

# --- CONFIGURATION ---
URL_IMAGE = "http://10.0.7.196:8080/shot.jpg"

Builder.load_string('''
<WindowManager>:
    StartScreen:
    CreateUserScreen:
    AddChildScreen:
    LoginScreen:
    ScanScreen:
    DetailsScreen:

<RoundedButton@Button>:
    background_color: (0, 0, 0, 0)
    background_normal: ''
    canvas.before:
        Color:
            rgba: (0.2, 0.8, 0.5, 1) if self.state == 'normal' else (0.15, 0.6, 0.4, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [25,]

<StyledTextInput@TextInput>:
    background_color: (0.12, 0.12, 0.12, 1)
    foreground_color: (1, 1, 1, 1)
    cursor_color: (0.2, 0.8, 0.5, 1)
    hint_text_color: (0.4, 0.4, 0.4, 1)
    padding: [15, 15]
    font_size: '16sp'
    multiline: False

<StartScreen>:
    name: "start"
    BoxLayout:
        orientation: 'vertical'
        padding: [40, 60]
        spacing: 25
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "PANDOO 🐼"
            font_size: '56sp'
            bold: True
            color: (0.2, 0.8, 0.5, 1)
            size_hint_y: 0.6
        RoundedButton:
            text: "SE CONNECTER"
            size_hint_y: None
            height: '60dp'
            on_release: root.manager.current = "login"
        Button:
            text: "CRÉER UN COMPTE"
            size_hint_y: None
            height: '60dp'
            color: (0.2, 0.8, 0.5, 1)
            background_color: (0,0,0,0)
            on_release: root.manager.current = "create_user"

<CreateUserScreen>:
    name: "create_user"
    BoxLayout:
        orientation: 'vertical'
        padding: [30, 40]
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "INSCRIPTION"
            font_size: '24sp'
            bold: True
            size_hint_y: None
            height: '60dp'
        StyledTextInput:
            id: name_input
            hint_text: "Nom complet"
        StyledTextInput:
            id: email_input
            hint_text: "Email"
        StyledTextInput:
            id: password_input
            hint_text: "Mot de passe"
            password: True
        Label:
            id: error_label
            text: ""
            color: (1, 0.3, 0.3, 1)
            size_hint_y: None
            height: '30dp'
        RoundedButton:
            text: "CRÉER MON COMPTE"
            size_hint_y: None
            height: '60dp'
            on_release: root.register_user()

<AddChildScreen>:
    name: "add_child"
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "PROFIL ENFANT"
            font_size: '24sp'
            bold: True
        StyledTextInput:
            id: child_name
            hint_text: "Prénom de l'enfant"
        StyledTextInput:
            id: child_age
            hint_text: "Âge"
            input_filter: 'int'
        RoundedButton:
            text: "TERMINER"
            size_hint_y: None
            height: '60dp'
            on_release: root.create_child()

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: 'vertical'
        padding: [30, 50]
        spacing: 20
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "CONNEXION"
            font_size: '28sp'
            bold: True
        StyledTextInput:
            id: login_email
            hint_text: "Email"
        StyledTextInput:
            id: login_password
            hint_text: "Mot de passe"
            password: True
        Label:
            id: login_error
            text: ""
            color: (1, 0.4, 0.4, 1)
        RoundedButton:
            text: "S'IDENTIFIER"
            size_hint_y: None
            height: '60dp'
            on_release: root.login_user()

<ScanScreen>:
    name: "scan"
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0, 0, 0, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        RelativeLayout:
            size_hint_y: 0.8
            Image:
                id: camera_preview
            Widget:
                canvas.after:
                    Color:
                        rgba: (0.2, 0.8, 0.5, 0.6)
                    Line:
                        width: 2
                        rounded_rectangle: (self.width*0.15, self.height*0.3, self.width*0.7, self.height*0.4, 15)
        Label:
            text: app.status_text
            size_hint_y: 0.2
            color: (0.2, 0.8, 0.5, 1)

<DetailsScreen>:
    name: "details"
    BoxLayout:
        orientation: 'vertical'
        padding: 25
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: app.product_name
            font_size: '26sp'
            bold: True
            color: (0.2, 0.8, 0.5, 1)
            size_hint_y: None
            height: '60dp'
        ScrollView:
            Label:
                text: app.nutrition_info
                font_size: '18sp'
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
                line_height: 1.3
        RoundedButton:
            text: "SCANNER UN AUTRE PRODUIT"
            size_hint_y: None
            height: '60dp'
            on_release: root.manager.current = "scan"
''')

class StartScreen(Screen): pass

class CreateUserScreen(Screen):
    def register_user(self):
        user_data = {
            "name": self.ids.name_input.text,
            "email": self.ids.email_input.text,
            "password": self.ids.password_input.text
        }
        try:
            res = requests.post("http://127.0.0.1:8000/users/", json=user_data, timeout=5)
            if res.status_code == 200:
                App.get_running_app().user_id = res.json()["user"]["id"]
                self.manager.current = "add_child"
            else:
                self.ids.error_label.text = "Erreur inscription"
        except: self.ids.error_label.text = "Serveur injoignable"

class AddChildScreen(Screen):
    def create_child(self):
        app = App.get_running_app()
        child_data = {
            "name": self.ids.child_name.text,
            "age": int(self.ids.child_age.text or 0),
            "id_parent": app.user_id
        }
        try:
            url = f"http://127.0.0.1:8000/children/{app.user_id}"
            res = requests.post(url, json=child_data, timeout=5)
            if res.status_code == 200:
                # Redirection vers la connexion après la création réussie
                self.manager.current = "login"
        except: 
            self.ids.child_error.text = "Erreur création enfant"

class LoginScreen(Screen):
    def login_user(self):
        email = self.ids.login_email.text.strip()
        password = self.ids.login_password.text.strip()
        
        if not email or not password:
            self.ids.login_error.text = "Champs manquants"
            return
            
        login_data = {"email": email, "password": password}
        
        try:
            # Envoi vers ton futur endpoint de login
            res = requests.post("http://127.0.0.1:8000/login", json=login_data, timeout=5)
            if res.status_code == 200:
                data = res.json()
                App.get_running_app().user_id = data.get("id")
                self.manager.current = "scan"
            else:
                self.ids.login_error.text = "Email ou mot de passe incorrect"
        except:
            # Pour tes tests si le backend login n'est pas prêt, 
            # tu peux décommenter la ligne suivante pour forcer l'accès :
            # self.manager.current = "scan"
            self.ids.login_error.text = "Serveur injoignable"

class ScanScreen(Screen):
    def on_enter(self):
        self.update_event = Clock.schedule_interval(self.update, 1.0 / 30.0)
    def on_leave(self):
        Clock.unschedule(self.update_event)

    def update(self, dt):
        try:
            img_resp = urllib.request.urlopen(URL_IMAGE, timeout=1)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, -1)
            if frame is not None:
                for barcode in decode(frame):
                    code = barcode.data.decode('utf-8')
                    if code.isdigit():
                        Clock.unschedule(self.update_event)
                        
                        # 1. On récupère les détails (OpenFoodFacts)
                        app = App.get_running_app()
                        app.fetch_details(code)
                        
                        # 2. ON ENREGISTRE DANS TON API (Backend)
                        self.save_to_backend(code)
                        
                        # 3. On change d'écran
                        self.manager.current = "details"
                
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.ids.camera_preview.texture = texture
        except: pass

    def save_to_backend(self, code):
        app = App.get_running_app()
        import json

        # 1. On récupère les nutriments stockés lors du fetch_details
        # On utilise getattr pour éviter un crash si nutrition_data n'est pas encore prêt
        nutri = getattr(app, 'nutrition_data', {})
        
        # 2. Préparation du dictionnaire (Body JSON)
        # On s'assure que chaque valeur est du bon type (str ou float)
        product_data = {
            "barcode": str(code),
            "name": app.product_name,
            "type": "Alimentation",
            "brand": "Inconnu",
            "calories": float(nutri.get('calories', 0)),
            "glucides": float(nutri.get('sugars', 0)),
            "proteins": float(nutri.get('proteins', 0)),
            "lipids": 0.0,
            "salt": float(nutri.get('salt', 0)),
            "calcium": 0.0
        }

        try:
            # 3. Encodage propre en UTF-8 pour les accents
            payload = json.dumps(product_data, ensure_ascii=False).encode('utf-8')
            headers = {'Content-Type': 'application/json; charset=utf-8'}
            
            # 4. Construction de l'URL avec l'id_child en paramètre (Query Parameter)
            # On utilise l'ID 1 pour le moment (à rendre dynamique plus tard)
            id_enfant_test = 1 
            url = f"http://127.0.0.1:8000/products/?id_child={id_enfant_test}"
            
            # 5. Envoi de la requête POST
            res = requests.post(url, data=payload, headers=headers, timeout=5)
            
            if res.status_code in [200, 201]:
                print(f"✅ Succès : '{app.product_name}' enregistré pour l'enfant {id_enfant_test}")
            else:
                # Si ça échoue, on affiche le message précis du backend
                print(f"❌ Erreur {res.status_code} : {res.text}")
                
        except Exception as e:
            print(f"📡 Erreur de connexion au serveur : {e}")

class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class PandooApp(App):
    product_name = StringProperty("Produit")
    nutrition_info = StringProperty("")
    status_text = StringProperty("Prêt pour le scan")
    user_id = None

    def fetch_details(self, code):
        headers = {'User-Agent': 'PandooApp - contact@pandoo.com'}
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res = requests.get(url, headers=headers, timeout=5)
            
            # 1. On force l'encodage sur la réponse brute
            res.encoding = 'utf-8' 
            
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == 1:
                    p = data["product"]
                    n = p.get("nutriments", {})
                    
                    # --- NETTOYAGE EXTRÊME DES ACCENTS ---
                    raw_name = p.get("product_name", "Produit inconnu")
                    # On s'assure que c'est bien de l'unicode propre
                    if isinstance(raw_name, bytes):
                        self.product_name = raw_name.decode('utf-8')
                    else:
                        self.product_name = str(raw_name)
                    
                    self.nutrition_data = {
                        "calories": float(n.get('energy-kcal_100g', 0)),
                        "sugars": float(n.get('sugars_100g', 0)),
                        "proteins": float(n.get('proteins_100g', 0)),
                        "salt": float(n.get('salt_100g', 0))
                    }
                    
                    self.nutrition_info = (
                        f"⚡ Calories : {self.nutrition_data['calories']} kcal\n\n"
                        f"🍭 Sucres : {self.nutrition_data['sugars']} g\n\n"
                        f"🧂 Sel : {self.nutrition_data['salt']} g\n\n"
                        f"🥩 Protéines : {self.nutrition_data['proteins']} g"
                    )
                    
                    print(f"✅ Détails récupérés : {self.product_name}")
                else:
                    self.product_name = "Non trouvé"
                    self.nutrition_info = "Code inconnu."
            else:
                self.product_name = "Erreur"
                self.nutrition_info = f"Erreur serveur : {res.status_code}"
                
        except Exception as e:
            print(f"📡 Erreur : {e}")
            self.product_name = "Erreur"
            self.nutrition_info = "Connexion perdue."

    def build(self):
        return WindowManager()

if __name__ == '__main__':
    PandooApp().run()