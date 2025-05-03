Įvadas
a.  Kas yra jūsų programa?
Tai yra programa skirta automatizuoti medžių kirtimo veiksmus žaidime. Programa veikia kaip "botas", kuris naudoja ekrano nuskaitymą, kad rastų medžius, kirstų juos ir tvarkytų inventorių, įskaitant rąstų išmetimą, kai inventorius užsipildo. Programa taip pat registruoja veikimo laiką ir surinktų rąstų skaičių.
b.  Kaip paleisti programą?
Programą galima paleisti vykdant main.py failą. Prieš paleidžiant, reikia įsitikinti, kad TreeFactory.base_path kintamasis faile tree.py nurodo teisingą kelią iki paveikslėlių failų ir kad visi reikalingi .png failai egzistuoja nurodytame kelyje. Taip pat reikia įdiegti reikiamas Python bibliotekas (pyautogui, opencv-python, numpy).
c.  Kaip naudotis programa?
Paleidus main.py, programa paprašys įvesti Woodcutting lygį ir pasirinkti medžių tipus, kuriuos norite kirsti, pateikiant galimas parinktis ir jų lygio reikalavimus. Pasirinkus medžius, botas pradės ieškoti pasirinktų medžių ekrane, bandys juos kirsti, o užsipildžius inventoriui, išmes rąstus. Botas veiks tol, kol bus pasiektas maksimalus aktyvaus veikimo laikas arba kol bus sustabdytas vartotojo.
Deja, kolkas programa veikia tik 1920*1080 ekrano rezoliucija.

Pagrindinė dalis / Analizė
Šiame skyriuje analizuojamas programos įgyvendinimas, demonstruojant, kaip buvo laikomasi projekto tikslų ir funkcinių reikalavimų. Programos struktūra, sudaryta iš kelių modulių (main.py, woodcutting_bot.py, scanner.py, tree.py, tree_finder.py, inventory.py, runtime_logger.py), atspindi objektinio programavimo principų taikymą.
Funkcinių reikalavimų įgyvendinimas:

Programa įgyvendina pagrindinius medžių kirtimo boto funkcinius reikalavimus:

Medžių paieška: Modulis scanner.py ir funkcija find_tree modulyje tree_finder.py yra atsakingi už medžių atvaizdų paiešką ekrane, naudojant pyautogui ir opencv-python bibliotekas. Tai atitinka reikalavimą identifikuoti tikslus žaidimo aplinkoje.
Kodo pavyzdys (iš tree_finder.py):

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ... kodas medžio paieškai ...
    pos = scanner.find_on_screen(image_path, confidence=confidence)
    if pos:
        print(f"Rastas {tree.name} ({os.path.basename(image_path)}) pozicijoje {pos}!")
        return pos, tree_type
    # ... toliau kodas sukiojimui ir bandymui is naujo ...

    
Medžių kirtimas: Funkcija chop_action modulyje tree_finder.py imituoja pelės paspaudimą rastos medžio pozicijos centre, atliekant kirtimo veiksmą.
Kodo pavyzdys (iš tree_finder.py):

def chop_action(pos, tree_type):
    # ... saugumo patikrinimai ...
    pyautogui.moveTo(pos[0], pos[1], duration=random.uniform(0.2, 0.5))
    pyautogui.click()
    time.sleep(random.uniform(1.0, 2.0))
    return True

Inventoriaus tvarkymas: Modulis inventory.py teikia funkcijas inventoriaus būsenai tikrinti (is_inventory_full) ir rąstams išmesti (drop_all_logs), kai inventorius pilnas. Naudojamas shift klavišas kartu su paspaudimu, kad būtų galima greitai išmesti daiktus.
Kodo pavyzdys (iš inventory.py):

def is_inventory_full(scanner: ImageScanner, template_path: str, confidence: float) -> bool:
    found = scanner.find_on_screen(template_path, confidence=confidence)
    return found is not None

def drop_all_logs(scanner: ImageScanner, log_templates: list, inventory_region: tuple, confidence: float) -> tuple[bool, int]:
    # ... kodas rąstų paieškai inventoriuje ir jų išmetimui ...
    pyautogui.keyDown('shift')
    pyautogui.click()
    pyautogui.keyUp('shift')
    # ... toliau kodas ...

Progresyvumo registravimas: Modulis runtime_logger.py saugo surinktų rąstų skaičių ir sesijos veikimo laiko statistiką failuose (log_count.txt, runtime_log.txt).
Kodo pavyzdys (iš runtime_logger.py):

def save_log_count(current_count):
    with open(LOG_COUNT_FILE, "w", encoding='utf-8') as f:
        f.write(f"Iš viso surinkta malkų iki paskutinio išmetimo: {current_count}\\n")

def save_runtime_info(start_time, pause_time, total_logs_collected):
    # ... kodas veikimo laiko skaičiavimui ...
    with open(RUNTIME_LOG_FILE, "a", encoding='utf-8') as f:
        # ... rašoma informacija apie sesiją ...
        f.write(f"Paskutinis malkų skaičius: {total_logs_collected}\\n")


 OOP ramsčiai, jų reikšmė ir naudojimas:

Inkapsuliacija (Encapsulation): Duomenys (atributai) ir metodai, veikiantys su tais duomenimis, yra sujungti į vieną vienetą (klasę). Tai padeda paslėpti vidinę klasės būseną ir užtikrina duomenų vientisumą. Pavyzdžiui, ImageScanner klasė inkapsuliuoja ekrano nuskaitymo logiką ir konfidencialumo nustatymus. WoodcuttingBot klasė inkapsuliuoja visą boto veikimo logiką, saugodama savo būseną (pvz., self.total_logs_collected, self.tree_spot).
Kodo pavyzdys (iš scanner.py):

  class ImageScanner:
    def __init__(self, confidence=0.65):
        self.confidence = confidence # Inkapsuliuotas atributas

    def screenshot(self): # Metodas, veikiantis su vidiniais duomenimis (nors čia tiesiogiai nenaudoja self.confidence)
        # ... kodas ...
        pass

    def find_on_screen(self, template_path, region=None, confidence=None): # Metodas
        # ... kodas ...
        pass

Abstrakcija (Abstraction): Sudėtingos sistemos detalės yra paslepiamos, pateikiant tik būtiniausią sąsają. Bazinis Tree klasė yra abstrahuotas medžio apibrėžimas su abstrakčiu metodu required_level, nurodant, kad kiekvienas konkretus medžio tipas turės šį metodą, bet neapibrėžiant, kaip jis bus įgyvendintas.
Kodo pavyzdys (iš tree.py):

  from abc import ABC, abstractmethod

class Tree(ABC): # Abstrakti bazinė klasė
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths

    @abstractmethod
    def required_level(self): # Abstraktus metodas
        pass

Paveldėjimas (Inheritance): Naujos klasės (išvestinės klasės) perima savybes ir elgesį iš esamų klasių (bazinių klasių). NormalTree ir OakTree klasės paveldi iš bazinės Tree klasės, perimdamos __init__ metodą ir name, image_paths atributus, bet įgyvendina savo specifinę required_level logiką.
Kodo pavyzdys (iš tree.py):

class NormalTree(Tree): # Paveldėjimas
    def required_level(self): return 1

class OakTree(Tree): # Paveldėjimas
    def required_level(self): return 15

Polimorfizmas (Polymorphism): Gebėjimas skirtingoms klasėms reaguoti į tą patį metodą skirtingais būdais. Nors šiame kode polimorfizmas nėra itin ryškus per metodų perrašymą, jo apraiškų yra, pavyzdžiui, find_tree funkcija modulyje tree_finder.py gali dirbti su skirtingais Tree objektais (NormalTree, OakTree), kreipdamasi į jų bendrus atributus (image_paths) arba metodus, jei tokių būtų daugiau. Taip pat drop_all_logs funkcija modulyje inventory.py iteruoja per skirtingus rąstų šablonus (log_templates), kurie gali atspindėti skirtingus rąstų tipus, traktuojant juos bendru būdu (kaip "rąstų šablonus").
Kodo pavyzdys (iš tree_finder.py):

  def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ...
    for tree_type in temp_tree_types:
        tree = TreeFactory.create_tree(tree_type) # Gaunami skirtingi Tree tipo objektai
        for image_path in tree.image_paths: # Polimorfinis naudojimas, nes NormalTree ir OakTree turi .image_paths
            pos = scanner.find_on_screen(image_path, confidence=confidence)
            # ...

Naudojamas dizaino šablonas:

Projekte naudojamas Gamyklinis metodas (Factory Method) dizaino šablonas, realizuotas TreeFactory klasėje. Šis šablonas leidžia kurti objektus nenurodant tikslios klasės, kuri bus sukurta. TreeFactory.create_tree(tree_type) metodas grąžina atitinkamą Tree paveldinčios klasės (NormalTree ar OakTree) objektą, priklausomai nuo tree_type parametro. Tai suteikia lankstumo pridedant naujus medžių tipus ateityje, nekeičiant kliento kodo, kuris naudoja gamyklą.

Kodo pavyzdys (iš tree.py):

class TreeFactory:
    # ...
    @staticmethod
    def create_tree(tree_type):
        # ... objektų kūrimo logika pagal tree_type ...
        if tree_type in mapping:
            return mapping[tree_type] # Grąžinamas konkretus Tree objektas
        # ...


Remiantis pateiktais failais ir OOP kurso reikalavimais, pagrindinę dalį / analizę galima aprašyti taip:

2. Pagrindinė dalis / Analizė
Šiame skyriuje analizuojamas programos įgyvendinimas, demonstruojant, kaip buvo laikomasi projekto tikslų ir funkcinių reikalavimų. Programos struktūra, sudaryta iš kelių modulių (main.py, woodcutting_bot.py, scanner.py, tree.py, tree_finder.py, inventory.py, runtime_logger.py), atspindi objektinio programavimo principų taikymą.

Funkcinių reikalavimų įgyvendinimas:

Programa įgyvendina pagrindinius medžių kirtimo boto funkcinius reikalavimus:

Medžių paieška: Modulis scanner.py ir funkcija find_tree modulyje tree_finder.py yra atsakingi už medžių atvaizdų paiešką ekrane, naudojant pyautogui ir opencv-python bibliotekas. Tai atitinka reikalavimą identifikuoti tikslus žaidimo aplinkoje.
Kodo pavyzdys (iš tree_finder.py):
Python

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ... kodas medžio paieškai ...
    pos = scanner.find_on_screen(image_path, confidence=confidence)
    if pos:
        print(f"Rastas {tree.name} ({os.path.basename(image_path)}) pozicijoje {pos}!")
        return pos, tree_type
    # ... toliau kodas sukiojimui ir bandymui is naujo ...
Medžių kirtimas: Funkcija chop_action modulyje tree_finder.py imituoja pelės paspaudimą rastos medžio pozicijos centre, atliekant kirtimo veiksmą.
Kodo pavyzdys (iš tree_finder.py):
Python

def chop_action(pos, tree_type):
    # ... saugumo patikrinimai ...
    pyautogui.moveTo(pos[0], pos[1], duration=random.uniform(0.2, 0.5))
    pyautogui.click()
    time.sleep(random.uniform(1.0, 2.0))
    return True
Inventoriaus tvarkymas: Modulis inventory.py teikia funkcijas inventoriaus būsenai tikrinti (is_inventory_full) ir rąstams išmesti (drop_all_logs), kai inventorius pilnas. Naudojamas shift klavišas kartu su paspaudimu, kad būtų galima greitai išmesti daiktus.
Kodo pavyzdys (iš inventory.py):
Python

def is_inventory_full(scanner: ImageScanner, template_path: str, confidence: float) -> bool:
    found = scanner.find_on_screen(template_path, confidence=confidence)
    return found is not None

def drop_all_logs(scanner: ImageScanner, log_templates: list, inventory_region: tuple, confidence: float) -> tuple[bool, int]:
    # ... kodas rąstų paieškai inventoriuje ir jų išmetimui ...
    pyautogui.keyDown('shift')
    pyautogui.click()
    pyautogui.keyUp('shift')
    # ... toliau kodas ...
Progresyvumo registravimas: Modulis runtime_logger.py saugo surinktų rąstų skaičių ir sesijos veikimo laiko statistiką failuose (log_count.txt, runtime_log.txt).
Kodo pavyzdys (iš runtime_logger.py):
Python

def save_log_count(current_count):
    with open(LOG_COUNT_FILE, "w", encoding='utf-8') as f:
        f.write(f"Iš viso surinkta malkų iki paskutinio išmetimo: {current_count}\\n")

def save_runtime_info(start_time, pause_time, total_logs_collected):
    # ... kodas veikimo laiko skaičiavimui ...
    with open(RUNTIME_LOG_FILE, "a", encoding='utf-8') as f:
        # ... rašoma informacija apie sesiją ...
        f.write(f"Paskutinis malkų skaičius: {total_logs_collected}\\n")
4 OOP ramsčiai, jų reikšmė ir naudojimas:

Inkapsuliacija (Encapsulation): Duomenys (atributai) ir metodai, veikiantys su tais duomenimis, yra sujungti į vieną vienetą (klasę). Tai padeda paslėpti vidinę klasės būseną ir užtikrina duomenų vientisumą. Pavyzdžiui, ImageScanner klasė inkapsuliuoja ekrano nuskaitymo logiką ir konfidencialumo nustatymus. WoodcuttingBot klasė inkapsuliuoja visą boto veikimo logiką, saugodama savo būseną (pvz., self.total_logs_collected, self.tree_spot).
Kodo pavyzdys (iš scanner.py):
Python

class ImageScanner:
    def __init__(self, confidence=0.65):
        self.confidence = confidence # Inkapsuliuotas atributas

    def screenshot(self): # Metodas, veikiantis su vidiniais duomenimis (nors čia tiesiogiai nenaudoja self.confidence)
        # ... kodas ...
        pass

    def find_on_screen(self, template_path, region=None, confidence=None): # Metodas
        # ... kodas ...
        pass
Abstrakcija (Abstraction): Sudėtingos sistemos detalės yra paslepiamos, pateikiant tik būtiniausią sąsają. Bazinis Tree klasė yra abstrahuotas medžio apibrėžimas su abstrakčiu metodu required_level, nurodant, kad kiekvienas konkretus medžio tipas turės šį metodą, bet neapibrėžiant, kaip jis bus įgyvendintas.
Kodo pavyzdys (iš tree.py):
Python

from abc import ABC, abstractmethod

class Tree(ABC): # Abstrakti bazinė klasė
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths

    @abstractmethod
    def required_level(self): # Abstraktus metodas
        pass
Paveldėjimas (Inheritance): Naujos klasės (išvestinės klasės) perima savybes ir elgesį iš esamų klasių (bazinių klasių). NormalTree ir OakTree klasės paveldi iš bazinės Tree klasės, perimdamos __init__ metodą ir name, image_paths atributus, bet įgyvendina savo specifinę required_level logiką.
Kodo pavyzdys (iš tree.py):
Python

class NormalTree(Tree): # Paveldėjimas
    def required_level(self): return 1

class OakTree(Tree): # Paveldėjimas
    def required_level(self): return 15
Polimorfizmas (Polymorphism): Gebėjimas skirtingoms klasėms reaguoti į tą patį metodą skirtingais būdais. Nors šiame kode polimorfizmas nėra itin ryškus per metodų perrašymą, jo apraiškų yra, pavyzdžiui, find_tree funkcija modulyje tree_finder.py gali dirbti su skirtingais Tree objektais (NormalTree, OakTree), kreipdamasi į jų bendrus atributus (image_paths) arba metodus, jei tokių būtų daugiau. Taip pat drop_all_logs funkcija modulyje inventory.py iteruoja per skirtingus rąstų šablonus (log_templates), kurie gali atspindėti skirtingus rąstų tipus, traktuojant juos bendru būdu (kaip "rąstų šablonus").
Kodo pavyzdys (iš tree_finder.py):
Python

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ...
    for tree_type in temp_tree_types:
        tree = TreeFactory.create_tree(tree_type) # Gaunami skirtingi Tree tipo objektai
        for image_path in tree.image_paths: # Polimorfinis naudojimas, nes NormalTree ir OakTree turi .image_paths
            pos = scanner.find_on_screen(image_path, confidence=confidence)
            # ...
Naudojamas dizaino šablonas:

Projekte naudojamas Gamyklinis metodas (Factory Method) dizaino šablonas, realizuotas TreeFactory klasėje. Šis šablonas leidžia kurti objektus nenurodant tikslios klasės, kuri bus sukurta. TreeFactory.create_tree(tree_type) metodas grąžina atitinkamą Tree paveldinčios klasės (NormalTree ar OakTree) objektą, priklausomai nuo tree_type parametro. Tai suteikia lankstumo pridedant naujus medžių tipus ateityje, nekeičiant kliento kodo, kuris naudoja gamyklą.

Kodo pavyzdys (iš tree.py):
Python

class TreeFactory:
    # ...
    @staticmethod
    def create_tree(tree_type):
        # ... objektų kūrimo logika pagal tree_type ...
        if tree_type in mapping:
            return mapping[tree_type] # Grąžinamas konkretus Tree objektas
        # ...
Kompozicijos ir/arba agregacijos principai:

Projekte naudojama kompozicija ir agregacija.

Kompozicija: WoodcuttingBot klasė turi ImageScanner objektą (sukurtą __init__ metu: self.scanner = ImageScanner(...)). Nors ImageScanner gali egzistuoti nepriklausomai nuo WoodcuttingBot, šiame kontekste botas yra atsakingas už scanner objekto gyvavimo ciklo valdymą (bent jau pagal numatytąjį scenarijų).
Agregacija: WoodcuttingBot naudoja (bet nebūtinai tiesiogiai valdo gyvavimo ciklo) funkcijas iš kitų modulių, tokių kaip inventory.py (inventory.is_inventory_full, inventory.drop_all_logs) ir tree_finder.py (tree_finder.find_tree, tree_finder.verify_tree_location, tree_finder.chop_action, tree_finder.rotate_view). Tai labiau laisva asociacija, kur WoodcuttingBot priklauso nuo šių modulių teikiamų paslaugų.
Kodo pavyzdys (iš woodcutting_bot.py):


class WoodcuttingBot:
    def __init__(self):
        self.scanner = ImageScanner(confidence=0.65) # Kompozicija
        # ...
    def run(self):
        # ...
        if inventory.is_inventory_full(self.scanner, ...) # Agregacija/naudojimas
            # ...
        found_spot, found_type = tree_finder.find_tree(self.scanner, ...) # Agregacija/naudojimas
        # ...

Remiantis pateiktais failais ir OOP kurso reikalavimais, pagrindinę dalį / analizę galima aprašyti taip:

2. Pagrindinė dalis / Analizė
Šiame skyriuje analizuojamas programos įgyvendinimas, demonstruojant, kaip buvo laikomasi projekto tikslų ir funkcinių reikalavimų. Programos struktūra, sudaryta iš kelių modulių (main.py, woodcutting_bot.py, scanner.py, tree.py, tree_finder.py, inventory.py, runtime_logger.py), atspindi objektinio programavimo principų taikymą.

Funkcinių reikalavimų įgyvendinimas:

Programa įgyvendina pagrindinius medžių kirtimo boto funkcinius reikalavimus:

Medžių paieška: Modulis scanner.py ir funkcija find_tree modulyje tree_finder.py yra atsakingi už medžių atvaizdų paiešką ekrane, naudojant pyautogui ir opencv-python bibliotekas. Tai atitinka reikalavimą identifikuoti tikslus žaidimo aplinkoje.
Kodo pavyzdys (iš tree_finder.py):
Python

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ... kodas medžio paieškai ...
    pos = scanner.find_on_screen(image_path, confidence=confidence)
    if pos:
        print(f"Rastas {tree.name} ({os.path.basename(image_path)}) pozicijoje {pos}!")
        return pos, tree_type
    # ... toliau kodas sukiojimui ir bandymui is naujo ...
Medžių kirtimas: Funkcija chop_action modulyje tree_finder.py imituoja pelės paspaudimą rastos medžio pozicijos centre, atliekant kirtimo veiksmą.
Kodo pavyzdys (iš tree_finder.py):
Python

def chop_action(pos, tree_type):
    # ... saugumo patikrinimai ...
    pyautogui.moveTo(pos[0], pos[1], duration=random.uniform(0.2, 0.5))
    pyautogui.click()
    time.sleep(random.uniform(1.0, 2.0))
    return True
Inventoriaus tvarkymas: Modulis inventory.py teikia funkcijas inventoriaus būsenai tikrinti (is_inventory_full) ir rąstams išmesti (drop_all_logs), kai inventorius pilnas. Naudojamas shift klavišas kartu su paspaudimu, kad būtų galima greitai išmesti daiktus.
Kodo pavyzdys (iš inventory.py):
Python

def is_inventory_full(scanner: ImageScanner, template_path: str, confidence: float) -> bool:
    found = scanner.find_on_screen(template_path, confidence=confidence)
    return found is not None

def drop_all_logs(scanner: ImageScanner, log_templates: list, inventory_region: tuple, confidence: float) -> tuple[bool, int]:
    # ... kodas rąstų paieškai inventoriuje ir jų išmetimui ...
    pyautogui.keyDown('shift')
    pyautogui.click()
    pyautogui.keyUp('shift')
    # ... toliau kodas ...
Progresyvumo registravimas: Modulis runtime_logger.py saugo surinktų rąstų skaičių ir sesijos veikimo laiko statistiką failuose (log_count.txt, runtime_log.txt).
Kodo pavyzdys (iš runtime_logger.py):
Python

def save_log_count(current_count):
    with open(LOG_COUNT_FILE, "w", encoding='utf-8') as f:
        f.write(f"Iš viso surinkta malkų iki paskutinio išmetimo: {current_count}\\n")

def save_runtime_info(start_time, pause_time, total_logs_collected):
    # ... kodas veikimo laiko skaičiavimui ...
    with open(RUNTIME_LOG_FILE, "a", encoding='utf-8') as f:
        # ... rašoma informacija apie sesiją ...
        f.write(f"Paskutinis malkų skaičius: {total_logs_collected}\\n")
4 OOP ramsčiai, jų reikšmė ir naudojimas:

Inkapsuliacija (Encapsulation): Duomenys (atributai) ir metodai, veikiantys su tais duomenimis, yra sujungti į vieną vienetą (klasę). Tai padeda paslėpti vidinę klasės būseną ir užtikrina duomenų vientisumą. Pavyzdžiui, ImageScanner klasė inkapsuliuoja ekrano nuskaitymo logiką ir konfidencialumo nustatymus. WoodcuttingBot klasė inkapsuliuoja visą boto veikimo logiką, saugodama savo būseną (pvz., self.total_logs_collected, self.tree_spot).
Kodo pavyzdys (iš scanner.py):
Python

class ImageScanner:
    def __init__(self, confidence=0.65):
        self.confidence = confidence # Inkapsuliuotas atributas

    def screenshot(self): # Metodas, veikiantis su vidiniais duomenimis (nors čia tiesiogiai nenaudoja self.confidence)
        # ... kodas ...
        pass

    def find_on_screen(self, template_path, region=None, confidence=None): # Metodas
        # ... kodas ...
        pass
Abstrakcija (Abstraction): Sudėtingos sistemos detalės yra paslepiamos, pateikiant tik būtiniausią sąsają. Bazinis Tree klasė yra abstrahuotas medžio apibrėžimas su abstrakčiu metodu required_level, nurodant, kad kiekvienas konkretus medžio tipas turės šį metodą, bet neapibrėžiant, kaip jis bus įgyvendintas.
Kodo pavyzdys (iš tree.py):
Python

from abc import ABC, abstractmethod

class Tree(ABC): # Abstrakti bazinė klasė
    def __init__(self, name, image_paths):
        self.name = name
        self.image_paths = image_paths

    @abstractmethod
    def required_level(self): # Abstraktus metodas
        pass
Paveldėjimas (Inheritance): Naujos klasės (išvestinės klasės) perima savybes ir elgesį iš esamų klasių (bazinių klasių). NormalTree ir OakTree klasės paveldi iš bazinės Tree klasės, perimdamos __init__ metodą ir name, image_paths atributus, bet įgyvendina savo specifinę required_level logiką.
Kodo pavyzdys (iš tree.py):
Python

class NormalTree(Tree): # Paveldėjimas
    def required_level(self): return 1

class OakTree(Tree): # Paveldėjimas
    def required_level(self): return 15
Polimorfizmas (Polymorphism): Gebėjimas skirtingoms klasėms reaguoti į tą patį metodą skirtingais būdais. Nors šiame kode polimorfizmas nėra itin ryškus per metodų perrašymą, jo apraiškų yra, pavyzdžiui, find_tree funkcija modulyje tree_finder.py gali dirbti su skirtingais Tree objektais (NormalTree, OakTree), kreipdamasi į jų bendrus atributus (image_paths) arba metodus, jei tokių būtų daugiau. Taip pat drop_all_logs funkcija modulyje inventory.py iteruoja per skirtingus rąstų šablonus (log_templates), kurie gali atspindėti skirtingus rąstų tipus, traktuojant juos bendru būdu (kaip "rąstų šablonus").
Kodo pavyzdys (iš tree_finder.py):
Python

def find_tree(scanner: ImageScanner, available_tree_types: list, confidence: float):
    # ...
    for tree_type in temp_tree_types:
        tree = TreeFactory.create_tree(tree_type) # Gaunami skirtingi Tree tipo objektai
        for image_path in tree.image_paths: # Polimorfinis naudojimas, nes NormalTree ir OakTree turi .image_paths
            pos = scanner.find_on_screen(image_path, confidence=confidence)
            # ...
Naudojamas dizaino šablonas:

Projekte naudojamas Gamyklinis metodas (Factory Method) dizaino šablonas, realizuotas TreeFactory klasėje. Šis šablonas leidžia kurti objektus nenurodant tikslios klasės, kuri bus sukurta. TreeFactory.create_tree(tree_type) metodas grąžina atitinkamą Tree paveldinčios klasės (NormalTree ar OakTree) objektą, priklausomai nuo tree_type parametro. Tai suteikia lankstumo pridedant naujus medžių tipus ateityje, nekeičiant kliento kodo, kuris naudoja gamyklą.

Kodo pavyzdys (iš tree.py):
Python

class TreeFactory:
    # ...
    @staticmethod
    def create_tree(tree_type):
        # ... objektų kūrimo logika pagal tree_type ...
        if tree_type in mapping:
            return mapping[tree_type] # Grąžinamas konkretus Tree objektas
        # ...
Kompozicijos ir/arba agregacijos principai:

Projekte naudojama kompozicija ir agregacija.

Kompozicija: WoodcuttingBot klasė turi ImageScanner objektą (sukurtą __init__ metu: self.scanner = ImageScanner(...)). Nors ImageScanner gali egzistuoti nepriklausomai nuo WoodcuttingBot, šiame kontekste botas yra atsakingas už scanner objekto gyvavimo ciklo valdymą (bent jau pagal numatytąjį scenarijų).
Agregacija: WoodcuttingBot naudoja (bet nebūtinai tiesiogiai valdo gyvavimo ciklo) funkcijas iš kitų modulių, tokių kaip inventory.py (inventory.is_inventory_full, inventory.drop_all_logs) ir tree_finder.py (tree_finder.find_tree, tree_finder.verify_tree_location, tree_finder.chop_action, tree_finder.rotate_view). Tai labiau laisva asociacija, kur WoodcuttingBot priklauso nuo šių modulių teikiamų paslaugų.
Kodo pavyzdys (iš woodcutting_bot.py):
Python

class WoodcuttingBot:
    def __init__(self):
        self.scanner = ImageScanner(confidence=0.65) # Kompozicija
        # ...
    def run(self):
        # ...
        if inventory.is_inventory_full(self.scanner, ...) # Agregacija/naudojimas
            # ...
        found_spot, found_type = tree_finder.find_tree(self.scanner, ...) # Agregacija/naudojimas
        # ...

Skaitymas iš failo ir rašymas į failą:

Programa skaito ir rašo duomenis į failus, siekdama išsaugoti ir atkurti boto progresą bei registruoti veikimo statistiką.

runtime_logger.py modulis atsakingas už:
Skaitymas: load_log_count() funkcija skaito paskutinį surinktų rąstų skaičių iš log_count.txt failo, programos paleidimo metu.
Rašymas: save_log_count(current_count) funkcija įrašo dabartinį surinktų rąstų skaičių į log_count.txt. save_runtime_info(...) funkcija prideda informaciją apie kiekvienos sesijos veikimo laiką ir pabaigos rąstų skaičių į runtime_log.txt.
woodcutting_bot.py modulis taip pat skaito ir rašo paskutinį pasirinktų medžių tipų sąrašą į last_selected_trees.txt failą, siekiant palengvinti pakartotinį paleidimą.

Testavimas:

Pateiktame kodo yra sukurti 3 testavimo failai test_runtime_logger.py, test_tree.py ir test_woodcutting_bot.py. šie testai sukurti ištestuoti OOP bei dalį kodo. Deja, tačiau su nuotraukų atpažinimu testavimas buvo per sudėtingas ir nepavyko tokio sukurti, kuris galėtų tai ištestuoti.

Kodo stilius:

Programos kodas parašytas Python kalba. Bendras kodo formatavimas ir struktūra atrodo sekanti bendras Python programavimo konvencijas, įskaitant klasių, funkcijų, kintamųjų pavadinimus ir importų tvarkymą. Stengtasi laikytis PEP8 stiliaus.

Pagalbinės priemonės:

Kaip pagalbinės priemonės naudotos Gemini AI (ištaisyti kodo klaidas, sugeneruoti testinius failus, bei pagalba aprašant darbą, bei rasti tam tikrus sprendimus kaip ką atlikti ar geriau atlikti), Copilot, Youtube image recognition in Python tutorial, buvo kreiptasi ir į fullstack programuotoja, dėl iškilusios problemos su inventory region problema.

