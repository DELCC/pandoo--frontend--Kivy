import requests
import webbrowser
from kivy.config import Config

# --- CONFIGURATION DE LA FENÊTRE ---
Config.set('graphics', 'width', '433')
Config.set('graphics', 'height', '650')
Config.set('graphics', 'resizable', False)

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import StringProperty

# Importation de nos composants et clients réseaux personnalisés
import backend_client
import screens

class WindowManager(ScreenManager):
    pass

class PandooApp(App):
    product_name = StringProperty("Chargement...")
    
    # --- PROPRIÉTÉS INDIVIDUELLES POUR ÉVITER LES BUGS DE LIAISON KV ---
    val_glucides = StringProperty("0.0 g")
    c_glucides = StringProperty("ffffff")
    
    val_proteines = StringProperty("0.0 g")
    c_proteines = StringProperty("ffffff")
    
    val_sucres = StringProperty("0.0 g")
    c_sucres = StringProperty("ffffff")
    
    val_lipides = StringProperty("0.0 g")
    c_lipides = StringProperty("ffffff")
    
    val_fibres = StringProperty("0.0 g")
    c_fibres = StringProperty("ffffff")
    
    val_energie = StringProperty("0 kcal")
    c_energie = StringProperty("22cc22")
    
    pandoo_advice = StringProperty("Analyse en cours...")
    product_allergens = StringProperty("Aucun")
    status_text = StringProperty("Scannez un produit")
    
    user_id = 0 
    active_child_id = 1
    active_child_birthdate = "2020-01-01"
    active_child_allergies = StringProperty("")

    TRANSLATIONS = {"Milk": "Lait", "Nuts": "Noisettes", "Eggs": "Œufs", "Peanuts": "Arachides", "Soybeans": "Soja", "Wheat": "Blé", "Hazelnuts": "Noisettes"}

    def open_google_search(self):
        query = self.product_name.replace("\n", " ").replace(" ", "+")
        webbrowser.open(f"https://www.google.com/search?q={query}")

    def save_to_backend(self, code):
        headers = {'User-Agent': 'PandooApp - Python/Kivy'}
        try:
            url_off = f"https://world.openfoodfacts.org/api/v0/product/{code}.json"
            res_off = requests.get(url_off, headers=headers, timeout=5)
            
            if res_off.status_code == 200 and res_off.json().get("status") == 1:
                p = res_off.json()["product"]
                n = p.get("nutriments", {})
                self.product_name = p.get('product_name', 'Produit inconnu')
                
                all_text = p.get('allergens_from_ingredients', '') or p.get('allergens', '')
                raw_items = all_text.replace("en:", "").replace("fr:", "").split(",")
                clean_list = []
                for item in raw_items:
                    name = item.strip().capitalize()
                    if name:
                        translated = self.TRANSLATIONS.get(name, name)
                        if translated not in clean_list: clean_list.append(translated)
                
                final_allergens = [a for a in clean_list if not (a == "Nuts" and "Noisettes" in clean_list or a == "Milk" and "Lait" in clean_list)]
                self.product_allergens = ", ".join(sorted(final_allergens)) if final_allergens else "Aucun allergène détecté"

                val_kcal = float(n.get('energy-kcal_100g', 0))
                val_sucre = round(float(n.get('sugars_100g', 0)), 2)
                val_sel = round(float(n.get('salt_100g', 0)), 2)
                val_lip = round(float(n.get('fat_100g', 0)), 2)
                val_glu = round(float(n.get('carbohydrates_100g', 0)), 2)
                val_fib = round(float(n.get('fiber_100g', 0)), 2)
                val_prot = round(float(n.get('proteins_100g', 0)), 2)
                val_calcium = round(float(n.get('calcium_100g', 0)), 3)

                def get_c(v, s_e, s_o, reverse=False):
                    if not reverse:
                        return "22cc22" if v <= s_e else "ff9900" if v <= s_o else "ff3333"
                    return "22cc22" if v >= s_e else "ff9900" if v >= s_o else "ff3333"

                c_suc, c_sel = get_c(val_sucre, 5.0, 13.5), get_c(val_sel, 0.3, 0.9)
                c_lip, c_glu = get_c(val_lip, 3.0, 20.0), get_c(val_glu, 30.0, 50.0)
                c_prot, c_fib = get_c(val_prot, 8.0, 4.0, reverse=True), get_c(val_fib, 5.0, 2.5, reverse=True)

                if val_sucre > 13.5 and val_sel > 0.9:
                    self.pandoo_advice = "[color=ff3333]• Ce produit est beaucoup trop riche en sucre ET en sel ![/color]"
                elif val_sucre > 13.5:
                    self.pandoo_advice = "[color=ff3333]• Dans un fruit, le sucre vient avec plein de vitamines. C'est le sucre champion ![/color]"
                elif val_sel > 0.9:
                    self.pandoo_advice = "[color=ff3333]• Manger moins de sel, c'est le secret pour ton petit cœur ![/color]"
                elif val_fib < 2.5:
                    self.pandoo_advice = "[color=ff9900]• Ce produit manque de fibres, amies de ton ventre ![/color]"
                else:
                    self.pandoo_advice = "[color=22cc22]Ce produit semble équilibré pour petit Pandoo ![/color]"

                # --- MISE À JOUR EN DIRECT DES STRINGPROPERTY POUR LE FICHIER KV ---
                self.val_glucides = f"{val_glu:.1f} g"
                self.c_glucides = c_glu
                
                self.val_proteines = f"{val_prot:.1f} g"
                self.c_proteines = c_prot
                
                self.val_sucres = f"{val_sucre:.1f} g"
                self.c_sucres = c_suc
                
                self.val_lipides = f"{val_lip:.1f} g"
                self.c_lipides = c_lip
                
                self.val_fibres = f"{val_fib:.1f} g"
                self.c_fibres = c_fib
                
                self.val_energie = f"{int(val_kcal)} kcal"
                self.c_energie = "22cc22"
                
                product_data = {
                    "barcode": int(code), "name": str(self.product_name),
                    "brand": str(p.get('brands', 'Marque inconnue')), "type": str(p.get('categories', 'Aliment')),
                    "calories": float(val_kcal), "glucides": float(val_glu), "calcium": float(val_calcium),
                    "proteins": float(val_prot), "lipids": float(val_lip), "salt": float(val_sel),
                    "sugars": float(val_sucre), "fibers": float(val_fib),
                    "id_child": int(self.active_child_id)  # <-- AJOUT : L'ID de l'enfant est maintenant inclus dans le JSON envoyé
                }
                
                # Envoi au backend : l'ID de l'enfant est également conservé en paramètre d'URL (selon ta route actuelle)
                res = requests.post(f"{backend_client.BACKEND_URL}/products/?id_child={self.active_child_id}", json=product_data, timeout=5)
                return res
            else:
                self.pandoo_advice = "Erreur de connexion."
        except:
            self.pandoo_advice = "Erreur de connexion."

    def build(self):
        return WindowManager()

if __name__ == '__main__':
    PandooApp().run()