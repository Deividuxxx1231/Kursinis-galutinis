import pyautogui
import time
import random
import os
import traceback
from datetime import datetime, timedelta
# Removed unused math import

from tree import TreeFactory, Tree # Ensure Tree is imported if needed for type hinting or direct use
from scanner import ImageScanner
import inventory
import runtime_logger
import tree_finder

class WoodcuttingBot:
    def __init__(self):
        self.scanner = ImageScanner(confidence=0.65)
        self.base_path = TreeFactory.base_path

        required_files = {
            "full_inventory.png",
            "tree.png", "tree_v1.png", "tree_v2.png", "tree_v3.png", "tree_v4.png", "tree_v5.png",
            "oak.png", "oak_v1.png", "oak_v2.png", "oak_v3.png","oak_v4.png" , "oak_v5.png",
            "empty_inventory.png",
            "log_1.png",
            "log_2.png"
        }
        TreeFactory.check_required_files(self.base_path, required_files) # Assuming this handles FileNotFoundError

        self.full_inv_template = os.path.join(self.base_path, "full_inventory.png")
        self.empty_inv_template = os.path.join(self.base_path, "empty_inventory.png")

        self.log_templates = [
            os.path.join(self.base_path, "log_1.png"),
            os.path.join(self.base_path, "log_2.png")
        ]
        self.log_drop_confidence = 0.8

        self.tree_find_confidence = 0.55
        self.tree_verify_confidence = 0.4
        self.inventory_full_confidence = 0.93
        self.inventory_empty_confidence = 0.85
        self.default_confidence = 0.65

        self.inventory_region = self._calculate_inventory_region()

        self.available_tree_types = ["normal", "oak"]

        # --- NAUJA DALIS: Gauti vartotojo lygį ---
        self.woodcutting_level = self.ask_woodcutting_level()
        # --- NAUJOS DALIES PABAIGA ---

        self.selected_tree_types = self.ask_tree_choice() # Dabar naudos self.woodcutting_level

        self.total_logs_collected = runtime_logger.load_log_count() #
        print(f"Pradinis įkeltas malkų skaičius: {self.total_logs_collected}")

        self.start_time = datetime.now()
        self.pause_time = timedelta()
        self.pause_start = None
        self.max_runtime = timedelta(hours=4)
        self.tree_spot = None
        self.current_tree_type = None

    def _calculate_inventory_region(self):
        """
        Grąžina numatytąsias inventoriaus regiono koordinates ekrane.
        """
        base_inventory_region = (1680, 740, 190, 260)
        print(f"Naudojamas numatytasis inventoriaus regionas: {base_inventory_region}")
        time.sleep(0.5)
        return base_inventory_region

    # --- NAUJAS METODAS: Gauti vartotojo lygį ---
    def ask_woodcutting_level(self):
        """Prašo vartotojo įvesti woodcutting lygį ir jį validuoja."""
        while True:
            try:
                level_input = input("Įveskite savo Woodcutting lygį (1-99): ")
                level = int(level_input)
                if 1 <= level <= 99:
                    print(f"Jūsų Woodcutting lygis: {level}")
                    return level
                else:
                    print("Klaida: Lygis turi būti skaičius tarp 1 ir 99.")
            except ValueError:
                print("Klaida: Įveskite tik skaičių.")
            except Exception as e:
                print(f"Netikėta klaida įvedant lygį: {e}")
    # --- NAUJO METODO PABAIGA ---

    def ask_tree_choice(self):
        """
        Klausia vartotojo, kokius medžius kirsti, ir tikrina lygio reikalavimus.
        """
        print("\nPasirinkite medžius, kuriuos norite kirsti (atskirti kableliais, pvz.: 1,2):")
        available_options = {}
        for idx, tree_name in enumerate(self.available_tree_types):
            try:
                tree = TreeFactory.create_tree(tree_name) #
                required = tree.required_level() #
                print(f"{idx + 1}. {tree.name} (reikalingas lygis: {required})")
                available_options[idx + 1] = {'type': tree_name, 'name': tree.name, 'level': required}
            except ValueError as e:
                print(f"Klaida gaunant informaciją apie medį '{tree_name}': {e}")
            except FileNotFoundError as e:
                print(f"Klaida: {e}") # Handle missing tree images gracefully

        last_selected_str = ""
        try:
            with open("last_selected_trees.txt", "r", encoding='utf-8') as f:
                last_selected_str = f.read().strip()
            if last_selected_str:
                print(f"\nPaskutinis pasirinkimas buvo: {last_selected_str}")
                use_last = input("Naudoti paskutinį pasirinkimą? (t/n): ").lower()
                if use_last == 't':
                    last_selected_list = last_selected_str.split(',')
                    valid_last_selection = [t for t in last_selected_list if t in self.available_tree_types]

                    # --- NAUJA DALIS: Patikrinti paskutinio pasirinkimo lygį ---
                    can_use_last = True
                    if valid_last_selection:
                        for tree_type in valid_last_selection:
                             try:
                                 # Surandame medžio informaciją iš available_options pagal tipą
                                 tree_info = next((info for num, info in available_options.items() if info['type'] == tree_type), None)
                                 if tree_info and tree_info['level'] > self.woodcutting_level:
                                     print(f"Negalima naudoti paskutinio pasirinkimo: Jūsų lygis ({self.woodcutting_level}) per žemas medžiui '{tree_info['name']}' (reikia {tree_info['level']}).")
                                     can_use_last = False
                                     break # Užtenka vieno netinkamo medžio
                             except Exception as e:
                                 print(f"Klaida tikrinant paskutinio pasirinkimo lygį medžiui '{tree_type}': {e}")
                                 can_use_last = False # Saugumo sumetimais, jei įvyko klaida
                                 break
                    else:
                        can_use_last = False # Nėra galiojančių medžių paskutiniame pasirinkime
                    # --- NAUJOS DALIES PABAIGA ---

                    if valid_last_selection and can_use_last:
                        print(f"Naudojamas paskutinis pasirinkimas: {', '.join(valid_last_selection)}")
                        return valid_last_selection
                    elif not can_use_last and valid_last_selection:
                        print("Pasirinkite iš naujo.")
                    else:
                        print("Paskutinis pasirinkimas nebegalioja arba netinkamas jūsų lygiui, pasirinkite iš naujo.")

        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Klaida skaitant last_selected_trees.txt: {e}")

        # Jei nenaudojamas paskutinis pasirinkimas arba jis netinkamas
        while True:
            try:
                choice = input("Įveskite pasirinkimus (numerius, atskirtus kableliu): ")
                indexes = [int(i.strip()) for i in choice.split(",") if i.strip().isdigit()]
                selected_types = []
                invalid_level_trees = []
                all_choices_valid = True

                if not indexes:
                     print("Nieko neįvesta arba įvestis neteisinga. Bandykite dar kartą.")
                     continue

                for index in indexes:
                    if index in available_options:
                        option = available_options[index]
                        if option['level'] <= self.woodcutting_level:
                            selected_types.append(option['type'])
                        else:
                            invalid_level_trees.append(f"'{option['name']}' (reikia {option['level']})")
                            all_choices_valid = False
                    else:
                        print(f"Klaida: Neteisingas pasirinkimo numeris {index}.")
                        all_choices_valid = False
                        # Galima iškart nutraukti, jei vienas neteisingas
                        # break

                if not all_choices_valid:
                    if invalid_level_trees:
                        print(f"Klaida: Jūsų lygis ({self.woodcutting_level}) per žemas šiems medžiams: {', '.join(invalid_level_trees)}.")
                    print("Prašome pasirinkti medžius iš naujo.")
                    continue # Grįžta į ciklo pradžią ir klausia vėl

                if selected_types:
                     # Patikrinimas praėjo sėkmingai
                    try:
                        with open("last_selected_trees.txt", "w", encoding='utf-8') as f:
                            f.write(",".join(selected_types))
                        print(f"Pasirinkti medžiai: {', '.join(selected_types)}")
                        return selected_types
                    except IOError as e:
                        print(f"Klaida įrašant pasirinkimą į last_selected_trees.txt: {e}")
                        return selected_types # Grąžina pasirinkimą net jei nepavyko išsaugoti
                    except Exception as e:
                        print(f"Netikėta klaida įrašant pasirinkimą: {e}")
                        return selected_types
                else:
                    # Tai gali įvykti, jei buvo įvesti tik neteisingi numeriai, bet nebuvo lygio problemų
                    print("Nė vienas iš įvestų numerių nebuvo tinkamas. Bandykite dar kartą.")

            except ValueError:
                print("Netinkama įvestis. Įveskite skaičius atskirtus kableliu.")
            except Exception as e:
                print(f"Netikėta klaida renkantis medžius: {e}. Bandykite dar kartą.")

    # ... (likusi klasės dalis lieka nepakeista: start_pause, end_pause, run) ...
    def start_pause(self):
        if not self.pause_start:
            self.pause_start = datetime.now()

    def end_pause(self):
        if self.pause_start:
            elapsed_pause = datetime.now() - self.pause_start
            self.pause_time += elapsed_pause
            self.pause_start = None

    def run(self):
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Pradedamas Woodcutting Botas...")
        print(f"Jūsų Woodcutting lygis: {self.woodcutting_level}") # Pridėta lygio informacija
        print(f"Pasirinkti medžiai: {', '.join(self.selected_tree_types)}")
        print(f"Maksimalus veikimo laikas: {self.max_runtime}")
        print(f"Naudojamas inventoriaus regionas: {self.inventory_region}")

        print("\nTikrinama pradinė inventoriaus būsena...")
        time.sleep(1)
        initial_full = inventory.is_inventory_full(self.scanner, self.full_inv_template, self.inventory_full_confidence) #
        initial_empty = inventory.is_inventory_empty(self.scanner, self.empty_inv_template, self.inventory_empty_confidence) #

        if initial_full:
            print("Pradedant darbą inventorius yra PILNAS. Bandoma išmesti rąstus...")
            self.start_pause()
            success, dropped_count = inventory.drop_all_logs(self.scanner, self.log_templates, self.inventory_region, self.log_drop_confidence) #
            self.end_pause()
            if success and dropped_count > 0:
                 self.total_logs_collected += dropped_count
                 runtime_logger.save_log_count(self.total_logs_collected) #
                 time.sleep(1)
                 if inventory.is_inventory_full(self.scanner, self.full_inv_template, self.inventory_full_confidence): #
                      print("Inventorius vis dar pilnas po bandymo išmesti. Botas stabdomas.")
                      return
                 else:
                      print("Rąstai išmesti. Tęsiama.")
            elif success and dropped_count == 0:
                 print("Inventorius atrodė pilnas, bet nerasta rąstų išmetimui. Tęsiama atsargiai.")
            else:
                 print("Nepavyko išmesti rąstų pradedant. Botas stabdomas.")
                 return
        elif initial_empty:
            print("Pradedant darbą inventorius yra TUŠČIAS.")
        else:
            print("Pradedant darbą inventorius yra dalinai užpildytas (arba nepilnai atpažintas).")


        # Main loop
        try:
            while True:
                # Check runtime limit
                active_runtime = (datetime.now() - self.start_time) - self.pause_time
                if active_runtime > self.max_runtime:
                    print(f"Botas pasiekė maksimalų AKTYVAUS veikimo laiką ({self.max_runtime}). Sustabdoma.")
                    raise StopIteration

                # Check if inventory is full
                if inventory.is_inventory_full(self.scanner, self.full_inv_template, self.inventory_full_confidence): #
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Inventorius pilnas. Bandoma išmesti rąstus...")
                    self.start_pause()
                    success, dropped_count = inventory.drop_all_logs(self.scanner, self.log_templates, self.inventory_region, self.log_drop_confidence) #
                    self.end_pause()

                    if success and dropped_count > 0:
                        self.total_logs_collected += dropped_count
                        runtime_logger.save_log_count(self.total_logs_collected) #
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Rąstai ({dropped_count}) išmesti. Tęsiama medžių paieška. Viso: {self.total_logs_collected}")
                        self.tree_spot = None
                        self.current_tree_type = None
                        time.sleep(random.uniform(1.0, 2.0))
                        continue
                    elif success and dropped_count == 0:
                         print(f"[{datetime.now().strftime('%H:%M:%S')}] Inventorius atrodė pilnas, bet nerasta rąstų išmetimui. Tęsiama.")
                         time.sleep(random.uniform(1.0, 2.0))
                         continue
                    else:
                        print("Klaida išmetant rąstus. Botas stabdomas.")
                        break

                # Check if the last known tree spot is still valid
                current_spot_valid = False
                if self.tree_spot and self.current_tree_type:
                    if tree_finder.verify_tree_location(self.scanner, self.tree_spot, self.current_tree_type, self.tree_find_confidence): #
                        current_spot_valid = True
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Medis ({self.current_tree_type}) dingo iš senos vietos ({self.tree_spot}). Ieškoma naujo.")
                        self.tree_spot = None
                        self.current_tree_type = None

                # If no valid spot, find a new tree
                if not current_spot_valid:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Ieškoma naujo medžio...")
                    self.start_pause()
                    # Pakeista: find_tree dabar naudoja jau patikrintus selected_tree_types
                    found_spot, found_type = tree_finder.find_tree(self.scanner, self.selected_tree_types, self.tree_find_confidence) #
                    self.end_pause()

                    if found_spot and found_type:
                        self.tree_spot = found_spot
                        self.current_tree_type = found_type
                        current_spot_valid = True
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] find_tree negrąžino medžio (tai neturėtų įvykti). Laukiama 15s ir bandoma vėl.")
                        self.start_pause()
                        time.sleep(15)
                        self.end_pause()
                        continue

                # If we have a valid spot (either old one verified or new one found)
                if current_spot_valid and self.tree_spot and self.current_tree_type:
                    self.end_pause()
                    if tree_finder.chop_action(self.tree_spot, self.current_tree_type): #
                        check_timeout = 120
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Medis '{self.current_tree_type}' paspaustas ties {self.tree_spot}. Laukiama ~5s prieš pradedant tikrinti.")
                        time.sleep(random.uniform(4.5, 6.0))

                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Tikrinama kas sekundę, ar medis vis dar vietoje (iki {check_timeout}s)...")
                        check_start_time = time.time()
                        tree_still_present_in_loop = True

                        while time.time() - check_start_time < check_timeout:
                            if inventory.is_inventory_full(self.scanner, self.full_inv_template, self.inventory_full_confidence): #
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Inventorius užsipildė tikrinant medį. Einama išmesti.")
                                tree_still_present_in_loop = False
                                break

                            if not tree_finder.verify_tree_location(self.scanner, self.tree_spot, self.current_tree_type, self.tree_verify_confidence): #
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Medis dingo iš vietos po kirtimo (conf={self.tree_verify_confidence}).")
                                tree_still_present_in_loop = False
                                break
                            else:
                                time.sleep(1.0)

                        if not tree_still_present_in_loop:
                            if not inventory.is_inventory_full(self.scanner, self.full_inv_template, self.inventory_full_confidence): #
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Medis nukirstas ir dingo. Laukiama ~10s prieš ieškant kito.")
                                self.start_pause()
                                time.sleep(random.uniform(8, 12))
                                self.end_pause()
                                print(f"[{datetime.now().strftime('%H:%M:%S')}] Pamirštama medžio vieta, ieškoma naujo.")
                                self.tree_spot = None
                                self.current_tree_type = None

                        elif time.time() - check_start_time >= check_timeout:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Pasiektas tikrinimo limitas ({check_timeout}s), medis vis dar buvo matomas (galbūt bot'as stringa?).")
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] Bandoma sukti kamerą ir pamiršti vietą, kad nestrigtų.")
                            self.start_pause()
                            tree_finder.rotate_view() #
                            time.sleep(random.uniform(2, 4))
                            self.end_pause()
                            self.tree_spot = None
                            self.current_tree_type = None

                    else:
                         print(f"[{datetime.now().strftime('%H:%M:%S')}] Klaida atliekant kirtimo veiksmą ({self.current_tree_type} ties {self.tree_spot}). Bandysim ieškoti kito medžio.")
                         self.tree_spot = None
                         self.current_tree_type = None
                         time.sleep(random.uniform(1.0, 2.0))

        except StopIteration:
            print("\nBotas sustabdytas dėl pasiekto maksimalaus veikimo laiko.")
        except KeyboardInterrupt:
            print("\nBotas sustabdytas vartotojo (Ctrl+C).")
        except Exception as e:
            print(f"\nĮvyko netikėta kritinė klaida pagrindiniame cikle: {e}")
            traceback.print_exc()
        finally:
            print("\n" + "="*10 + " Baigiamas darbas " + "="*10)
            try:
                pyautogui.keyUp('shift')
            except Exception:
                pass

            print("\nIšsaugoma statistika:")
            if self.pause_start:
                print("- Užbaigiama nebaigta pauzė...")
                self.end_pause()

            try:
                 runtime_logger.save_runtime_info(self.start_time, self.pause_time, self.total_logs_collected) #
            except Exception as e:
                 print(f"!! KRITINĖ KLAIDA kviečiant save_runtime_info: {e}")
                 traceback.print_exc()

            try:
                 runtime_logger.save_log_count(self.total_logs_collected) #
            except Exception as e:
                 print(f"!! KRITINĖ KLAIDA kviečiant save_log_count pabaigoje: {e}")
                 traceback.print_exc()

            print("\nBotas baigė darbą.")
            print("="*38)