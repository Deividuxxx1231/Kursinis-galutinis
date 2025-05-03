import os
from datetime import datetime, timedelta
import traceback

LOG_COUNT_FILE = "log_count.txt"
RUNTIME_LOG_FILE = "runtime_log.txt"

def load_log_count():
    try:
        with open(LOG_COUNT_FILE, "r", encoding='utf-8') as f:
            line = f.readline()
            if line:
                return int(line.split(":")[-1].strip())
            else:
                return 0
    except (FileNotFoundError, ValueError, IndexError):
        print(f"Failas {LOG_COUNT_FILE} nerastas arba tuščias. Pradedama nuo 0.")
        return 0
    except Exception as e:
        print(f"!! KLAIDA skaitant {LOG_COUNT_FILE}: {e}. Pradedama nuo 0.")
        return 0

def save_log_count(current_count):
    print(f"  * Bandoma įrašyti į {LOG_COUNT_FILE} (Viso malkų: {current_count})")
    try:
        with open(LOG_COUNT_FILE, "w", encoding='utf-8') as f:
            f.write(f"Iš viso surinkta malkų iki paskutinio išmetimo: {current_count}\n")
        print(f"  * Malkų skaičius ({current_count}) sėkmingai įrašytas į {LOG_COUNT_FILE}")
    except IOError as e:
        print(f"!! KLAIDA [IOError] įrašant malkų skaičių į {LOG_COUNT_FILE}: {e}")
    except Exception as e:
        print(f"!! Netikėta KLAIDA save_log_count: {e}")

def save_runtime_info(start_time, pause_time, total_logs_collected):
    now = datetime.now()
    total_runtime = now - start_time
    active_runtime = total_runtime - pause_time
    print(f"  * Bandoma įrašyti į {RUNTIME_LOG_FILE} (Bendra: {total_runtime}, Aktyvi: {active_runtime})")
    try:
        with open(RUNTIME_LOG_FILE, "a", encoding='utf-8') as f:
            f.write("\n" + "="*50 + "\n")
            f.write(f"Sesijos pradžia: {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Sesijos pabaiga: {now.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Sesijos bendras veikimo laikas: {total_runtime}\n")
            f.write(f"Sesijos pauzės (neaktyvumo) laikas: {pause_time}\n")
            f.write(f"Sesijos aktyvaus darbo laikas: {active_runtime}\n")
            f.write(f"Paskutinis malkų skaičius: {total_logs_collected}\n")
            f.write("="*50 + "\n")
        print(f"  * Veikimo laiko informacija sėkmingai įrašyta į {RUNTIME_LOG_FILE}")
    except IOError as e:
        print(f"!! KLAIDA [IOError] įrašant veikimo laiko informaciją į {RUNTIME_LOG_FILE}: {e}")
    except Exception as e:
        print(f"!! Netikėta KLAIDA save_runtime_info: {e}")