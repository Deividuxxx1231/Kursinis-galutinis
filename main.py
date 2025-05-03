import traceback
from woodcutting_bot import WoodcuttingBot
from tree import TreeFactory

if __name__ == "__main__":
    try:
        bot = WoodcuttingBot()
        bot.run()
    except FileNotFoundError as e:
        print(f"\nKLAIDA PALEIDŽIANT: {e}")
        try:
            bp = TreeFactory.base_path
            print(f"Patikrinkite, ar teisingai nurodytas kelias 'base_path' ({bp}) TreeFactory klasėje ir ar egzistuoja visi reikalingi .png failai.")
        except Exception:
             print("Patikrinkite, ar teisingai nurodytas kelias 'base_path' TreeFactory klasėje ir ar egzistuoja visi reikalingi .png failai.")
    except ImportError as e:
        print(f"\nKLAIDA PALEIDŽIANT: Nepavyko importuoti modulio - {e}.")
        print("Įsitikinkite, kad įdiegėte visas reikalingas bibliotekas:")
        print("pip install pyautogui opencv-python numpy")
        print("Taip pat patikrinkite, ar visi projekto failai (.py) yra tame pačiame aplanke arba Python paieškos kelyje.")
    except Exception as e:
        print(f"\nĮvyko netikėta KLAIDA paleidžiant botą: {e}")
        traceback.print_exc()
    input("\nPaspauskite Enter norėdami uždaryti langą...")