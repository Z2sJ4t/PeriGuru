from fuzzywuzzy import fuzz

from GUI.data_structure.Layout import load_coords_json

class ScreenFinder:
    def __init__(self):
        self.screen_texts = []

    def load_screen_texts(self, file_path):
        self.screen_texts = load_coords_json(file_path)

    def find_text(self, text):
        # text, x, y
        best_match = max(self.screen_texts, key=\
            lambda x: fuzz.ratio(text, x[0]))
        print(best_match)
        return best_match[1], best_match[2]