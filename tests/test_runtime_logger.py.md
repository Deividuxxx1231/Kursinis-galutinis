import unittest
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import patch, mock_open
import runtime_logger

class TestRuntimeLogger(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.TemporaryDirectory()
        self.log_count_file = os.path.join(self.test_dir.name, "test_log_count.txt")
        self.runtime_log_file = os.path.join(self.test_dir.name, "test_runtime_log.txt")

        self.log_count_patcher = patch('runtime_logger.LOG_COUNT_FILE', self.log_count_file)
        self.runtime_log_patcher = patch('runtime_logger.RUNTIME_LOG_FILE', self.runtime_log_file)
        self.log_count_patcher.start()
        self.runtime_log_patcher.start()

    def tearDown(self):
        self.log_count_patcher.stop()
        self.runtime_log_patcher.stop()
        self.test_dir.cleanup()

    def test_load_log_count_file_not_found(self):
        self.assertEqual(runtime_logger.load_log_count(), 0)

    def test_load_log_count_empty_file(self):
        with open(self.log_count_file, 'w') as f:
            f.write("")
        self.assertEqual(runtime_logger.load_log_count(), 0)

    def test_load_log_count_invalid_content(self):
        with open(self.log_count_file, 'w') as f:
            f.write("Netinkamas formatas")
        self.assertEqual(runtime_logger.load_log_count(), 0)

    def test_load_log_count_valid_content(self):
        with open(self.log_count_file, 'w', encoding='utf-8') as f:
            f.write("Iš viso surinkta malkų iki paskutinio išmetimo: 123\n")
        self.assertEqual(runtime_logger.load_log_count(), 123)

    def test_load_log_count_valid_content_no_prefix(self):
        with open(self.log_count_file, 'w', encoding='utf-8') as f:
            f.write(": 456")
        self.assertEqual(runtime_logger.load_log_count(), 456)


    def test_save_log_count(self):
        runtime_logger.save_log_count(50)
        with open(self.log_count_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, "Iš viso surinkta malkų iki paskutinio išmetimo: 50\n")
        self.assertEqual(runtime_logger.load_log_count(), 50)

    @patch('runtime_logger.datetime')
    def test_save_runtime_info(self, mock_dt):
        start_time = datetime(2023, 1, 1, 10, 0, 0)
        end_time = datetime(2023, 1, 1, 11, 30, 0)
        pause_time = timedelta(minutes=15)
        total_logs = 250

        mock_dt.now.return_value = end_time
        mock_dt.strftime.side_effect = lambda dt_obj, fmt: dt_obj.strftime(fmt)

        runtime_logger.save_runtime_info(start_time, pause_time, total_logs)

        self.assertTrue(os.path.exists(self.runtime_log_file))
        with open(self.runtime_log_file, 'r', encoding='utf-8') as f:
            content = f.read()

        self.assertIn("Sesijos pradžia: 2023-01-01 10:00:00", content)
        self.assertIn("Sesijos pabaiga: 2023-01-01 11:30:00", content)
        self.assertIn("Sesijos bendras veikimo laikas: 1:30:00", content)
        self.assertIn("Sesijos pauzės (neaktyvumo) laikas: 0:15:00", content)
        self.assertIn("Sesijos aktyvaus darbo laikas: 1:15:00", content)
        self.assertIn(f"Paskutinis malkų skaičius: {total_logs}", content)
        self.assertIn("="*50, content)

    @patch("builtins.open", new_callable=mock_open)
    def test_save_log_count_io_error(self, mock_file):
        mock_file.return_value.write.side_effect = IOError("Disk full")
        try:
             runtime_logger.save_log_count(99)
             mock_file.assert_called_once_with(runtime_logger.LOG_COUNT_FILE, "w", encoding='utf-8')
        except Exception as e:
             self.fail(f"save_log_count() sukėlė netikėtą klaidą: {e}")


if __name__ == '__main__':
     unittest.main(argv=['first-arg-is-ignored'], exit=False)