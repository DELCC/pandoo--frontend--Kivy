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

# --- CONFIGURATION ---
URL_IMAGE = "http://192.168.1.157:8080/shot.jpg" 
BACKEND_URL = "http://127.0.0.1:8000"

# UN SEUL BUILDER ICI AVEC TOUTES LES MISES À JOUR
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
    canvas.before:
        Color:
            rgba: (0.1, 0.1, 0.1, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    canvas.after:
        Color:
            rgba: (0, 0, 0, 0.4)
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
    size: '110dp', '40dp'
    orientation: 'horizontal'
    padding: ['10dp', 0]
    spacing: '5dp'
    canvas.before:
        Color:
            rgba: (1, 1, 1, 0.2) if self.state == 'normal' else (1, 1, 1, 0.4)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [10,]
    Widget:
        size_hint: None, None
        size: '15dp', '40dp'
        canvas:
            Color:
                rgba: (1, 1, 1, 1)
            Line:
                points: [self.x + 12, self.y + 26, self.x + 4, self.y + 20, self.x + 12, self.y + 14]
                width: 1.5
                cap: 'round'
                joint: 'round'
    Label:
        text: "Retour"
        color: (1, 1, 1, 1)
        font_size: '15sp'

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
    background_color: (1, 1, 1, 0.9)
    foreground_color: (0, 0, 0, 1)
    cursor_color: (0.2, 0.8, 0.5, 1)
    padding: [15, 12, 15, 12]
    multiline: False

<PasswordInput@BoxLayout>:
    hint_text: ""
    orientation: 'horizontal'
    size_hint_y: None
    height: '55dp'
    canvas.before:
        Color:
            rgba: (1, 1, 1, 0.9)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [12,]
    TextInput:
        id: ti
        hint_text: root.hint_text
        password: True
        background_normal: ''
        background_active: ''
        background_color: (0,0,0,0)
        padding: [15, 18, 15, 15]
    EyeButton:
        on_release: ti.password = not ti.password
        Image:
            source: 'eye_on.png' if ti.password else 'eye_off.png'
            size_hint: None, None
            size: '25dp', '25dp'

<StartScreen>:
    name: "start"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 60]
            spacing: 25
            Label:
                text: "PANDOO"
                font_size: '60sp'
                bold: True
                color: (1, 1, 1, 1)
                outline_color: (0,0,0, 1)
                outline_width: 2
            Widget:
                size_hint_y: 0.3
            RoundedButton:
                text: "SE CONNECTER"
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
                    font_size: '28sp'
                    color: (1, 1, 1, 1)
                    bold: True
                StyledTextInput:
                    id: new_user
                    hint_text: "Nom d'utilisateur"
                    size_hint_y: None
                    height: '50dp'
                StyledTextInput:
                    id: new_email
                    hint_text: "Email"
                    size_hint_y: None
                    height: '50dp'
                PasswordInput:
                    id: new_pass_container
                    hint_text: "Mot de passe"
                Label:
                    id: error_label
                    text: ""
                    color: (1, 0.2, 0.2, 1)
                    bold: True
                RoundedButton:
                    text: "VALIDER"
                    size_hint_y: None
                    height: '60dp'
                    on_release: root.validate_and_create()

<LoginScreen>:
    name: "login"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
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
                padding: [40, 40, 40, 80]
                spacing: 20
                Label:
                    text: "CONNEXION"
                    font_size: '32sp'
                    color: (1, 1, 1, 1)
                    bold: True
                StyledTextInput:
                    id: login_user
                    hint_text: "Nom d'utilisateur"
                    size_hint_y: None
                    height: '55dp'
                PasswordInput:
                    id: login_pass_container
                    hint_text: "Mot de passe"
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
            padding: [40, 40]
            spacing: 15
            Label:
                text: "TON ENFANT"
                font_size: '28sp'
                color: (1, 1, 1, 1)
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
                color: (1, 0.2, 0.2, 1)
                bold: True
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
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [25, 40]
            spacing: 15
            Label:
                text: "SCAN RÉUSSI !"
                font_size: '26sp'
                bold: True
                color: (1, 1, 1, 1)
                size_hint_y: None
                height: '40dp'
            
            BoxLayout:
                orientation: 'vertical'
                padding: [20, 20]
                spacing: 8
                canvas.before:
                    Color:
                        rgba: (1, 1, 1, 0.95)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [20]
                
                Label:
                    text: app.product_name
                    font_size: '20sp'
                    bold: True
                    color: (0.1, 0.1, 0.1, 1)
                    size_hint_y: None
                    height: '65dp'
                    halign: 'center'
                    text_size: self.width, None

                Widget:
                    size_hint_y: None
                    height: '2dp'
                    canvas:
                        Color:
                            rgba: (0.2, 0.8, 0.5, 0.6)
                        Rectangle:
                            pos: self.x + 30, self.y
                            size: self.width - 60, self.height

                Label:
                    text: "Valeurs pour 100g :"
                    font_size: '15sp'
                    bold: True
                    italic: True
                    color: (0.4, 0.4, 0.4, 1)
                    size_hint_y: None
                    height: '30dp'
                    halign: 'left'
                    text_size: self.width - 40, None

                Label:
                    text: app.nutrition_info
                    font_size: '17sp'
                    color: (0.2, 0.2, 0.2, 1)
                    halign: 'left'
                    valign: 'top'
                    text_size: self.width - 40, self.height
                    line_height: 1.3
            
            Widget:
                size_hint_y: 0.1

            RoundedButton:
                text: "RESCANNER"
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
        password = self.ids.new_pass_container.ids.ti.text
        payload = {"name": username, "username": username, "email": email, "password": password}
        try:
            res = requests.post(f"{BACKEND_URL}/users/", json=payload, timeout=5)
            if res.status_code in [200, 201]:
                user_data = res.json()
                uid = user_data.get("id") or user_data.get("id_user") or 1
                App.get_running_app().user_id = uid
                self.manager.current = "add_child"
            else:
                self.ids.error_label.text = "Erreur lors de la création"
        except:
            self.ids.error_label.text = "Erreur de connexion"

class AddChildScreen(Screen):
    def create_child(self):
        name = self.ids.child_name.text
        age = self.ids.child_age.text
        parent_id = App.get_running_app().user_id
        if not name or not age: return
        try:
            payload = {"name": name, "age": int(age), "id_parent": parent_id}
            res = requests.post(f"{BACKEND_URL}/children/{parent_id}", json=payload, timeout=5)
            if res.status_code in [200, 201]:
                self.manager.current = "login"
        except: pass

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
                    
                    # Récupération de la marque
                    brand = p.get("brands", "Marque inconnue").split(',')[0].strip()
                    self.product_name = f"{p.get('product_name', 'Produit Inconnu')}\n({brand})"
                    
                    n = p.get("nutriments", {})
                    self.nutrition_data = {
                        "calories": n.get('energy-kcal_100g', 0),
                        "glucides": n.get('sugars_100g', 0),
                        "proteins": n.get('proteins_100g', 0),
                        "salt": n.get('salt_100g', 0)
                    }
                    
                    # On construit uniquement la liste des nutriments (sans le titre Valeurs pour 100g)
                    self.nutrition_info = (
                        f"Énergie : {self.nutrition_data['calories']} kcal\n"
                        f"Sucres : {self.nutrition_data['glucides']} g\n"
                        f"Sel : {self.nutrition_data['salt']} g\n"
                        f"Protéines : {self.nutrition_data['proteins']} g"
                    )
                    self.save_to_backend(code)
        except Exception as e:
            print(f"Erreur fetch_details: {e}")

    def save_to_backend(self, code):
        payload = {
            "barcode": str(code), 
            "name": self.product_name, 
            "type": self.product_category,
            "brand": self.product_brand, 
            "calories": float(self.nutrition_data.get('calories', 0.0)),
            "glucides": float(self.nutrition_data.get('glucides', 0.0)),
            "proteins": float(self.nutrition_data.get('proteins', 0.0)),
            "lipids": 0.0, 
            "salt": float(self.nutrition_data.get('salt', 0.0)), 
            "calcium": 0.0
        }
        try:
            requests.post(f"{BACKEND_URL}/products/?id_child=1", json=payload, timeout=5)
        except: pass

    def build(self): 
        return WindowManager()

if __name__ == '__main__':
    PandooApp().run()
