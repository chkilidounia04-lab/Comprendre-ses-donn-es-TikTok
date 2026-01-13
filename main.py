import json
import pandas as pd
import matplotlib.pyplot as plt
import os

class TikTokMirror:
    def __init__(self):
        # LA BOUSSOLE : Trouve le dossier du script automatiquement pour éviter les erreurs de chemin
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_folder = os.path.join(self.script_dir, 'data')
        self.all_videos = []
        self.all_searches = []
        self.all_comments = []

    def find_key_recursive(self, obj, target_key):
        """Fonction récursive."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k == target_key:
                    return v
                res = self.find_key_recursive(v, target_key)
                if res is not None:
                    return res
        elif isinstance(obj, list):
            for item in obj:
                res = self.find_key_recursive(item, target_key)
                if res is not None:
                    return res
        return None

    def load_data(self):
        """Charge et nettoie les données provenant du dossier 'data'."""
        if not os.path.exists(self.data_folder):
            print(f" Erreur : Crée un dossier nommé 'data' à côté de ce fichier.")
            return

        files = [f for f in os.listdir(self.data_folder) if f.endswith('.json')]
        if not files:
            print(f" Aucun fichier .json trouvé dans {self.data_folder}")
            return

        for filename in files:
            print(f" Analyse de {filename}...")
            with open(os.path.join(self.data_folder, filename), 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    
                    # Extraction par force brute (Récursivité)
                    v_list = self.find_key_recursive(data, 'VideoList')
                    s_list = self.find_key_recursive(data, 'SearchList')
                    c_list = self.find_key_recursive(data, 'CommentsList')

                    if v_list:
                        for v in v_list:
                            self.all_videos.append({'Timestamp': v.get('Date') or v.get('date')})
                    if s_list:
                        for s in s_list:
                            self.all_searches.append({
                                'Term': s.get('SearchTerm') or s.get('searchTerm'),
                                'Timestamp': s.get('Date') or s.get('date')
                            })
                    if c_list:
                        for c in c_list:
                            self.all_comments.append({'Text': c.get('comment')})
                except Exception as e:
                    print(f" Erreur lors de la lecture du fichier {filename}: {e}")

        # --- C'EST ICI QUE LA MAGIE OPÈRE ---
        # On transforme les listes en Tableaux Pandas et on enlève les doublons
        if self.all_videos:
            self.video_df = pd.DataFrame(self.all_videos).drop_duplicates()
        if self.all_searches:
            self.search_df = pd.DataFrame(self.all_searches).drop_duplicates()
        if self.all_comments:
            self.comment_df = pd.DataFrame(self.all_comments).drop_duplicates()

        print(f" Succès ! {len(self.all_videos)} vidéos chargées (Doublons ignorés).")

    def run_analysis(self):
        """toutes les analyses graphiques."""
        if not self.all_videos:
            print(" Aucune donnée vidéo trouvée. Vérifiez le fichier JSON.")
            return

        # 1. Analyse Addiction (Heures)
        df_v = pd.DataFrame(self.all_videos).dropna()
        df_v['Timestamp'] = pd.to_datetime(df_v['Timestamp'])
        df_v['Heure'] = df_v['Timestamp'].dt.hour
        
        plt.figure(figsize=(12, 6))
        df_v['Heure'].value_counts().sort_index().plot(kind='bar', color='#ff0050') 
        plt.title("Mon Horloge Biologique TikTok (Vidéos vues par heure)")
        plt.xlabel("Heure de la journée (0h - 23h)")
        plt.ylabel("Nombre de vidéos")
        plt.savefig(os.path.join(self.script_dir, 'mon_addiction.png'))
        print(" Graphique 'mon_addiction.png' ")

        # 2. Analyse Thèmes (Commentaires & Recherches)
        words_to_track = ['Tea', 'Love','Dubai', 'Food', 'Skincare', 'Etude', 'Economie', 'drama']
        combined_text = " ".join([str(c['Text']) for c in self.all_comments]) + " " + \
                        " ".join([str(s['Term']) for s in self.all_searches])
        
        counts = {w: combined_text.lower().count(w.lower()) for w in words_to_track}
        
        plt.figure(figsize=(12, 6))
        plt.bar(counts.keys(), counts.values(), color='#00f2ea') # Deuxième couleur TikTok
        plt.title("Les Thèmes de Prédilection (Basé sur recherches et commentaires)")
        plt.ylabel("Occurrences")
        plt.savefig(os.path.join(self.script_dir, 'mes_themes.png'))
        print(" Graphique 'mes_themes.png' généré !")

        # 3. Analyse Sentiment
        self.analyze_sentiment()

if __name__ == "__main__":
    app = TikTokMirror()
    app.load_data()
    app.run_analysis()
    print(f"\n Les 3 graphiques sont prêts.")
