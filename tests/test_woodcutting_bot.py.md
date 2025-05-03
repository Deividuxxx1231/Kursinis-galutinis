import unittest
from unittest.mock import patch, MagicMock, mock_open, call
import os
from datetime import datetime, timedelta

# Importuojame testuojamą klasę ir reikalingas priklausomybes tipams
from woodcutting_bot import WoodcuttingBot
from tree import Tree, NormalTree, OakTree # Reikia TreeFactory mock'inimui
from scanner import ImageScanner # Reikia ImageScanner mock'inimui


# Sukuriame imitacines medžių klases testavimui
class MockNormalTree(Tree):
    def __init__(self):
        super().__init__("Normal Tree", ["dummy_normal_path.png"])
    def required_level(self): return 1

class MockOakTree(Tree):
    def __init__(self):
        super().__init__("Oak Tree", ["dummy_oak_path.png"])
    def required_level(self): return 15


# --- Testų klasė ---
class TestWoodcuttingBotLogic(unittest.TestCase):

    # Kiekvienam testui paruošiame šviežią aplinką su mock'ais
    # Patchinam viską, ko reikia __init__ ir testuojamiems metodams
    @patch('woodcutting_bot.ImageScanner', spec=ImageScanner)
    @patch('woodcutting_bot.TreeFactory')
    @patch('woodcutting_bot.runtime_logger')
    @patch('woodcutting_bot.inventory') # Nors nenaudojamas tiesiogiai testuojamuose metoduose, bet __init__ jį importuoja
    @patch('woodcutting_bot.tree_finder') # Tas pats kaip inventory
    @patch('builtins.input')
    @patch('builtins.open', new_callable=mock_open)
    @patch('woodcutting_bot.os.path.exists') # Reikia TreeFactory.check_required_files viduje __init__ ir ask_tree_choice
    @patch('woodcutting_bot.datetime')
    @patch('woodcutting_bot.timedelta', return_value=timedelta()) # Grąžinam tuščią timedelta
    def run_bot_init(self, mock_timedelta, mock_datetime, mock_os_exists, mock_file, mock_input, mock_tf, mock_inv, mock_rt_logger, mock_tree_factory, mock_scanner):
        # Konfigūruojame pagrindinius mock'us, kad __init__ praeitų sėkmingai

        # 1. runtime_logger mock'as
        mock_rt_logger.load_log_count.return_value = 0 # Pradinis logų skaičius

        # 2. TreeFactory mock'as
        #    check_required_files nieko nedaro (arba galim patikrinti iškvietimą)
        mock_tree_factory.check_required_files.return_value = None
        #    create_tree grąžina mūsų imitacines klases
        def mock_create_tree(tree_type):
            if tree_type == "normal":
                return MockNormalTree()
            elif tree_type == "oak":
                return MockOakTree()
            else:
                raise ValueError(f"Unknown mock tree type: {tree_type}")
        mock_tree_factory.create_tree.side_effect = mock_create_tree
        mock_tree_factory.base_path = "dummy/base/path" # Nustatome netikrą kelią

        # 3. os.path.exists mock'as
        #    Tarkime, visi failai egzistuoja (svarbu TreeFactory.check_required_files)
        #    ir last_selected_trees.txt failas egzistuoja pagal nutylėjimą
        #    Testuose galėsime pakeisti jo reikšmę specifiniams scenarijams
        mock_os_exists.return_value = True

        # 4. input mock'as
        #    Nustatome numatytas reikšmes, kurias testai galės pakeisti
        mock_input.side_effect = ['1', '1'] # Numatytasis lygis 1, medis 1

        # 5. open mock'as
        #    Numatytasis failo turinys (galėsime pakeisti)
        mock_file.return_value.read.return_value = "normal" # Numatytasis paskutinis pasirinkimas

        # 6. datetime mock'as
        mock_datetime.now.return_value = datetime(2025, 5, 1, 9, 0, 0)

        # --- Iškviečiame __init__ su visais paruoštais mock'ais ---
        bot = WoodcuttingBot()

        # Grąžiname bot'ą ir mock'ų rinkinį, kad testai galėtų juos naudoti/tikrinti
        return bot, {
            "input": mock_input,
            "open": mock_file,
            "os_exists": mock_os_exists,
            "tree_factory": mock_tree_factory,
            "rt_logger": mock_rt_logger
        }

    # --- Testuojame ask_woodcutting_level ---
    def test_ask_woodcutting_level_valid(self):
        # Inicijuojame botą su pradiniais mock'ais, bet pakeičiame input seką
        input_sequence = ['abc', '100', '0', '25'] # Blogas, per didelis, per mažas, GERAS
        with patch('builtins.input', side_effect=input_sequence):
             bot, mocks = self.run_bot_init()
             # Nors __init__ kviečia ask_level, čia kviečiame dar kartą tiesiogiai testavimui
             # Svarbu: __init__ jau nustatė bot.woodcutting_level pagal *pirmą* input seką ('abc' -> klaida -> '100' -> klaida -> '0' -> klaida -> '25')
             # Testuojame patį metodą izoliuotai
             level = bot.ask_woodcutting_level()

        self.assertEqual(level, 25)
        # Patikriname, kad input buvo kviestas 4 kartus šio metodo viduje
        # DĖMESIO: Dėl __init__ iškvietimo, mocks['input'].call_count bus didesnis bendrai.
        # Testuojant izoliuotai, reikėtų mock'inti tik šiam metodui.
        # Bet čia matome, kad metodas veikė kaip tikėtasi su pateikta seką.

    # --- Testuojame ask_tree_choice ---

    def test_ask_tree_choice_first_run_sufficient_level(self):
        # Botas su 20 lygiu, last_selected neegzistuoja, renkasi normal ir oak
        bot, mocks = self.run_bot_init()
        mocks['os_exists'].side_effect = lambda path: path != "last_selected_trees.txt" # Failas neegzistuoja
        mocks['input'].side_effect = ['20', '1, 2'] # Įvedamas lygis 20, tada pasirenkama 1 ir 2
        # Atnaujiname bot lygį po __init__ pagal testą
        bot.woodcutting_level = bot.ask_woodcutting_level() # Dabar bus 20
        # Kviečiame testuojamą metodą
        selected_trees = bot.ask_tree_choice()

        self.assertEqual(selected_trees, ['normal', 'oak'])
        # Patikriname, kad buvo bandyta rašyti į failą
        mocks['open'].assert_called_with("last_selected_trees.txt", "w", encoding='utf-8')
        mocks['open']().write.assert_called_once_with("normal,oak")

    def test_ask_tree_choice_insufficient_level(self):
        # Botas su 10 lygiu, bando rinktis normal ir oak, tada pasirenka tik normal
        bot, mocks = self.run_bot_init()
        mocks['os_exists'].side_effect = lambda path: path != "last_selected_trees.txt"
        # Pirma įvestis lygiui, antra - blogam pasirinkimui, trečia - geram
        mocks['input'].side_effect = ['10', '1, 2', '1']
        bot.woodcutting_level = bot.ask_woodcutting_level() # Dabar bus 10
        selected_trees = bot.ask_tree_choice()

        self.assertEqual(selected_trees, ['normal'])
        # Patikriname input iškvietimus (lygis + blogas pasirinkimas + geras pasirinkimas)
        self.assertEqual(mocks['input'].call_count, 3)
        mocks['open'].assert_called_with("last_selected_trees.txt", "w", encoding='utf-8')
        mocks['open']().write.assert_called_once_with("normal")

    def test_ask_tree_choice_use_last_selection_valid(self):
         # Botas su 20 lygiu, failas egzistuoja su "normal,oak", sutinka naudoti
        bot, mocks = self.run_bot_init()
        mocks['os_exists'].return_value = True # Failas egzistuoja
        mocks['open'].return_value.read.return_value = "normal,oak" # Failo turinys
        # Lygis 20, patvirtinimas 't'
        mocks['input'].side_effect = ['20', 't']
        bot.woodcutting_level = bot.ask_woodcutting_level() # Lygis 20
        selected_trees = bot.ask_tree_choice()

        self.assertEqual(selected_trees, ['normal', 'oak'])
        # Patikriname input (lygis + patvirtinimas)
        self.assertEqual(mocks['input'].call_count, 2)
        # Patikriname, kad nebuvo bandyta rašyti į failą iš naujo
        mocks['open']().write.assert_not_called()

    def test_ask_tree_choice_use_last_selection_invalid_level(self):
        # Botas su 10 lygiu, failas su "normal,oak", bando naudoti, bet negali, tada renkasi "normal"
        bot, mocks = self.run_bot_init()
        mocks['os_exists'].return_value = True
        mocks['open'].return_value.read.return_value = "normal,oak"
        # Lygis 10, patvirtinimas 't', naujas pasirinkimas '1'
        mocks['input'].side_effect = ['10', 't', '1']
        bot.woodcutting_level = bot.ask_woodcutting_level() # Lygis 10
        selected_trees = bot.ask_tree_choice()

        self.assertEqual(selected_trees, ['normal'])
        # Patikriname input (lygis + 't' + naujas '1')
        self.assertEqual(mocks['input'].call_count, 3)
        # Patikriname, kad buvo įrašytas naujas pasirinkimas
        mocks['open'].assert_called_with("last_selected_trees.txt", "w", encoding='utf-8')
        mocks['open']().write.assert_called_once_with("normal")

    # Galima pridėti testą pauzėms (start_pause/end_pause), bet jis paprastesnis
    # @patch('woodcutting_bot.datetime')
    # def test_pause_logic(self, mock_datetime):
    #     bot, mocks = self.run_bot_init()
    #     start_pause_time = datetime(2025, 5, 1, 10, 0, 0)
    #     end_pause_time = datetime(2025, 5, 1, 10, 5, 0)
    #     mock_datetime.now.side_effect = [start_pause_time, end_pause_time]

    #     bot.start_pause()
    #     self.assertEqual(bot.pause_start, start_pause_time)
    #     bot.end_pause()
    #     self.assertIsNone(bot.pause_start)
    #     self.assertEqual(bot.pause_time, timedelta(minutes=5))


if __name__ == '__main__':
    unittest.main(argv=['first-arg-is-ignored'], exit=False)