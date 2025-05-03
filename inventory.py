import pyautogui
import time
import random
import os
from datetime import datetime
from scanner import ImageScanner

def is_inventory_full(scanner: ImageScanner, template_path: str, confidence: float) -> bool:
    found = scanner.find_on_screen(template_path, confidence=confidence)
    return found is not None

def is_inventory_empty(scanner: ImageScanner, template_path: str, confidence: float) -> bool:
    found = scanner.find_on_screen(template_path, confidence=confidence)
    return found is not None

def drop_all_logs(scanner: ImageScanner, log_templates: list, inventory_region: tuple, confidence: float) -> tuple[bool, int]:
    print(f"--- [{datetime.now().strftime('%H:%M:%S')}] Išmetami rąstai ---")

    if not (isinstance(inventory_region, tuple) and len(inventory_region) == 4):
        print(f"KLAIDA: Neteisingas inventoriaus regiono formatas: {inventory_region}. Naudojamas visas ekranas.")
        inventory_region = None
    else:
        print(f"Naudojamas inventoriaus regionas rąstų paieškai: {inventory_region}")

    found_any_logs = False
    total_dropped_in_cycle = 0
    shift_pressed = False

    try:
        for log_template in log_templates:
            try:
                locations = scanner.locate_all_on_screen(
                    log_template,
                    region=inventory_region,
                    confidence=confidence
                )

                if locations:
                    log_filename = os.path.basename(log_template)
                    print(f"Rasta {len(locations)} rąstų pagal '{log_filename}'. Metama...")
                    found_any_logs = True
                    logs_dropped_this_type = 0
                    for box in locations:
                        try:
                            log_pos = pyautogui.center(box)
                            pyautogui.moveTo(log_pos, duration=random.uniform(0.05, 0.15))
                            if not shift_pressed:
                                pyautogui.keyDown('shift')
                                shift_pressed = True
                                time.sleep(random.uniform(0.05, 0.1))
                            pyautogui.click()
                            time.sleep(random.uniform(0.05, 0.1))
                            logs_dropped_this_type += 1
                            total_dropped_in_cycle += 1
                            time.sleep(random.uniform(0.1, 0.25))
                        except Exception as inner_e:
                            print(f"Klaida metant konkretų rąstą ties {box}: {inner_e}")
                            if shift_pressed:
                                try: pyautogui.keyUp('shift'); shift_pressed = False
                                except: pass
                    print(f"  Išmesta {logs_dropped_this_type} vnt. '{log_filename}'.")

            except Exception as e:
                print(f"Klaida ieškant ar metant rąstus ({os.path.basename(log_template)}): {e}")
                if shift_pressed:
                   try: pyautogui.keyUp('shift'); shift_pressed = False
                   except: pass

        if shift_pressed:
           try: pyautogui.keyUp('shift'); shift_pressed = False
           except: pass

        if not found_any_logs:
            print("Inventoriuje nerasta jokių atpažįstamų rąstų nurodytame regione.")

        print(f"Išmetimo ciklas baigtas. Išmesta šiame cikle: {total_dropped_in_cycle}.")
        return True, total_dropped_in_cycle

    finally:
         if shift_pressed:
            try: pyautogui.keyUp('shift')
            except: pass