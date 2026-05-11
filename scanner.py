import cv2
from pyzbar import pyzbar

class BarcodeScanner:
    @staticmethod
    def scan(frame):
        """
        Détecte un code-barres dans une image (frame) 
        et renvoie le numéro sous forme de texte.
        """
        # On décode les codes-barres présents dans l'image
        barcodes = pyzbar.decode(frame)
        
        for barcode in barcodes:
            # On extrait les données et on les transforme en texte
            barcode_data = barcode.data.decode("utf-8")
            return barcode_data
            
        return None
    