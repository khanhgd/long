
import sys
import os
import time
import datetime
import threading
import io
import urllib.parse
import webbrowser
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import pygame
from gtts import gTTS

# --- FIX ENCODING CHO WINDOWS CONSOLE ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr.reconfigure(encoding='utf-8')

# --- CÁC HÀM CƠ BẢN ---

def speak(text, lang='vi'):
    """Chuyển đổi văn bản thành giọng nói (gTTS) và phát trực tiếp qua pygame."""
    try:
        # Xóa dòng hiển thị đồng hồ hiện tại (nếu có) để in không đè chéo
        sys.stdout.write("\r" + " " * 80 + "\r")
        print(f"🤖 Bot: {text}")

        tts = gTTS(text=text, lang=lang, slow=False)
        temp_file = "temp_response.mp3"
        tts.save(temp_file)
        
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.mixer.quit()
        time.sleep(0.2)
        
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
    except Exception as e:
        print(f"[!] Lỗi phát giọng nói: {e}")

def listen():
    """Lắng nghe qua sounddevice trong 5 giây và nhận diện."""
    recognizer = sr.Recognizer()
    samplerate = 16000
    duration = 5
    
    sys.stdout.write("\r" + " " * 80 + "\r")
    print("🎙️ Đang nghe... (trong 5 giây)")
    
    try:
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        
        sys.stdout.write("\r" + " " * 80 + "\r")
        print("⏳ Đang nhận diện...")
        
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, recording, samplerate, format='wav')
        wav_buffer.seek(0)
        
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)
            
        text = recognizer.recognize_google(audio_data, language="vi-VN")
        sys.stdout.write("\r" + " " * 80 + "\r")
        print(f"🗣️ Bạn nói: '{text}'")
        return text.lower()
        
    except sr.UnknownValueError:
        pass # Tránh spam khi môi trường im lặng
    except Exception as e:
        print(f"[!] Lỗi mic: {e}")
    return ""

def get_current_time_response():
    """Trả về chuỗi thời gian hiện tại."""
    now = datetime.datetime.now()
    hour = now.hour
    minute = now.minute
    
    if 0 <= hour < 12:
        period = "sáng"
    elif 12 <= hour < 18:
        period = "chiều"
    else:
        period = "tối"
        
    hour_12 = hour if hour <= 12 else hour - 12
    if hour_12 == 0:
        hour_12 = 12
        
    if minute == 0:
        return f"Bây giờ là {hour_12} giờ {period}."
    else:
        return f"Bây giờ là {hour_12} giờ {minute} phút {period}."

def search_on_chrome(query):
    """Mở Google Chrome tìm kiếm."""
    sys.stdout.write("\r" + " " * 80 + "\r")
    print(f"🚀 Mở trình duyệt tìm kiếm: {query}")
    url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
    
    if sys.platform == 'win32':
        try:
            chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
            webbrowser.get(chrome_path).open(url)
        except webbrowser.Error:
            try:
                chrome_path_x86 = "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s"
                webbrowser.get(chrome_path_x86).open(url)
            except webbrowser.Error:
                webbrowser.open(url)
    elif sys.platform.startswith('linux'):
        try:
            chrome_path = "/usr/bin/google-chrome %s"
            webbrowser.get(chrome_path).open(url)
        except webbrowser.Error:
            webbrowser.open(url)
    else:
        webbrowser.open(url)

def execute_command(command):
    """Mở các ứng dụng phổ biến trên Windows và Linux."""
    is_win = sys.platform == 'win32'
    is_linux = sys.platform.startswith('linux')

    if "powerpoint" in command or "trình chiếu" in command:
        speak("Đang mở PowerPoint")
        if is_win: os.system("start powerpnt")
        elif is_linux: os.system("libreoffice --impress &")
    elif "word" in command or "văn bản" in command:
        speak("Đang mở Microsoft Word")
        if is_win: os.system("start winword")
        elif is_linux: os.system("libreoffice --writer &")
    elif "excel" in command or "bảng tính" in command:
        speak("Đang mở Excel")
        if is_win: os.system("start excel")
        elif is_linux: os.system("libreoffice --calc &")
    elif "chrome" in command or "trình duyệt" in command:
        speak("Đang mở Google Chrome")
        if is_win: os.system("start chrome")
        elif is_linux: os.system("google-chrome &")
    elif "máy tính" in command or "calculator" in command:
        speak("Đang mở ứng dụng Máy tính")
        if is_win: os.system("start calc")
        elif is_linux: os.system("gnome-calculator &")
    elif "notepad" in command or "ghi chú" in command:
        speak("Đang mở Notepad")
        if is_win: os.system("start notepad")
        elif is_linux: os.system("gedit &")
    else:
        speak("Tôi chưa được dạy cách mở ứng dụng này.")

def display_realtime_clock(stop_event):
    """Luồng hiển thị đồng hồ thời gian thực tránh lag terminal."""
    while not stop_event.is_set():
        now = datetime.datetime.now()
        time_str = now.strftime("%d/%m/%Y %H:%M:%S")
        sys.stdout.write(f"\r🕒 [Hệ thống]: {time_str}  ")
        sys.stdout.flush()
        time.sleep(0.5)

def display_help():
    """Hiển thị menu trợ giúp đầu chu trình với ASCII art kocuziab AI."""
    os.system('cls' if os.name == 'nt' else 'clear')

    # ANSI color codes
    RED = "\033[91m"
    BRIGHT_RED = "\033[1;91m"
    DARK_RED = "\033[31m"
    YELLOW = "\033[93m"
    WHITE = "\033[97m"
    RESET = "\033[0m"

    print(BRIGHT_RED + r"""
    ██╗  ██╗ ██████╗  ██████╗██╗   ██╗███████╗██╗ █████╗ ██████╗ 
    ██║ ██╔╝██╔═══██╗██╔════╝██║   ██║╚══███╔╝██║██╔══██╗██╔══██╗
    █████╔╝ ██║   ██║██║     ██║   ██║  ███╔╝ ██║███████║██████╔╝
    ██╔═██╗ ██║   ██║██║     ██║   ██║ ███╔╝  ██║██╔══██║██╔══██╗
    ██║  ██╗╚██████╔╝╚██████╗╚██████╔╝███████╗██║██║  ██║██████╔╝
    ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═╝╚═════╝ """ + 
          YELLOW + r"""
                                          █████╗ ██╗
                                         ██╔══██╗██║
                                         ███████║██║
                                         ██╔══██║██║
                                         ██║  ██║██║
                                         ╚═╝  ╚═╝╚═╝
    """ + RESET)

    print(DARK_RED + "    ─" * 20 + RESET)
    print(YELLOW + "        AI Assistant system developed by Khanh 2007" + RESET)
    print(DARK_RED + "    ─" * 20 + RESET)
    print()
    print(WHITE + "=" * 64 + RESET)
    print(RED + "  HE THONG TRO LY AO TONG HOP" + RESET)
    print(WHITE + "=" * 64 + RESET)
    print(f"  {WHITE}[ 🚀 TÌM KIẾM  ] {RESET}'tìm kiếm [từ khóa]', 'mở Chrome'")
    print(f"  {WHITE}[ 💬 GIAO TIẾP  ] {RESET}'xin chào', 'có gì vui', 'mấy giờ rồi'")
    print(f"  {WHITE}[ ⚙️  ĐIỀU KHIỂN ] {RESET}'mở word', 'mở máy tính', 'mở notepad'")
    print(f"  {WHITE}[ 🛑 HỆ THỐNG  ] {RESET}'thoát', 'tạm biệt', 'tắt hệ thống'")
    print(WHITE + "-" * 64 + RESET + "\n")

# --- LUỒNG CHÍNH ---

def main():
    display_help()
    
    stop_clock_event = threading.Event()
    clock_thread = threading.Thread(target=display_realtime_clock, args=(stop_clock_event,), daemon=True)
    clock_thread.start()
    
    now = datetime.datetime.now()
    if 0 <= now.hour < 12:
        greeting = "Chào buổi sáng"
    elif 12 <= now.hour < 18:
        greeting = "Chào buổi chiều"
    else:
        greeting = "Chào buổi tối"
        
    speak(f"{greeting}! Hệ thống trợ lý ảo Kocuziab AI đã sẵn sàng. Bạn có cần tôi giúp gì không?")
    
    try:
        while True:
            # Nghe liên tục
            command = listen()
            
            if not command:
                continue
            
            # --- XỬ LÝ LỆNH ---
            if "thoát" in command or "tạm biệt" in command or "tắt" in command:
                speak("Chương trình kết thúc. Chào tạm biệt bạn!")
                break
                
            elif "xin chào" in command:
                speak("Chào bạn! Chúc bạn một ngày học tập và làm việc thật tốt.")
                
            elif "có gì vui" in command:
                speak("Thế giới AI mỗi ngày đều tiến bộ, tôi cũng đang tốt lên từng ngày!")
                
            elif "trợ giúp" in command:
                speak("Tôi có thể giúp bạn mở ứng dụng, tìm kiếm thông tin và xem giờ.")
                display_help()
                
            elif "giờ" in command or "thời gian" in command:
                response = get_current_time_response()
                speak(response)
                
            elif "mở" in command:
                if "chrome" in command and "mở chrome" == command.strip():
                    speak("Đang mở trình duyệt Google Chrome")
                    webbrowser.open("https://www.google.com")
                else:
                    execute_command(command)
                
            elif "tìm kiếm" in command:
                keyword = command.split("tìm kiếm", 1)[1].strip()
                if keyword:
                    speak(f"Đang tìm kiếm thông tin về {keyword}")
                    search_on_chrome(keyword)
                else:
                    speak("Bạn muốn tôi tìm kiếm thông tin gì?")
            else:
                # Revert to default state when command is not recognized
                sys.stdout.write("\r" + " " * 80 + "\r")
                print("What do you need? No spam.")

    except KeyboardInterrupt:
        sys.stdout.write("\r" + " " * 80 + "\r")
        print("\nĐã ngắt hệ thống đột ngột. Tạm biệt!")
        
    finally:
        stop_clock_event.set()

if __name__ == "__main__":
    main()
