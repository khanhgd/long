"""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ███████╗██╗██████╗ ███████╗    ████████╗ ██████╗  ██████╗   ║
║    ██╔════╝██║██╔══██╗██╔════╝       ██╔══╝██╔═══██╗██╔═══██╗  ║
║    █████╗  ██║██████╔╝█████╗         ██║   ██║   ██║██║   ██║  ║
║    ██╔══╝  ██║██╔══██╗██╔══╝         ██║   ██║   ██║██║   ██║  ║
║    ██║     ██║██║  ██║███████╗       ██║   ╚██████╔╝╚██████╔╝  ║
║    ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝       ╚═╝    ╚═════╝  ╚═════╝   ║
║                                                                  ║
║   ██████╗ ███████╗████████╗███████╗ ██████╗████████╗██╗ ██████╗ ║
║   ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██║██╔═══██╗║
║   ██║  ██║█████╗     ██║   █████╗  ██║        ██║   ██║██║   ██║║
║   ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║   ██║██║   ██║║
║   ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║   ██║╚██████╔╝║
║   ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝   ╚═╝ ╚═════╝ ║
║                                                                  ║
║          [ FLAME RECOGNITION & ALERT SYSTEM v1.0 ]              ║
║                                                                  ║
║       ██╗  ██╗██╗  ██╗ █████╗ ███╗  ██╗██╗  ██╗                 ║
║       ██║ ██╔╝██║  ██║██╔══██╗████╗ ██║██║  ██║                 ║
║       █████╔╝ ███████║███████║██╔██╗██║███████║                 ║
║       ██╔═██╗ ██╔══██║██╔══██║██║╚████║██╔══██║                 ║
║       ██║  ██╗██║  ██║██║  ██║██║  ███║██║  ██║                 ║
║       ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚══╝╚═╝  ╚═╝                 ║
║                                                                  ║
║            >> Developer: KHANH  |  Year: 2007 <<                ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

  ASCII FORMAT  |  He thong nhan dien ngon lua tich hop hoan chinh
  Camera Module + Flame Recognition + Voice Alert & Notification System
"""

# ════════════════════════════════════════════════════════════════════
#  IMPORTS
# ════════════════════════════════════════════════════════════════════
import cv2
import numpy as np
import time
import threading
import logging
import os
from datetime import datetime
from pathlib import Path
from collections import deque
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from gtts import gTTS
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame

try:
    import winsound
    HAS_WINSOUND = True
except ImportError:
    HAS_WINSOUND = False


# ════════════════════════════════════════════════════════════════════
#  ASCII BANNER (in ra terminal khi khởi động)
# ════════════════════════════════════════════════════════════════════
# ANSI color codes
BRIGHT_RED = "\033[1;91m"
DARK_RED = "\033[31m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def print_banner():
    """In banner ASCII ra terminal."""
    os.system("cls" if os.name == "nt" else "clear")
    print(BRIGHT_RED + r"""
       )                          )        
    ( /(          (             ( /(   (    
    )\())    (    )\ )   (      )\())  )\   
   ((_)\    ))\  (()/(  ))\   ((_)\  ((_)  
    _((_)  /((_)  )(_))/((_)   _((_)  _    
   | || | (_))   | |_ (_))    |_  /  (_)   
   | __ | / -_)  |  _| / -_)    / /   _    
   |_||_| \___|   \__| \___|   /___| (_)   
    """ + RESET)

    print(BRIGHT_RED + r"""
                        ███████╗██╗██████╗ ███████╗
                        ██╔════╝██║██╔══██╗██╔════╝
                        █████╗  ██║██████╔╝█████╗  
                        ██╔══╝  ██║██╔══██╗██╔══╝  
                        ██║     ██║██║  ██║███████╗
                        ╚═╝     ╚═╝╚═╝  ╚═╝╚══════╝""" + 
          YELLOW + r"""
    ██████╗ ███████╗████████╗███████╗██████╗ ████████╗ ██████╗ ██████╗ 
    ██╔══██╗██╔════╝╚══██╔══╝██╔════╝██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
    ██║  ██║█████╗     ██║   █████╗  ██║        ██║   ██║   ██║██████╔╝
    ██║  ██║██╔══╝     ██║   ██╔══╝  ██║        ██║   ██║   ██║██╔══██╗
    ██████╔╝███████╗   ██║   ███████╗╚██████╗   ██║   ╚██████╔╝██║  ██║
    ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝ ╚═════╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
    """ + RESET)

    print(DARK_RED + "    ─" * 20 + RESET)
    print(YELLOW + "        Fire detection system developed by Khanh 2007" + RESET)
    print(DARK_RED + "    ─" * 20 + RESET)
    
    print("  [INFO] He thong dang khoi dong...")
    print("  [INFO] Nhan 'q' de thoat | 'm' de bat/tat mask")
    print("  " + "=" * 40)
    print()


# ════════════════════════════════════════════════════════════════════
#  MODULE 1 – CAMERA
#  (dua tren camera.py – hien thi anh thermal-like)
# ════════════════════════════════════════════════════════════════════
class CameraModule:
    """Quan ly viec mo va doc frame tu camera."""

    def __init__(self, index: int = 0, width: int = 640, height: int = 480):
        self.index  = index
        self.width  = width
        self.height = height
        self.cap    = None

    def open(self) -> bool:
        self.cap = cv2.VideoCapture(self.index)
        if not self.cap.isOpened():
            print(f"  [LOI] Khong mo duoc camera (index={self.index})")
            return False
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH,  self.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        print(f"  [OK ] Camera {self.index} da mo ({self.width}x{self.height})")
        return True

    def read(self):
        """Doc mot frame. Tra ve (True, frame) hoac (False, None)."""
        if self.cap is None:
            return False, None
        return self.cap.read()

    def get_thermal_preview(self, frame: np.ndarray) -> np.ndarray:
        """Chuyen frame thanh anh thermal-like (COLORMAP_INFERNO)."""
        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        thermal = cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)
        return thermal

    def release(self):
        if self.cap:
            self.cap.release()
            self.cap = None


# ════════════════════════════════════════════════════════════════════
#  MODULE 2 – FIRE NOTIFICATION SYSTEM
#  (dua tren he thong thong bao lua.py)
# ════════════════════════════════════════════════════════════════════
LOG_DIR  = Path(__file__).parent / "logs"
LOG_FILE = LOG_DIR / "fire_events.log"
LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level    = logging.INFO,
    format   = "%(asctime)s [%(levelname)s] %(message)s",
    handlers = [
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
_logger = logging.getLogger("KhanhFireSystem")


def text_to_speech(text, lang='vi'):
    """Chuyển đổi văn bản thành giọng nói và phát trực tiếp (hỗ trợ Tiếng Việt)."""
    try:
        # 1. Tạo file âm thanh từ văn bản dùng Google Text-to-Speech
        tts = gTTS(text=text, lang=lang, slow=False)
        temp_file = "temp_alert_fire.mp3"
        tts.save(temp_file)
        
        # 2. Sử dụng pygame để phát âm thanh
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        # 3. Chờ cho đến khi âm thanh phát xong
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        # 4. Giải phóng file
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        time.sleep(0.1)
        
        # 5. Xóa file tạm
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception as e:
                pass
    except Exception as e:
        _logger.error(f"Lỗi khi phát giọng nói: {e}")


class FireNotificationSystem:
    """Phat canh bao am thanh va ghi log khi phat hien lua."""

    ALERT_COOLDOWN = 7.0   # Tăng cooldown để đọc hết câu cảnh báo
    EMAIL_COOLDOWN = 60.0  # Thoi gian tro (cooldown) giua cac email: 60 giay de tranh spam email

    def __init__(self, target_email="your_target_email@gmail.com"):
        self._last_alert   = 0.0
        self._last_email   = 0.0
        self._alert_thread = None
        self._email_thread = None
        self._active       = False
        self.target_email  = target_email

    def _play_alert(self):
        # Phát bíp trước
        if HAS_WINSOUND:
            for _ in range(3):
                winsound.Beep(1000, 300)
                time.sleep(0.1)
        else:
            print("\a\a\a", end="", flush=True)
            
        # Đọc cảnh báo bằng giọng nói
        text_to_speech("Cảnh báo khẩn cấp, phát hiện có cháy. Yêu cầu kiểm tra ngay lập tức.")

    def _send_email_alert(self, confidence, location):
        """Gui email canh bao su dung tai khoan Gmail."""
        # De bao mat hon, ban nen dung Environment Variables
        gmail_user = os.getenv("GMAIL_USER", "your_email@gmail.com")
        gmail_app_password = os.getenv("GMAIL_APP_PASSWORD", "your_app_password")

        if gmail_user == "your_email@gmail.com" or gmail_app_password == "your_app_password":
            _logger.warning("Chua thiet lap GMAIL_USER/GMAIL_APP_PASSWORD. Bo qua viec gui email.")
            return

        msg = MIMEMultipart()
        msg['From'] = gmail_user
        msg['To'] = self.target_email
        msg['Subject'] = "[KHAN CAP] Phat hien lua tu camera quan sat!"

        body = f"""
HE THONG PHAT HIEN LUA KHANH 2007
-----------------------------------
CANH BAO KHAN CAP! Phat hien co chay.
Vi tri: {location}
Do tin cay: {confidence * 100:.0f}%
Thoi gian: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
Yeu cau kiem tra khu vuc ngay lap tuc!
        """
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        try:
            # Giao thiep voi may chu Gmail
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_app_password)
            text = msg.as_string()
            server.sendmail(gmail_user, self.target_email, text)
            server.quit()
            _logger.info(f"Da gui email canh bao toi {self.target_email}")
        except Exception as e:
            _logger.error(f"Loi khi gui email canh bao: {e}")

    def trigger(self, confidence: float = 1.0, location: str = "Camera"):
        now = time.time()
        
        # Phat hien lua va thong bao am thanh xuyen suot
        if now - self._last_alert >= self.ALERT_COOLDOWN:
            self._last_alert = now
            self._active     = True
            _logger.warning(
                "PHAT HIEN LUA! | Do tin cay: %.0f%% | Vi tri: %s",
                confidence * 100, location,
            )
            if self._alert_thread is None or not self._alert_thread.is_alive():
                self._alert_thread = threading.Thread(
                    target=self._play_alert, daemon=True
                )
                self._alert_thread.start()

        # Gui tin nhan Email canh bao (co the co timer doc lap de khong bi spam lien tuc)
        if now - self._last_email >= self.EMAIL_COOLDOWN:
            self._last_email = now
            if self._email_thread is None or not self._email_thread.is_alive():
                self._email_thread = threading.Thread(
                    target=self._send_email_alert, args=(confidence, location), daemon=True
                )
                self._email_thread.start()

    def clear(self):
        if self._active:
            _logger.info("AN TOAN – Ngon lua da tat.")
            self._active = False

    def is_active(self) -> bool:
        return self._active


# ════════════════════════════════════════════════════════════════════
#  MODULE 3 – FLAME RECOGNITION ENGINE
#  (dua tren he thong nhan dien ngon lua.py)
# ════════════════════════════════════════════════════════════════════

# ── Nguong mau lua (HSV) ─────────────────────────────────────────────────────
LOWER_FIRE_1 = np.array([0,   120, 150])
UPPER_FIRE_1 = np.array([15,  255, 255])
LOWER_FIRE_2 = np.array([160, 120, 150])
UPPER_FIRE_2 = np.array([180, 255, 255])
LOWER_FIRE_3 = np.array([16,  120, 150])
UPPER_FIRE_3 = np.array([35,  255, 255])

MIN_CONTOUR_AREA    = 500
FIRE_CONFIRM_FRAMES = 5
HISTORY_LEN         = 30

COLOR_FIRE    = (0,   80,  255)
COLOR_SAFE    = (80,  255, 80)
COLOR_TEXT    = (255, 255, 255)


class FlameRecognitionEngine:
    """Nhan dien ngon lua tu frame BGR."""

    def build_fire_mask(self, hsv: np.ndarray) -> np.ndarray:
        m1 = cv2.inRange(hsv, LOWER_FIRE_1, UPPER_FIRE_1)
        m2 = cv2.inRange(hsv, LOWER_FIRE_2, UPPER_FIRE_2)
        m3 = cv2.inRange(hsv, LOWER_FIRE_3, UPPER_FIRE_3)
        mask = cv2.bitwise_or(m1, cv2.bitwise_or(m2, m3))
        k    = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN,  k, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, k, iterations=2)
        return mask

    def analyze_contours(self, mask: np.ndarray, frame_area: int):
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)
        detections = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < MIN_CONTOUR_AREA:
                continue
            x, y, w, h   = cv2.boundingRect(cnt)
            aspect_ratio  = h / (w + 1e-5)
            hull          = cv2.convexHull(cnt)
            hull_area     = cv2.contourArea(hull)
            solidity      = area / (hull_area + 1e-5)
            ratio_score   = min(aspect_ratio / 2.0, 1.0)
            area_score    = min(area / (frame_area * 0.3), 1.0)
            solid_score   = max(1.0 - abs(solidity - 0.6) / 0.6, 0.0)
            confidence    = (ratio_score * 0.4 + area_score * 0.3
                             + solid_score * 0.3)
            detections.append((cnt, (x, y, w, h), min(confidence, 1.0)))
        detections.sort(key=lambda d: cv2.contourArea(d[0]), reverse=True)
        return detections

    def process(self, frame: np.ndarray):
        """Phan tich frame, tra ve (mask, danh_sach_vung_lua)."""
        blurred = cv2.GaussianBlur(frame, (7, 7), 0)
        hsv     = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        mask    = self.build_fire_mask(hsv)
        h, w    = frame.shape[:2]
        dets    = self.analyze_contours(mask, h * w)
        return mask, dets


# ════════════════════════════════════════════════════════════════════
#  HUD RENDERER
# ════════════════════════════════════════════════════════════════════

def draw_hud(frame: np.ndarray, fire_detected: bool, detections: list,
             fps: float, history: deque, thermal_mode: bool) -> np.ndarray:
    h, w = frame.shape[:2]

    # ── Thanh trang thai ──────────────────────────────────────────────────
    bar_color = COLOR_FIRE if fire_detected else COLOR_SAFE
    cv2.rectangle(frame, (0, 0), (w, 56), bar_color, -1)
    cv2.rectangle(frame, (0, 0), (w, 56), (255, 255, 255), 1)

    status = "!! PHAT HIEN LUA !!" if fire_detected else ">> AN TOAN <<"
    cv2.putText(frame, status, (12, 38),
                cv2.FONT_HERSHEY_SIMPLEX, 1.1, COLOR_TEXT, 2, cv2.LINE_AA)

    mode_label = "[THERMAL]" if thermal_mode else "[NORMAL]"
    cv2.putText(frame, mode_label, (w - 155, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_TEXT, 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS:{fps:.1f}", (w - 130, 48),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, COLOR_TEXT, 2, cv2.LINE_AA)

    # ── Watermark developer ────────────────────────────────────────────────
    wm = "KHANH 2007 | ASCII FORMAT"
    cv2.putText(frame, wm, (10, h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)

    # ── Ve contour & bbox ─────────────────────────────────────────────────
    for cnt, (x, y, bw, bh), conf in detections:
        cv2.drawContours(frame, [cnt], -1, COLOR_FIRE, 2)
        cv2.rectangle(frame, (x, y), (x + bw, y + bh), COLOR_FIRE, 2)
        label = f"LUA {conf*100:.0f}%"
        (lw, lh), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        ly = max(y - 8, lh + 62)
        cv2.rectangle(frame, (x, ly - lh - 4), (x + lw + 4, ly + 2), COLOR_FIRE, -1)
        cv2.putText(frame, label, (x + 2, ly - 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, COLOR_TEXT, 1, cv2.LINE_AA)

    # ── Do thi lich su (goc duoi phai) ────────────────────────────────────
    gw, gh = 170, 55
    gx, gy = w - gw - 10, h - gh - 30
    cv2.rectangle(frame, (gx, gy), (gx + gw, gy + gh), (20, 20, 20), -1)
    cv2.rectangle(frame, (gx, gy), (gx + gw, gy + gh), (100, 100, 100), 1)
    cv2.putText(frame, "Lich su phat hien", (gx + 4, gy + 14),
                cv2.FONT_HERSHEY_SIMPLEX, 0.36, (160, 160, 160), 1)
    hist = list(history)
    if hist:
        bu = gw / len(hist)
        for i, val in enumerate(hist):
            bx  = int(gx + i * bu)
            bh2 = int((gh - 18) * val)
            c   = COLOR_FIRE if val > 0.5 else COLOR_SAFE
            cv2.rectangle(frame,
                          (bx, gy + gh - bh2),
                          (int(bx + bu - 1), gy + gh), c, -1)

    # ── So vung lua ───────────────────────────────────────────────────────
    cv2.putText(frame, f"Vung lua: {len(detections)}", (10, h - 38),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_TEXT, 1, cv2.LINE_AA)

    return frame


# ════════════════════════════════════════════════════════════════════
#  MAIN: TICH HOP TAT CA MODULE
# ════════════════════════════════════════════════════════════════════

def run(camera_index: int = 0):
    print_banner()

    camera   = CameraModule(camera_index)
    engine   = FlameRecognitionEngine()
    notifier = FireNotificationSystem()

    if not camera.open():
        return

    show_mask     = False
    thermal_mode  = False
    fire_counter  = 0
    fire_detected = False
    fps_counter   = 0
    fps_start     = time.time()
    fps           = 0.0
    history       = deque([0.0] * HISTORY_LEN, maxlen=HISTORY_LEN)

    print("  [RUN] Vong lap chinh bat dau...\n")

    while True:
        ret, frame = camera.read()
        if not ret:
            print("  [LOI] Khong doc duoc frame.")
            break

        # Chon frame hien thi: thermal hoac binh thuong
        display_frame = (camera.get_thermal_preview(frame)
                         if thermal_mode else frame.copy())

        # Phan tich ngon lua (luon dung frame goc BGR)
        mask, detections = engine.process(frame)

        # Logic xac nhan (chong bao dong gia)
        if detections:
            fire_counter = min(fire_counter + 1, FIRE_CONFIRM_FRAMES + 5)
        else:
            fire_counter = max(fire_counter - 1, 0)

        prev_state    = fire_detected
        fire_detected = fire_counter >= FIRE_CONFIRM_FRAMES

        # Thong bao
        if fire_detected and detections:
            avg_conf = sum(c for _, _, c in detections) / len(detections)
            notifier.trigger(confidence=avg_conf, location=f"Camera {camera_index}")
        elif prev_state and not fire_detected:
            notifier.clear()

        # Cap nhat lich su
        hist_val = min(len(detections) / 3.0, 1.0) if detections else 0.0
        history.append(hist_val)

        # FPS
        fps_counter += 1
        elapsed = time.time() - fps_start
        if elapsed >= 1.0:
            fps = fps_counter / elapsed
            fps_counter = 0
            fps_start = time.time()

        # Ve HUD
        output = draw_hud(display_frame, fire_detected, detections,
                          fps, history, thermal_mode)
        cv2.imshow("KHANH 2007 | Fire Detection Tool", output)

        if show_mask:
            cv2.imshow("Fire Mask (DEBUG)", cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR))

        # Phim dieu khien
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            print("\n  [INFO] Thoat chuong trinh.")
            break
        elif key == ord('m'):
            show_mask = not show_mask
            if not show_mask:
                cv2.destroyWindow("Fire Mask (DEBUG)")
        elif key == ord('t'):
            thermal_mode = not thermal_mode
            mode_str = "THERMAL" if thermal_mode else "BINH THUONG"
            print(f"  [INFO] Che do hien thi: {mode_str}")

    camera.release()
    cv2.destroyAllWindows()
    print(f"  [LOG] Su kien da duoc luu tai: {LOG_FILE}")


# ════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    run(camera_index=0)
