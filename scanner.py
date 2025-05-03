import pyautogui
import cv2
import numpy as np
import os

class ImageScanner:
    def __init__(self, confidence=0.65):
        self.confidence = confidence

    def screenshot(self):
        try:
            image = pyautogui.screenshot()
            return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Klaida darant ekrano nuotrauką: {e}")
            return None

    def find_on_screen(self, template_path, region=None, confidence=None):
        conf = confidence if confidence is not None else self.confidence

        screen = self.screenshot()
        if screen is None:
            return None

        original_x, original_y = 0, 0
        if region:
            x, y, w, h = region
            h_screen, w_screen = screen.shape[:2]
            x1, y1 = max(0, int(x)), max(0, int(y))
            x2, y2 = min(w_screen, int(x + w)), min(h_screen, int(y + h))
            if x1 >= x2 or y1 >= y2:
                return None
            screen = screen[y1:y2, x1:x2]
            original_x, original_y = x1, y1
        else:
            original_x, original_y = 0, 0

        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            return None

        if template.shape[0] < 5 or template.shape[1] < 5:
            return None

        if screen.shape[0] < template.shape[0] or screen.shape[1] < template.shape[1]:
             return None

        try:
            result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            if max_val >= conf:
                center_x = original_x + max_loc[0] + template.shape[1] // 2
                center_y = original_y + max_loc[1] + template.shape[0] // 2
                return (center_x, center_y)
        except cv2.error as e:
            return None
        except Exception as e:
            print(f"Netikėta klaida find_on_screen ieškant {os.path.basename(template_path)}: {e}")
            return None

        return None

    def locate_all_on_screen(self, template_path, region=None, confidence=None):
        conf = confidence if confidence is not None else self.confidence
        try:
            locations = list(pyautogui.locateAllOnScreen(
                template_path,
                region=region,
                confidence=conf
            ))
            return locations
        except pyautogui.ImageNotFoundException:
            return []
        except Exception as e:
            print(f"Klaida locate_all_on_screen ieškant {os.path.basename(template_path)}: {e}")
            return []