import cv2
import urllib.request
import numpy as np
import requests
import json
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, DictProperty
from pyzbar.pyzbar import decode
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

# --- CONFIGURATION ---
URL_IMAGE = "http://192.168.1.157:8080/shot.jpg" 
BACKEND_URL = "http://127.0.0.1:8000"

Builder.load_string('''
<WindowManager>:
    StartScreen:
    CreateUserScreen:
    AddChildScreen:
    LoginScreen:
    ScanScreen:
    DetailsScreen:

<BackButton@ButtonBehavior+BoxLayout>:
    size_hint: None, None
    size: '110dp', '40dp'
    orientation: 'horizontal'
    padding: ['10dp', 0]
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: (0.2, 0.8, 0.5, 0.1) if self.state == 'normal' else (0.2, 0.8, 0.5, 0.2)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    Widget:
        size_hint: None, None
        size: '15dp', '40dp'
        canvas:
            Color:
                rgba: (0.2, 0.8, 0.5, 1)
            Line:
                points: [self.x + 12, self.y + 26, self.x + 4, self.y + 20, self.x + 12, self.y + 14]
                width: 1.3
                cap: 'round'
                joint: 'round'
    Label:
        text: "Retour"
        color: (0.2, 0.8, 0.5, 1)
        font_size: '15sp'
        halign: 'left'
        valign: 'middle'
        text_size: self.size

<RoundedButton@Button>:
    background_color: (0, 0, 0, 0)
    canvas.before:
        Color:
            rgba: (0.2, 0.8, 0.5, 1) if self.state == 'normal' else (0.15, 0.6, 0.4, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [25,]

<StyledTextInput@TextInput>:
    background_normal: ''
    background_active: ''
    background_disabled_normal: ''
    background_color: (0, 0, 0, 0)
    foreground_color: (0, 0, 0, 1)
    hint_text_color: (0.4, 0.4, 0.4, 1)
    cursor_color: (0.2, 0.8, 0.5, 1)
    padding: [15, 12, 15, 12]
    multiline: False
    canvas.before:
        Color:
            rgba: (0.92, 0.92, 0.92, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
        Color:
            rgba: (0, 0, 0, 1)

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
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        AnchorLayout:
            anchor_x: 'left'
            anchor_y: 'top'
            size_hint_y: None
            height: '70dp'
            padding: [10, 10]
            BackButton:
                on_release: root.manager.current = "start"
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 0, 40, 30]
            spacing: 12
            Label:
                text: "INSCRIPTION"
                font_size: '24sp'
                color: (0.2, 0.8, 0.5, 1)
                bold: True
            StyledTextInput:
                id: new_user
                hint_text: "Nom d'utilisateur"
                size_hint_y: None
                height: '45dp'
            StyledTextInput:
                id: new_email
                hint_text: "Email (ex: test@test.com)"
                size_hint_y: None
                height: '45dp'
            StyledTextInput:
                id: new_pass
                hint_text: "Mot de passe"
                password: True
                size_hint_y: None
                height: '45dp'
            Label:
                id: error_label
                text: ""
                color: (1, 0.3, 0.3, 1)
                font_size: '12sp'
                size_hint_y: None
                height: '30dp'
            RoundedButton:
                text: "VALIDER"
                size_hint_y: None
                height: '55dp'
                on_release: root.validate_and_create()

<AddChildScreen>:
    name: "add_child"
    BoxLayout:
        orientation: 'vertical'
        padding: [40, 40]
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "TON ENFANT"
            font_size: '24sp'
            color: (0.2, 0.8, 0.5, 1)
            bold: True
        StyledTextInput:
            id: child_name
            hint_text: "Prénom de l'enfant"
            size_hint_y: None
            height: '50dp'
        StyledTextInput:
            id: child_age
            hint_text: "Âge"
            input_filter: 'int'
            size_hint_y: None
            height: '50dp'
        Label:
            id: child_error
            text: ""
            color: (1, 0.3, 0.3, 1)
            size_hint_y: None
            height: '30dp'
        RoundedButton:
            text: "ENREGISTRER L'ENFANT"
            size_hint_y: None
            height: '60dp'
            on_release: root.create_child()

<LoginScreen>:
    name: "login"
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: (0.08, 0.08, 0.08, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        AnchorLayout:
            anchor_x: 'left'
            anchor_y: 'top'
            size_hint_y: None
            height: '70dp'
            padding: [10, 10]
            BackButton:
                on_release: root.manager.current = "start"
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 0, 40, 60]
            spacing: 20
            Label:
                text: "CONNEXION"
                font_size: '32sp'
                color: (0.2, 0.8, 0.5, 1)
                bold: True
            StyledTextInput:
                id: login_user
                hint_text: "Nom d'utilisateur"
                size_hint_y: None
                height: '55dp'
            StyledTextInput:
                id: login_pass
                hint_text: "Mot de passe"
                password: True
                size_hint_y: None
                height: '55dp'
            RoundedButton:
                text: "ENTRER"
                size_hint_y: None
                height: '60dp'
                on_release: root.login_user()

<ScanScreen>:
    name: "scan"
    BoxLayout:
        orientation: 'vertical'
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
            bold: True

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
            text: "ANALYSE"
            font_size: '22sp'
            bold: True
            color: (0.2, 0.8, 0.5, 1)
            size_hint_y: None
            height: '40dp'
        BoxLayout:
            orientation: 'vertical'
            padding: 20
            spacing: 5
            canvas.before:
                Color:
                    rgba: (0.15, 0.15, 0.15, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [20]
            Label:
                text: app.product_brand
                font_size: '18sp'
                color: (0.6, 0.6, 0.6, 1)
                halign: 'center'
                size_hint_y: None
                height: '30dp'
            Label:
                text: app.product_name
                font_size: '26sp'
                bold: True
                color: (0.2, 0.8, 0.5, 1)
                halign: 'center'
                text_size: self.width, None
            Label:
                text: "Catégorie : " + app.product_category
                font_size: '14sp'
                color: (0.4, 0.4, 0.4, 1)
                halign: 'center'
            Widget:
                size_hint_y: None
                height: '15dp'
            Label:
                text: app.nutrition_info
                font_size: '18sp'
                halign: 'center'
                valign: 'top'
                text_size: self.width, None
        RoundedButton:
            text: "SCANNER À NOUVEAU"
            size_hint_y: None
            height: '60dp'
            on_release: root.manager.current = "scan"
''')

# --- CLASSES ---
class BackButton(ButtonBehavior, BoxLayout): pass
class StartScreen(Screen): pass
class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class CreateUserScreen(Screen):
    def validate_and_create(self):
        username = self.ids.new_user.text
        email = self.ids.new_email.text
        password = self.ids.new_pass.text
        
        # Envoi de 'name' et 'username' pour compatibilité maximale backend
        payload = {"name": username, "username": username, "email": email, "password": password}
        
        try:
            res = requests.post(f"{BACKEND_URL}/users/", json=payload, timeout=5)
            print(f"Server Response: {res.status_code} - {res.json()}")

            if res.status_code in [200, 201]:
                user_data = res.json()
                # Récupération sécurisée de l'ID
                uid = user_data.get("id") or user_data.get("id_user") or 1
                App.get_running_app().user_id = uid
                self.manager.current = "add_child"
            elif res.status_code == 422:
                self.ids.error_label.text = "Erreur : Email ou format invalide"
            else:
                self.ids.error_label.text = f"Erreur serveur : {res.status_code}"
        except Exception as e:
            print(f"Network Error: {e}")
            self.ids.error_label.text = "Erreur de connexion au serveur"

class AddChildScreen(Screen):
    def create_child(self):
        name = self.ids.child_name.text
        age = self.ids.child_age.text
        parent_id = App.get_running_app().user_id
        if not name or not age: 
            self.ids.child_error.text = "Veuillez remplir tous les champs"
            return
        try:
            payload = {"name": name, "age": int(age), "id_parent": parent_id}
            res = requests.post(f"{BACKEND_URL}/children/{parent_id}", json=payload, timeout=5)
            if res.status_code in [200, 201]:
                self.manager.current = "login"
        except:
            self.ids.child_error.text = "Erreur de connexion"

class LoginScreen(Screen):
    def login_user(self):
        if self.ids.login_user.text:
            self.manager.current = "scan"

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
                        App.get_running_app().fetch_details(code)
                        self.manager.current = "details"
                
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.ids.camera_preview.texture = texture
        except: pass

class PandooApp(App):
    product_name = StringProperty("Chargement...")
    product_brand = StringProperty("Marque")
    product_category = StringProperty("Alimentation")
    nutrition_info = StringProperty("")
    status_text = StringProperty("Alignez le code-barres")
    nutrition_data = DictProperty({})
    user_id = 1

    def fetch_details(self, code):
        headers = {'User-Agent': 'PandooApp - Python/Kivy'}
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == 1:
                    p = data["product"]
                    
                    # Extraction Marque
                    brand_raw = p.get("brands") or p.get("brands_tags", ["Inconnue"])
                    if isinstance(brand_raw, list): brand_raw = brand_raw[0]
                    self.product_brand = str(brand_raw).split(',')[0].strip()
                    
                    # Extraction Catégorie (via categories_old)
                    cat_raw = p.get("categories_old", "Alimentation")
                    self.product_category = str(cat_raw).split(',')[0].strip() if cat_raw else "Alimentation"
                    
                    self.product_name = p.get("product_name", "Produit Inconnu")
                    
                    n = p.get("nutriments", {})
                    self.nutrition_data = {
                        "calories": float(n.get('energy-kcal_100g', 0)),
                        "glucides": float(n.get('sugars_100g', 0)),
                        "proteins": float(n.get('proteins_100g', 0)),
                        "salt": float(n.get('salt_100g', 0))
                    }
                    self.nutrition_info = (
                        f"⚡ Calories : {self.nutrition_data['calories']} kcal\n\n"
                        f"🍭 Sucres : {self.nutrition_data['glucides']} g\n\n"
                        f"🧂 Sel : {self.nutrition_data['salt']} g\n\n"
                        f"🥩 Protéines : {self.nutrition_data['proteins']} g"
                    )
                    self.save_to_backend(code)
        except Exception as e:
            print(f"OFF Error: {e}")

    def save_to_backend(self, code):
        payload = {
            "barcode": str(code), 
            "name": self.product_name, 
            "type": self.product_category,
            "brand": self.product_brand, 
            "calories": self.nutrition_data.get('calories', 0.0),
            "glucides": self.nutrition_data.get('glucides', 0.0),
            "proteins": self.nutrition_data.get('proteins', 0.0),
            "lipids": 0.0, 
            "salt": self.nutrition_data.get('salt', 0.0), 
            "calcium": 0.0
        }
        try:
            # Envoi au format JSON automatique avec requests
            requests.post(f"{BACKEND_URL}/products/?id_child=1", json=payload, timeout=5)
        except Exception as e:
            print(f"Backend Save Error: {e}")

    def build(self): return WindowManager()

if __name__ == '__main__':
    PandooApp().run()