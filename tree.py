import os
from abc import ABC, abstractmethod

class Tree(ABC):
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths if isinstance(image_paths, list) else [image_paths]

    @abstractmethod
    def required_level(self):
        pass

class NormalTree(Tree):
    def required_level(self): return 1

class OakTree(Tree):
    def required_level(self): return 15

class TreeFactory:
    base_path = "C:/Users/Ruslan/Desktop/BOTAS" # Visada patikrinti ar geras destinationas

    @staticmethod
    def create_tree(tree_type):
        if not os.path.exists(TreeFactory.base_path):
            print(f"KLAIDA: Nurodytas bazinis kelias paveikslėliams neegzistuoja: {TreeFactory.base_path}")
            raise FileNotFoundError(f"Bazinis kelias nerastas: {TreeFactory.base_path}")

        mapping = {
            "normal": NormalTree("Normal Tree", [
                os.path.join(TreeFactory.base_path, "tree.png"),
                os.path.join(TreeFactory.base_path, "tree_v1.png"),
                os.path.join(TreeFactory.base_path, "tree_v2.png"),
                os.path.join(TreeFactory.base_path, "tree_v3.png"),
                os.path.join(TreeFactory.base_path, "tree_v4.png"),
                os.path.join(TreeFactory.base_path, "tree_v5.png")
            ]),
            "oak": OakTree("Oak Tree", [
                os.path.join(TreeFactory.base_path, "oak.png"),
                os.path.join(TreeFactory.base_path, "oak_v1.png"),
                os.path.join(TreeFactory.base_path, "oak_v2.png"),
                os.path.join(TreeFactory.base_path, "oak_v3.png"),
                os.path.join(TreeFactory.base_path, "oak_v4.png"),
                os.path.join(TreeFactory.base_path, "oak_v5.png")
            ]),
        }
        if tree_type in mapping:
            tree_instance = mapping[tree_type]
            all_paths_exist = True
            for path in tree_instance.image_paths:
                if not os.path.exists(path):
                    print(f"KLAIDA: Medžio '{tree_type}' paveikslėlis nerastas kelyje: {path}")
                    all_paths_exist = False
            if not all_paths_exist:
                raise FileNotFoundError(f"Trūksta vieno ar daugiau paveikslėlių medžiui '{tree_type}'")
            return tree_instance
        raise ValueError(f"Unknown tree type: {tree_type}")

    @staticmethod
    def check_required_files(base_path, required_files):
         print("Tikrinami reikalingi paveikslėlių failai...")
         all_files_ok = True
         for filename in required_files:
             filepath = os.path.join(base_path, filename)
             if not os.path.exists(filepath):
                 print(f"KLAIDA: Trūkstamas failas: {filepath}")
                 all_files_ok = False
         if not all_files_ok:
             raise FileNotFoundError("Trūksta vieno ar daugiau reikalingų paveikslėlių failų.")
         print("Visi reikalingi failai rasti.")
