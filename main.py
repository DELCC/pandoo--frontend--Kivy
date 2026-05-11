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
URL_IMAGE = "http://192.168.1.157:8080/shot.jpg"

Builder.load_string('''
<WindowManager>:
    StartScreen:
    CreateUserScreen:
    AddChildScreen:
    ScanScreen:
    DetailsScreen:

<StartScreen>:
    name: "start"
    BoxLayout:
        orientation: 'vertical'
        padding: 40
        spacing: 20
        canvas.before:
            Color:
                rgba: (0.1, 0.1, 0.1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "PANDOO 🐼"
            font_size: '48sp'
            bold: True
            color: (0.2, 0.8, 0.4, 1)
            size_hint_y: 0.4
        Button:
            text: "SE CONNECTER"
            size_hint_y: None
            height: '60dp'
            background_color: (0.2, 0.6, 1, 1)
            on_release: root.manager.current = "scan"
        Button:
            text: "CRÉER UN COMPTE"
            size_hint_y: None
            height: '60dp'
            background_color: (1, 1, 1, 0.1)
            on_release: root.manager.current = "create_user"

<CreateUserScreen>:
    name: "create_user"
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.1, 0.1, 0.1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "INSCRIPTION PARENT"
            font_size: '22sp'
            bold: True
        TextInput:
            id: name_input
            hint_text: "Nom"
            multiline: False
        TextInput:
            id: email_input
            hint_text: "Email"
            multiline: False
        TextInput:
            id: password_input
            hint_text: "Mot de passe"
            password: True
            multiline: False
        Label:
            id: error_label
            text: ""
            color: (1, 0.3, 0.3, 1)
        Button:
            text: "SUIVANT"
            size_hint_y: None
            height: '60dp'
            background_color: (0.2, 0.8, 0.4, 1)
            on_release: root.register_user()

<AddChildScreen>:
    name: "add_child"
    BoxLayout:
        orientation: 'vertical'
        padding: 30
        spacing: 15
        canvas.before:
            Color:
                rgba: (0.1, 0.1, 0.1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: "PROFIL ENFANT"
            bold: True
        TextInput:
            id: child_name
            hint_text: "Prénom enfant"
        TextInput:
            id: child_age
            hint_text: "Âge"
            input_filter: 'int'
        Label:
            id: child_error
            text: ""
            color: (1, 0.3, 0.3, 1)
        Button:
            text: "TERMINER"
            on_release: root.create_child()

<ScanScreen>:
    name: "scan"
    BoxLayout:
        orientation: 'vertical'
        Image:
            id: camera_preview
            size_hint_y: 0.8
        Label:
            text: app.status_text
            size_hint_y: 0.2
            bold: True

<DetailsScreen>:
    name: "details"
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        canvas.before:
            Color:
                rgba: (0.1, 0.1, 0.1, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: app.product_name
            font_size: '24sp'
            bold: True
            color: (0.2, 0.8, 0.4, 1)
            size_hint_y: None
            height: '50dp'
        ScrollView:
            Label:
                text: app.nutrition_info
                size_hint_y: None
                height: self.texture_size[1]
                text_size: self.width, None
                halign: 'center'
        Button:
            text: "RETOUR"
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
            if res.status_code == 200: self.manager.current = "scan"
        except: self.ids.child_error.text = "Erreur enfant"

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

class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class PandooApp(App):
    product_name = StringProperty("Produit")
    nutrition_info = StringProperty("")
    status_text = StringProperty("Prêt pour le scan")
    user_id = None

    def fetch_details(self, code):
        # ON AJOUTE UN HEADER POUR ÉVITER L'ERREUR 403
        headers = {'User-Agent': 'PandooApp - Android - Version 1.0 - contact@pandoo.com'}
        
        try:
            url = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res = requests.get(url, headers=headers, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if data.get("status") == 1:
                    p = data["product"]
                    n = p.get("nutriments", {})
                    self.product_name = p.get("product_name", "Inconnu")
                    self.nutrition_info = (
                        f"⚡ Calories : {n.get('energy-kcal_100g', 'N/A')} kcal\n"
                        f"🍭 Sucres : {n.get('sugars_100g', 'N/A')} g\n"
                        f"🧂 Sel : {n.get('salt_100g', 'N/A')} g\n"
                        f"🥩 Protéines : {n.get('proteins_100g', 'N/A')} g"
                    )
                else:
                    self.product_name = "Non trouvé"
                    self.nutrition_info = "Code inconnu d'OpenFoodFacts."
            else:
                self.product_name = f"Erreur {res.status_code}"
                self.nutrition_info = "Accès refusé par OpenFoodFacts."
        except Exception as e:
            self.nutrition_info = f"Erreur de connexion : {e}"

    def build(self):
        return WindowManager()

if __name__ == '__main__':
    PandooApp().run()