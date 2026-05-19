# class NutritionFormatter:
#     ''' @staticmethod
#     def get_summary(data):
#         """ Extrait les valeurs clés du dictionnaire 'nutriments' de l'API """
#         nutriments = data.get('nutriments', {})
        
#         # On récupère les valeurs en g/100g, avec '??' si la donnée manque
#         return {
#             "energy": nutriments.get('energy-kcal_100g', '??'),
#             "fat": nutriments.get('fat_100g', '??'),
#             "sugar": nutriments.get('sugars_100g', '??'),
#             "salt": nutriments.get('salt_100g', '??'),
#             "proteins": nutriments.get('proteins_100g', '??')
#         } 

#     @staticmethod
#     def get_display_text(summary):
#         """ Formate les données pour l'affichage dans l'interface Kivy """
#         return (
#             f"--- Valeurs pour 100g ---\n\n"
#             f"🔥 Énergie : {summary['energy']} kcal\n"
#             f"🧪 Matières grasses : {summary['fat']} g\n"
#             f"🍭 Sucres : {summary['sugar']} g\n"
#             f"💪 Protéines : {summary['proteins']} g\n"
#             f"🧂 Sel : {summary['salt']} g"
#         ) 