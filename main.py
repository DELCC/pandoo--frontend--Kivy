import cv2
import urllib.request
import numpy as np
import requests
import json
from kivy.config import Config

# --- CONFIGURATION DE LA FENÊTRE ---
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '650')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, DictProperty
from pyzbar.pyzbar import decode
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout

# --- CONFIGURATION RÉSEAU ---
URL_IMAGE = "http://192.168.1.157:8080/shot.jpg" 
BACKEND_URL = "http://127.0.0.1:8000"

Builder.load_string('''
<EyeButton@ButtonBehavior+AnchorLayout>:
    size_hint_x: None
    width: '50dp'

<BackgroundLayer@Image>:
    source: 'pandoo002.png'
    allow_stretch: True
    keep_ratio: False
    size_hint: (1, 1)
    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
    canvas.after:
        Color:
            rgba: (0, 0, 0, 0.2)
        Rectangle:
            pos: self.pos
            size: self.size

<WindowManager>:
    StartScreen:
    CreateUserScreen:
    LoginScreen:
    AddChildScreen:
    ScanScreen:
    DetailsScreen:

<BackButton@ButtonBehavior+BoxLayout>:
    size_hint: None, None
    size: '100dp', '40dp'
    orientation: 'horizontal'
    padding: ['10dp', 0]
    canvas.before:
        Color:
            rgba: (0, 0, 0, 0.3)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
    Label:
        text: "< Retour"
        color: (1, 1, 1, 1)
        font_size: '14sp'
        bold: True

<RoundedButton@Button>:
    background_color: (0, 0, 0, 0)
    font_size: '18sp'
    bold: True
    canvas.before:
        Color:
            rgba: (0.15, 0.75, 0.5, 1) if self.state == 'normal' else (0.1, 0.6, 0.4, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [25,]

# --- STYLE DES CHAMPS (INPUTS) UNIFIÉ ET ARRONDI ---
<BaseInput@BoxLayout>:
    hint_text: ""
    is_password: False
    orientation: 'horizontal'
    size_hint_y: None
    height: '55dp'
    canvas.before:
        Color:
            rgba: (1, 1, 1, 0.95)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
    TextInput:
        id: ti
        hint_text: root.hint_text
        password: root.is_password
        background_normal: ''
        background_active: ''
        background_color: (0,0,0,0)
        foreground_color: (0.1, 0.1, 0.1, 1)
        hint_text_color: (0.5, 0.5, 0.5, 1)
        cursor_color: (0.15, 0.75, 0.5, 1)
        padding: [20, 18, 15, 15]
        font_size: '16sp'
        multiline: False
        write_tab: False

<StartScreen>:
    name: "start"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 80]
            spacing: 20
            Label:
                text: "PANDOO"
                font_size: '56sp'
                bold: True
            Widget:
                size_hint_y: 1
            RoundedButton:
                text: "CONNEXION"
                size_hint_y: None
                height: '60dp'
                on_release: root.manager.current = "login"
            RoundedButton:
                text: "CRÉER UN COMPTE"
                size_hint_y: None
                height: '60dp'
                on_release: root.manager.current = "create_user"

<CreateUserScreen>:
    name: "create_user"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [30, 20]
            AnchorLayout:
                anchor_x: 'left'
                size_hint_y: None
                height: '60dp'
                BackButton:
                    on_release: root.manager.current = "start"
            BoxLayout:
                orientation: 'vertical'
                padding: [10, 20, 10, 0]
                spacing: 12
                Label:
                    text: "INSCRIPTION"
                    font_size: '28sp'
                    bold: True
                    size_hint_y: None
                    height: '60dp'
                BaseInput:
                    id: new_user
                    hint_text: "Nom d'utilisateur"
                BaseInput:
                    id: new_email
                    hint_text: "Email"
                BaseInput:
                    id: new_pass
                    hint_text: "Mot de passe"
                    is_password: True
                RoundedButton:
                    text: "VALIDER"
                    size_hint_y: None
                    height: '60dp'
                    on_release: root.validate_and_create()
                
                # --- NOUVEAU BOUTON GOOGLE ---
                Button:
                    text: "S'INSCRIRE AVEC GOOGLE"
                    size_hint_y: None
                    height: '50dp'
                    bold: True
                    background_color: (0, 0, 0, 0)
                    canvas.before:
                        Color:
                            rgba: (0.9, 0.9, 0.9, 1) if self.state == 'normal' else (0.8, 0.8, 0.8, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [25,]
                    color: (0.2, 0.2, 0.2, 1)
                    on_release: root.login_with_google()

<LoginScreen>:
    name: "login"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [30, 20]
            AnchorLayout:
                anchor_x: 'left'
                size_hint_y: None
                height: '60dp'
                BackButton:
                    on_release: root.manager.current = "start"
            BoxLayout:
                orientation: 'vertical'
                padding: [10, 60, 10, 80]
                spacing: 20
                Label:
                    text: "CONNEXION"
                    font_size: '36sp'
                    bold: True
                    size_hint_y: None
                    height: '100dp'
                BaseInput:
                    id: login_user
                    hint_text: "Utilisateur"
                BoxLayout:
                    size_hint_y: None
                    height: '55dp'
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 0.95)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [15,]
                    TextInput:
                        id: login_pass
                        hint_text: "Mot de passe"
                        password: True
                        background_normal: ''
                        background_active: ''
                        background_color: (0,0,0,0)
                        foreground_color: (0.1, 0.1, 0.1, 1)
                        hint_text_color: (0.5, 0.5, 0.5, 1)
                        padding: [20, 18, 15, 15]
                        font_size: '16sp'
                        multiline: False
                    EyeButton:
                        on_release: login_pass.password = not login_pass.password
                        Image:
                            source: 'eye_on.png' if login_pass.password else 'eye_off.png'
                            size_hint: None, None
                            size: '22dp', '22dp'
                            opacity: 0.6
                RoundedButton:
                    text: "ENTRER"
                    size_hint_y: None
                    height: '60dp'
                    on_release: root.login_user()

<AddChildScreen>:
    name: "add_child"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 60]
            spacing: 20
            Label:
                text: "TON ENFANT"
                font_size: '32sp'
                bold: True
            BaseInput:
                id: child_name
                hint_text: "Prénom"
            BaseInput:
                id: child_age
                hint_text: "Âge"
            RoundedButton:
                text: "ENREGISTRER"
                size_hint_y: None
                height: '60dp'
                on_release: root.create_child()

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
                        rgba: (0.15, 0.75, 0.5, 0.5)
                    Line:
                        width: 3
                        rounded_rectangle: (self.width*0.15, self.height*0.3, self.width*0.7, self.height*0.4, 20)
        Label:
            text: app.status_text
            size_hint_y: 0.2
            color: (0.15, 0.75, 0.5, 1)
            bold: True
            font_size: '18sp'

<DetailsScreen>:
    name: "details"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [30, 40]
            spacing: 20
            Label:
                text: "SCAN RÉUSSI !"
                font_size: '32sp'
                bold: True
                size_hint_y: None
                height: '60dp'
            BoxLayout:
                orientation: 'vertical'
                padding: [25, 30]
                spacing: 12
                canvas.before:
                    Color:
                        rgba: (1, 1, 1, 1)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                Label:
                    text: app.product_name
                    font_size: '20sp'
                    bold: True
                    color: (0.1, 0.1, 0.1, 1)
                    halign: 'center'
                    size_hint_y: None
                    height: '60dp'
                    text_size: self.width, None
                Widget:
                    size_hint_y: None
                    height: '2dp'
                    canvas:
                        Color:
                            rgba: (0.15, 0.75, 0.5, 0.5)
                        Rectangle:
                            pos: self.x + 30, self.y
                            size: self.width - 60, self.height
                Label:
                    text: "[i]Valeurs pour 100g :[/i]"
                    markup: True
                    font_size: '16sp'
                    color: (0.4, 0.4, 0.4, 1)
                    size_hint_y: None
                    height: '30dp'
                    halign: 'left'
                    text_size: self.width, None
                Label:
                    text: app.nutrition_info
                    font_size: '18sp'
                    color: (0.2, 0.2, 0.2, 1)
                    halign: 'left'
                    valign: 'top'
                    text_size: self.width, None
                    line_height: 1.3
            Widget:
                size_hint_y: 0.1
            RoundedButton:
                text: "RESCANNER"
                size_hint_y: None
                height: '60dp'
                on_release: root.manager.current = "scan"
''')

# --- LOGIQUE PYTHON ---
class BackButton(ButtonBehavior, BoxLayout): pass
class StartScreen(Screen): pass
class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class CreateUserScreen(Screen):
    def validate_and_create(self):
        username = self.ids.new_user.ids.ti.text
        email = self.ids.new_email.ids.ti.text
        password = self.ids.new_pass.ids.ti.text
        
        if not username or not email or not password: 
            return
            
        payload = {"name": username, "username": username, "email": email, "password": password}
        
        try:
            res = requests.post(f"{BACKEND_URL}/users/", json=payload, timeout=5)
            if res.status_code in [200, 201]:
                user_data = res.json()
                App.get_running_app().user_id = user_data.get("id", 1)
                self.manager.current = "add_child"
        except: 
            pass

    def login_with_google(self):
        """Ouvre le navigateur pour l'authentification Google via le backend"""
        import webbrowser
        webbrowser.open(f"{BACKEND_URL}/auth/login")

class AddChildScreen(Screen):
    def create_child(self):
        name = self.ids.child_name.ids.ti.text
        age = self.ids.child_age.ids.ti.text
        parent_id = App.get_running_app().user_id
        try:
            payload = {"name": name, "age": int(age), "id_parent": parent_id}
            res = requests.post(f"{BACKEND_URL}/children/{parent_id}", json=payload, timeout=5)
            if res.status_code in [200, 201]: self.manager.current = "login"
        except: pass

class LoginScreen(Screen):
    def login_user(self):
        if self.ids.login_user.ids.ti.text: self.manager.current = "scan"

class ScanScreen(Screen):
    def on_enter(self): self.update_event = Clock.schedule_interval(self.update, 1.0 / 30.0)
    def on_leave(self): Clock.unschedule(self.update_event)
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
    nutrition_info = StringProperty("")
    status_text = StringProperty("Scannez un produit")
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
                    brand = p.get("brands", "Inconnu").split(',')[0]
                    
                    # Correction du titre : on utilise un vrai saut de ligne
                    self.product_name = f"{p.get('product_name', 'Produit')}\n({brand})"
                    
                    n = p.get("nutriments", {})
                    
                    # Utilisation des triples guillemets pour gérer les sauts de ligne proprement
                    self.nutrition_info = (
                        f"Énergie : {n.get('energy-kcal_100g', 0)} kcal\n"
                        f"Sucres : {n.get('sugars_100g', 0)} g\n"
                        f"Sel : {n.get('salt_100g', 0)} g\n"
                        f"Protéines : {n.get('proteins_100g', 0)} g"
                    )
                    
                    self.save_to_backend(code)
        except Exception as e:
            print(f"Erreur lors de la récupération : {e}")
            self.product_name = "Erreur de connexion"

    def save_to_backend(self, code):
        headers = {'User-Agent': 'PandooApp - Python/Kivy'}
        try:
            url_off = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res_off = requests.get(url_off, headers=headers, timeout=5)
            
            if res_off.status_code == 200:
                data = res_off.json()
                if data.get("status") == 1:
                    p = data["product"]
                    n = p.get("nutriments", {})

                    # --- NETTOYAGE RADICAL DU TYPE ---
                    # On essaie plusieurs clés par sécurité
                    raw_type = p.get("categories_old") or p.get("categories") or "Aliment"
                    
                    # Si c'est une liste, on prend le premier élément
                    if isinstance(raw_type, list):
                        type_produit = raw_type[0]
                    else:
                        # Si c'est une string, on découpe par la virgule ET on nettoie
                        type_produit = str(raw_type).split(',')[0].strip()

                    payload = {
                        "barcode": str(code),
                        "name": p.get("product_name", "Inconnu"),
                        "brand": p.get("brands", "Inconnu").split(',')[0],
                        "type": type_produit, # Ici, on n'aura que le premier
                        "calories": float(n.get("energy-kcal_100g", 0)),
                        "glucides": float(n.get("carbohydrates_100g", 0)),
                        "sugars": float(n.get("sugars_100g", 0)),
                        "proteins": float(n.get("proteins_100g", 0)),
                        "lipids": float(n.get("fat_100g", 0)),
                        "salt": float(n.get("salt_100g", 0)),
                        "calcium": float(n.get("calcium_100g", 0)),
                        "id_parent": self.user_id 
                    }

                    # Envoi à ton API (127.0.0.1:8000 d'après ta capture)
                    id_enfant = 1 
                    full_url = f"{BACKEND_URL}/products/?id_child={id_enfant}"

                    response = requests.post(full_url, json=payload, timeout=5)
                    
                    if response.status_code in [200, 201]:
                        print(f"✅ Type enregistré : {type_produit}")
                    else:
                        print(f"❌ Erreur API : {response.text}")
        except Exception as e:
            print(f"❌ Erreur : {e}")

    def build(self): return WindowManager()

if __name__ == '__main__':
    PandooApp().run()