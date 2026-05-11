import cv2
import urllib.request
import numpy as np
import requests
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.clock import Clock
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty
from pyzbar.pyzbar import decode
from kivy.lang import Builder

# --- CONFIGURATION ---
URL_IMAGE = "http://192.168.1.157:8080/shot.jpg"
MY_API_URL = "http://127.0.0.1:8000/products/"

Builder.load_string('''
<WindowManager>:
    ScanScreen:
    DetailsScreen:

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
            font_size: '20sp'
            bold: True

<DetailsScreen>:
    name: "details"
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        
        Label:
            text: app.product_name
            font_size: '24sp'
            bold: True
            size_hint_y: None
            height: '50dp'
            color: (0.2, 0.6, 1, 1)
            halign: 'center'
            valign: 'middle'
            text_size: self.width, None

        # --- LA CORRECTION : Ajout de la mention 100g ---
        Label:
            text: "Valeurs indiquées pour 100g"
            font_size: '14sp'
            italic: True
            color: (0.8, 0.8, 0.8, 1)
            size_hint_y: None
            height: '30dp'
            halign: 'center'

        GridLayout:
            cols: 2
            spacing: 10
            padding: 15
            canvas.before:
                Color:
                    rgba: (0.15, 0.15, 0.15, 1)
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [10,]
            
            # --- Lignes nutritionnelles ---
            Label:
                text: "Calories:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_energy
                text: "..."
                halign: 'right'
                text_size: self.size

            Label:
                text: "Glucides:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_glucides
                text: "..."
                halign: 'right'
                text_size: self.size

            Label:
                text: "Lipides:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_fat
                text: "..."
                halign: 'right'
                text_size: self.size

            Label:
                text: "Protéines:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_proteins
                text: "..."
                halign: 'right'
                text_size: self.size

            Label:
                text: "Sel:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_salt
                text: "..."
                halign: 'right'
                text_size: self.size

            Label:
                text: "Calcium:"
                bold: True
                halign: 'left'
                text_size: self.size
            Label:
                id: val_calcium
                text: "..."
                halign: 'right'
                text_size: self.size

        Button:
            text: "FERMER ET REVENIR AU SCAN"
            size_hint_y: None
            height: '65dp'
            background_color: (0.9, 0.2, 0.2, 1)
            background_normal: ''
            bold: True
            on_release: root.manager.current = "scan"
''')

class ScanScreen(Screen):
    def on_enter(self):
        app = App.get_running_app()
        app.status_text = "Prêt à scanner"
        self.last_scanned = None
        self.update_event = Clock.schedule_interval(self.update, 1.0 / 60.0)

    def on_leave(self):
        Clock.unschedule(self.update_event)

    def update(self, dt):
        try:
            img_resp = urllib.request.urlopen(URL_IMAGE, timeout=2)
            img_np = np.array(bytearray(img_resp.read()), dtype=np.uint8)
            frame = cv2.imdecode(img_np, -1)
            if frame is not None:
                barcodes = decode(frame)
                for barcode in barcodes:
                    code = barcode.data.decode('utf-8')
                    if code != self.last_scanned:
                        self.last_scanned = code
                        threading.Thread(target=self.process_new_scan, args=(code,)).start()
                
                buf = cv2.flip(frame, 0).tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buf, colorfmt='bgr', bufferfmt='ubyte')
                self.ids.camera_preview.texture = texture
        except:
            pass

    def process_new_scan(self, code):
        app = App.get_running_app()
        Clock.schedule_once(lambda dt: setattr(app, 'status_text', "RECHERCHE..."))
        
        try:
            headers = {'User-Agent': 'PandooApp - 1.0'}
            url = f"https://world.openfoodfacts.org/api/v2/product/{code}"
            res = requests.get(url, headers=headers, timeout=5)
            
            if res.status_code == 200:
                data = res.json()
                if data.get('status') == 1:
                    p = data.get('product', {})
                    nut = p.get('nutriments', {})
                    
                    payload = {
                        "barcode": int(code),
                        "type": "Alimentation",
                        "name": str(p.get('product_name_fr') or p.get('product_name') or "Article"),
                        "brand": str(p.get('brands', 'INCONNU').split(',')[0].strip()),
                        "calories": float(nut.get('energy-kcal_100g', 0.0)),
                        "glucides": float(nut.get('carbohydrates_100g', 0.0)),
                        "calcium": float(nut.get('calcium_100g', 0.0)),
                        "proteins": float(nut.get('proteins_100g', 0.0)),
                        "lipids": float(nut.get('fat_100g', 0.0)),
                        "salt": float(nut.get('salt_100g', 0.0))
                    }
                    
                    Clock.schedule_once(lambda dt: self.update_details_ui(payload))
                    Clock.schedule_once(lambda dt: self.switch_to_details())
                    self.send_to_backend(payload)
                else:
                    Clock.schedule_once(lambda dt: setattr(app, 'status_text', "Produit inconnu"))
        except Exception as e:
            print(f"Erreur: {e}")

    def update_details_ui(self, p):
        app = App.get_running_app()
        app.product_name = f"{p['brand'].upper()} - {p['name']}"
        
        ds = app.root.get_screen('details')
        ds.ids.val_energy.text = f"{p['calories']} kcal"
        ds.ids.val_glucides.text = f"{p['glucides']} g"
        ds.ids.val_fat.text = f"{p['lipids']} g"
        ds.ids.val_proteins.text = f"{p['proteins']} g"
        ds.ids.val_salt.text = f"{p['salt']} g"
        ds.ids.val_calcium.text = f"{p['calcium']} mg"

    def switch_to_details(self):
        self.manager.current = "details"

    def send_to_backend(self, data):
        try:
            target_url = "http://127.0.0.1:8000/products/?id_child=1"
            res = requests.post(target_url, json=data, timeout=5)
            
            if res.status_code == 200:
                # Le backend renvoie le produit (existant ou nouveau)
                server_data = res.json()
                
                # On peut vérifier si le message de log du backend contenait "déjà existant"
                # Ou plus simplement, si le backend est configuré pour renvoyer 200, 
                # on affiche un message clair ici.
                
                # Pour un affichage précis, on se base sur la logique du backend :
                print(f"--- [API INFO] ---")
                print(f"Produit : {data['name']}")
                # On affiche le message de succès uniquement
                print(f"✅ Opération réussie (Article déjà stocké dans l'API)")
            
            # Note : Si tu veux un message "DÉJÀ ENREGISTRÉ" spécifique dans Kivy,
            # il est préférable que le Backend renvoie un code 201 pour "créé" 
            # et 200 pour "déjà présent".
        except Exception as e:
            print(f"❌ Backend injoignable : {e}")

class DetailsScreen(Screen): pass
class WindowManager(ScreenManager): pass

class PandooApp(App):
    product_name = StringProperty("")
    status_text = StringProperty("Prêt à scanner")
    
    def build(self):
        return WindowManager()

if __name__ == '__main__':
    PandooApp().run()