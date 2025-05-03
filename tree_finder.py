import pyautogui
import time
import random
import os
from datetime import datetime
from scanner import ImageScanner
from tree import TreeFactory

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ieškoma medžių: {', '.join(available_tree_types)} (sukama kol randama)")
    while True:
        temp_tree_types = list(available_tree_types)
        random.shuffle(temp_tree_types)
        for tree_type in temp_tree_types:
            try:
                tree = TreeFactory.create_tree(tree_type)
                for image_path in tree.image_paths:
                    pos = scanner.find_on_screen(image_path, confidence=confidence)
                    if pos:
                        print(f"Rastas {tree.name} ({os.path.basename(image_path)}) pozicijoje {pos}!")
                        return pos, tree_type
            except FileNotFoundError:
                 continue
            except ValueError as e:
                 print(f"Klaida gaunant medžio '{tree_type}' informaciją: {e}")
                 continue
            except Exception as e:
                 print(f"Netikėta klaida ieškant medžio tipo {tree_type}: {e}")
                 continue

        print("Nerasta šiame vaizde. Sukamas vaizdas ir bandoma vėl...")
        rotate_view()
        time.sleep(random.uniform(0.5, 1.5))

def verify_tree_location(scanner: ImageScanner, tree_spot: tuple, tree_type: str, confidence: float, region_size: int = 180):
    if not tree_spot or not tree_type:
        return False
    try:
        tree_obj = TreeFactory.create_tree(tree_type)
        x, y = tree_spot
        region = (
            max(0, x - region_size // 2),
            max(0, y - region_size // 2),
            region_size, region_size )
        for image_path in tree_obj.image_paths:
            if scanner.find_on_screen(image_path, region=region, confidence=confidence):
                return True
        return False
    except (FileNotFoundError, ValueError) as e:
        print(f"Klaida tikrinant medžio vietą ({tree_type}): {e}")
        return False
    except Exception as e:
        print(f"Netikėta klaida tikrinant medžio vietą: {e}")
        return False

def chop_action(pos, tree_type):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Bandoma kirsti {tree_type} ties {pos}")
    try:
        screen_w, screen_h = pyautogui.size()
        if not (0 <= pos[0] < screen_w and 0 <= pos[1] < screen_h):
            print(f"KLAIDA: Bandymas paspausti už ekrano ribų: {pos}")
            return False
        pyautogui.moveTo(pos[0], pos[1], duration=random.uniform(0.2, 0.5))
        pyautogui.click()
        time.sleep(random.uniform(1.0, 2.0))
        return True
    except Exception as e:
        print(f"Klaida atliekant paspaudimą (chop_action): {e}")
        return False

def rotate_view():
    print("Sukamas vaizdas...")
    try:
        key = random.choice(['left', 'right', 'up', 'down'])
        duration = random.uniform(0.4, 1.0)
        pyautogui.keyDown(key)
        time.sleep(duration)
        pyautogui.keyUp(key)
        print(f"Paspausta rodyklė: '{key}' ({duration:.2f}s)")
    except Exception as e:
        print(f"Klaida sukant vaizdą: {e}")