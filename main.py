import cv2
import urllib.request
import numpy as np
import requests
import json
import webbrowser
import re  # Ajout pour la validation du mot de passe
from kivy.config import Config

# --- CONFIGURATION DE LA FENÊTRE ---
Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '650')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
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
    ChildListScreen:
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
            rgba: (0.15, 0.75, 0.5, 0.9) if self.state == 'normal' else (0.1, 0.6, 0.4, 1)
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [25,]

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
                padding: [10, 15, 10, 0]
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
                        id: new_pass
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
                        on_release: new_pass.password = not new_pass.password
                        Image:
                            source: 'eye_off.png' if new_pass.password else 'eye_on.png'
                            size_hint: None, None
                            size: '22dp', '22dp'
                            opacity: 0.6
                
                # Rectangle d'erreur arrondi
                BoxLayout:
                    size_hint_y: None
                    height: '65dp' if root.error_msg else '0dp'
                    opacity: 1 if root.error_msg else 0
                    padding: [15, 5]
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 0.95)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [15,]
                    Label:
                        text: root.error_msg
                        color: (0.9, 0.2, 0.2, 1)
                        font_size: '12sp'
                        bold: True
                        halign: 'center'
                        valign: 'middle'
                        text_size: self.width - 30, None

                RoundedButton:
                    text: "VALIDER"
                    size_hint_y: None
                    height: '60dp'
                    on_release: root.validate_and_create()
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
                padding: [10, 40, 10, 40]
                spacing: 15
                Label:
                    text: "CONNEXION"
                    font_size: '36sp'
                    bold: True
                    size_hint_y: None
                    height: '80dp'
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
                            source: 'eye_off.png' if login_pass.password else 'eye_on.png'
                            size_hint: None, None
                            size: '22dp', '22dp'
                            opacity: 0.6
                RoundedButton:
                    text: "ENTRER"
                    size_hint_y: None
                    height: '60dp'
                    on_release: root.login_user()
                Button:
                    text: "SE CONNECTER AVEC GOOGLE"
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

<AddChildScreen>:
    name: "add_child"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [40, 60]
            spacing: 20
            Label:
                text: "AJOUTER UN ENFANT"
                font_size: '28sp'
                bold: True
            BaseInput:
                id: child_name
                hint_text: "Prénom"
            BaseInput:
                id: child_age
                hint_text: "Âge"
            RoundedButton:
                text: "AJOUTER"
                size_hint_y: None
                height: '60dp'
                on_release: root.create_child(more=True)
            Button:
                text: "VOIR MA LISTE"
                size_hint_y: None
                height: '40dp'
                background_color: (0,0,0,0)
                color: (1,1,1,1)
                underline: True
                on_release: root.create_child(more=False)

<ChildListScreen>:
    name: "child_list"
    RelativeLayout:
        BackgroundLayer:
        BoxLayout:
            orientation: 'vertical'
            padding: [30, 20]
            spacing: 20
            AnchorLayout:
                anchor_x: 'left'
                size_hint_y: None
                height: '60dp'
                BackButton:
                    on_release: root.manager.current = "start"
            Label:
                text: "QUI VA MANGER ?"
                font_size: '28sp'
                bold: True
                size_hint_y: None
                height: '60dp'
            ScrollView:
                BoxLayout:
                    id: container
                    orientation: 'vertical'
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 15
            RoundedButton:
                text: "+ AJOUTER UN ENFANT"
                size_hint_y: None
                height: '60dp'
                on_release: root.manager.current = "add_child"

<ScanScreen>:
    name: "scan"
    RelativeLayout:
        Image:
            id: camera_preview
            size_hint: (1, 1)
            pos_hint: {'center_x': 0.5, 'center_y': 0.5}
        Widget:
            canvas.after:
                Color:
                    rgba: (0.15, 0.75, 0.5, 0.5)
                Line:
                    width: 3
                    rounded_rectangle: (self.width*0.15, self.height*0.3, self.width*0.7, self.height*0.4, 20)
        Label:
            text: app.status_text
            size_hint: (1, 0.2)
            pos_hint: {'center_x': 0.5, 'y': 0}
            color: (0.15, 0.75, 0.5, 1)
            bold: True
            font_size: '18sp'
        AnchorLayout:
            anchor_x: 'left'
            anchor_y: 'top'
            padding: [20, 20]
            Button:
                text: "< Dernier Scan"
                size_hint: None, None
                size: '130dp', '45dp'
                background_color: (0,0,0,0)
                bold: True
                on_release: if app.product_name != "Chargement...": root.manager.current = "details"
                canvas.before:
                    Color:
                        rgba: (0.15, 0.75, 0.5, 0.7)
                    RoundedRectangle:
                        pos: self.pos
                        size: self.size
                        radius: [15,]

<DetailsScreen>:
    name: "details"
    RelativeLayout:
        BackgroundLayer:
        AnchorLayout:
            anchor_x: 'center'
            anchor_y: 'top'
            padding: [25, 40, 25, 0]
            BoxLayout:
                orientation: 'vertical'
                size_hint: (1, None)
                height: self.minimum_height
                spacing: 20
                Label:
                    text: "LE VERDICT DE PANDOO"
                    font_size: '26sp'
                    bold: True
                    color: (1, 1, 1, 1)
                    size_hint_y: None
                    height: '40dp'
                BoxLayout:
                    orientation: 'vertical'
                    size_hint: (1, None)
                    height: self.minimum_height
                    padding: [15, 20]
                    spacing: 10
                    canvas.before:
                        Color:
                            rgba: (1, 1, 1, 1)
                        RoundedRectangle:
                            pos: self.pos
                            size: self.size
                            radius: [20]
                    Label:
                        text: app.product_name
                        font_size: '18sp'
                        bold: True
                        color: (0.1, 0.1, 0.1, 1)
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.width, None
                        halign: 'center'
                    Label:
                        text: app.pandoo_advice
                        markup: True
                        font_size: '15sp'
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.width, None
                        halign: 'center'
                    Widget:
                        size_hint_y: None
                        height: '1dp'
                        canvas:
                            Color:
                                rgba: (0.15, 0.75, 0.5, 0.2)
                            Rectangle:
                                pos: self.x + 20, self.y
                                size: self.width - 40, self.height
                    Label:
                        text: app.nutrition_info
                        markup: True
                        font_size: '14sp'
                        color: (0.2, 0.2, 0.2, 1)
                        size_hint_y: None
                        height: self.texture_size[1]
                        text_size: self.width, None
                        halign: 'left'
        BoxLayout:
            orientation: 'vertical'
            size_hint: (0.85, None)
            height: '110dp'
            pos_hint: {'center_x': 0.5, 'y': 0.05}
            spacing: 12
            RoundedButton:
                text: "VOIR SUR GOOGLE"
                on_release: app.open_google_search()
            RoundedButton:
                text: "RETOUR AU SCANNER"
                on_release: root.manager.current = "scan"
''')

class BackButton(ButtonBehavior, BoxLayout): pass
class StartScreen(Screen): pass
class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class CreateUserScreen(Screen):
    error_msg = StringProperty("")

    def validate_and_create(self):
        username = self.ids.new_user.ids.ti.text.strip()
        email = self.ids.new_email.ids.ti.text.strip()
        password = self.ids.new_pass.text 
        
        if not username or not email or not password:
            self.error_msg = "Tous les champs sont obligatoires."
            return

        password_pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{10,}$"
        if not re.match(password_pattern, password):
            self.error_msg = "Le mot de passe doit contenir :\n10 caractères, 1 majuscule, 1 minuscule et 1 chiffre."
            return

        self.error_msg = ""
        # Le backend attend désormais 'username' explicitement
        payload = {"name": username, "username": username, "email": email, "password": password}
        
        try:
            res = requests.post(f"{BACKEND_URL}/users/", json=payload, timeout=5)
            
            # Gestion du doublon
            if res.status_code == 400:
                self.suggest_new_username(username)
            elif res.status_code in [200, 201]:
                user_data = res.json()
                # On s'adapte à la structure de réponse du backend
                new_id = user_data.get("user", {}).get("id") or user_data.get("id")
                App.get_running_app().user_id = new_id
                self.manager.current = "child_list" # Directement vers la liste après création
            else:
                self.error_msg = f"Erreur ({res.status_code})"
        except Exception as e: 
            self.error_msg = "Serveur injoignable."

    def suggest_new_username(self, base_name):
        """
        Analyse le nom pour incrémenter intelligemment.
        Ex: amo -> amo1, amo1 -> amo2, etc.
        """
        # On cherche si le nom finit déjà par des chiffres
        match = re.search(r"^(.*?)(\d+)$", base_name)
        
        if match:
            # Si on a "amo1", prefix="amo" et counter=2
            prefix = match.group(1)
            counter = int(match.group(2)) + 1
        else:
            # Si on a "amo", prefix="amo" et counter=1
            prefix = base_name
            counter = 1
            
        found = False
        new_suggestion = base_name
        
        # Teste les noms sur le serveur (ex: amo1, amo2...)
        while not found and counter < 100:
            temp_name = f"{prefix}{counter}"
            try:
                check = requests.get(f"{BACKEND_URL}/users/by-username/{temp_name}", timeout=2)
                if check.status_code == 404: 
                    new_suggestion = temp_name
                    found = True
                else:
                    counter += 1
            except:
                break
        
        if found:
            self.error_msg = f"Nom déjà pris. Essayez : {new_suggestion}"
            self.ids.new_user.ids.ti.text = new_suggestion
        else:
            self.error_msg = "Ce nom d'utilisateur est indisponible."

class LoginScreen(Screen):
    def login_user(self):
        username = self.ids.login_user.ids.ti.text.strip()
        if username:
            try:
                res = requests.get(f"{BACKEND_URL}/users/by-username/{username}", timeout=2)
                if res.status_code == 200:
                    user_data = res.json()
                    new_id = user_data.get("id")
                    App.get_running_app().user_id = new_id
                    self.manager.current = "child_list"
                else:
                    # Ici on pourrait ajouter un error_msg pour le login aussi
                    print("Utilisateur non trouvé")
            except Exception as e: print(f"Erreur de connexion : {e}")

    def login_with_google(self):
        webbrowser.open(f"{BACKEND_URL}/auth/login")
        self.check_event = Clock.schedule_interval(self.check_login_status, 2)

    def check_login_status(self, dt):
        try:
            email_to_check = "amaury.jacobe1@gmail.com"
            res = requests.get(f"{BACKEND_URL}/users/by-email/{email_to_check}", timeout=2)
            if res.status_code == 200:
                user_data = res.json()
                new_id = user_data.get("id")
                App.get_running_app().user_id = new_id
                Clock.unschedule(self.check_event)
                self.manager.current = "child_list"
        except: pass

class AddChildScreen(Screen):
    def create_child(self, more=True):
        name = self.ids.child_name.ids.ti.text
        age = self.ids.child_age.ids.ti.text
        parent_id = App.get_running_app().user_id
        if name and age and parent_id != 0:
            try:
                payload = {"name": name, "age": int(age), "id_parent": parent_id}
                res = requests.post(f"{BACKEND_URL}/children/", json=payload, timeout=5)
                if res.status_code in [200, 201]: 
                    self.ids.child_name.ids.ti.text = ""
                    self.ids.child_age.ids.ti.text = ""
            except: pass
        if not more: self.manager.current = "child_list"

class ChildListScreen(Screen):
    def on_enter(self):
        self.ids.container.clear_widgets()
        parent_id = App.get_running_app().user_id
        if parent_id == 0:
            self.manager.current = "start"
            return
        try:
            res = requests.get(f"{BACKEND_URL}/children/parent/{parent_id}", timeout=5)
            if res.status_code == 200:
                from kivy.uix.button import Button
                from kivy.graphics import Color, RoundedRectangle
                children = res.json()
                for child in children:
                    btn = Button(text=f"{child['name']} ({child['age']} ans)", size_hint_y=None, height='55dp', background_color=(0,0,0,0), color=(0.1, 0.1, 0.1, 1), bold=True)
                    with btn.canvas.before:
                        Color(1, 1, 1, 0.95)
                        btn.rect = RoundedRectangle(pos=btn.pos, size=btn.size, radius=[15,])
                    btn.bind(pos=self.update_rect, size=self.update_rect)
                    btn.bind(on_release=lambda x, c=child: self.select_child(c))
                    self.ids.container.add_widget(btn)
        except: pass

    def update_rect(self, instance, value):
        instance.rect.pos = instance.pos
        instance.rect.size = instance.size

    def select_child(self, child_data):
        App.get_running_app().active_child_id = child_data['id']
        self.manager.current = "scan"

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
                        App.get_running_app().save_to_backend(code)
                        self.manager.current = "details"
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.ids.camera_preview.texture = texture
        except: pass

class PandooApp(App):
    product_name = StringProperty("Chargement...")
    nutrition_info = StringProperty("")
    pandoo_advice = StringProperty("Analyse en cours...")
    status_text = StringProperty("Scannez un produit")
    user_id = 0 
    active_child_id = 1

    def open_google_search(self):
        query = self.product_name.replace("\n", " ").replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    def save_to_backend(self, code):
        headers = {'User-Agent': 'PandooApp - Python/Kivy'}
        try:
            url_off = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res_off = requests.get(url_off, headers=headers, timeout=5)
            
            if res_off.status_code == 200:
                data_off = res_off.json()
                if data_off.get("status") == 1:
                    p = data_off["product"]
                    n = p.get("nutriments", {})
                    
                    self.product_name = p.get('product_name', 'Produit inconnu')
                    val_kcal = int(n.get('energy-kcal_100g', 0))
                    val_sucre = round(float(n.get('sugars_100g', 0)), 2)
                    val_sel = round(float(n.get('salt_100g', 0)), 2)
                    val_lip = round(float(n.get('fat_100g', 0)), 2)
                    val_glu = round(float(n.get('carbohydrates_100g', 0)), 2)
                    val_fib = round(float(n.get('fiber_100g', 0)), 2)
                    val_prot = round(float(n.get('proteins_100g', 0)), 2)
                    val_calcium = round(float(n.get('calcium_100g', 0)), 3)

                    def get_c(v, s_e, s_o):
                        if v <= s_e: return "22cc22"
                        if v <= s_o: return "ff9900"
                        return "ff3333"

                    c_suc = get_c(val_sucre, 5.0, 13.5)
                    c_sel = get_c(val_sel, 0.3, 0.9)
                    c_lip = get_c(val_lip, 20.0, 35.0)

                    if val_sucre > 15.0:
                        self.pandoo_advice = "[color=ff3333]• Le sucre fatigue ton corps, choisis plutôt un fruit ![/color]"
                    elif val_calcium > 0.12:
                        self.pandoo_advice = "[color=22cc22]• Indispensable pour grandir et renforcer tes os.[/color]"
                    else:
                        self.pandoo_advice = "[color=22cc22]Ce produit semble équilibré pour petit Pandoo ![/color]"

                    self.nutrition_info = (
                        f"[b]Valeurs pour 100g :[/b]\n"
                        f"Énergie : {val_kcal} kcal\n"
                        f"Sucres : [color={c_suc}]{val_sucre:.2f}g[/color]  |  Sel : [color={c_sel}]{val_sel:.2f}g[/color]\n"
                        f"Lipides : [color={c_lip}]{val_lip:.2f}g[/color]  |  [color=3498db]Protéines : {val_prot:.2f}g[/color]\n"
                        f"[color=e67e22]Glucides : {val_glu:.2f}g[/color]  |  [color=9b59b6]Fibres : {val_fib:.2f}g[/color]"
                    )
                    
                    product_data = {
                        "barcode": str(code),
                        "name": self.product_name,
                        "brand": p.get('brands', 'Marque inconnue'),
                        "type": p.get('categories', 'Aliment'),
                        "calories": val_kcal,
                        "proteins": val_prot,
                        "glucides": val_glu,
                        "lipids": val_lip,
                        "salt": val_sel,
                        "sugars": val_sucre,
                        "fibers": val_fib,
                        "calcium": val_calcium
                    }
                    
                    res_backend = requests.post(
                        f"{BACKEND_URL}/products/?id_child={self.active_child_id}", 
                        json=product_data, 
                        timeout=5
                    )

        except Exception as e:
            print(f"Erreur API : {e}")
            self.pandoo_advice = "Erreur de connexion."

    def build(self): return WindowManager()

if __name__ == '__main__':
    PandooApp().run()