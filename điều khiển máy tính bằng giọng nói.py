import os
import sys
import time
import io
import webbrowser
import wikipedia
import pyautogui
import pyttsx3
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf

# Wikipedia language setup
wikipedia.set_lang('vi')

# Windows console encoding fix for Vietnamese
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stdin.encoding != 'utf-8':
    sys.stdin.reconfigure(encoding='utf-8')

# Initialize Text-to-Speech engine
try:
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    # Try to find a Vietnamese voice if available, otherwise use default
    for voice in voices:
        if "vietnam" in voice.name.lower():
            engine.setProperty('voice', voice.id)
            break
    engine.setProperty('rate', 180)  # Speed of speech
except Exception as e:
    print(f"Không thể khởi động hệ thống giọng nói: {e}")
    engine = None

def speak(text):
    """Assistant speaks the given text."""
    print(f"Trợ lý: {text}")
    if engine:
        engine.say(text)
        engine.runAndWait()

def listen():
    """
    Listens to voice for 5 seconds using sounddevice and recognizes using Google Web Speech API.
    """
    recognizer = sr.Recognizer()
    samplerate = 16000
    duration = 5
    
    print("\n[Đang nghe...] (Hãy nói lệnh của bạn)")
    try:
        # Record audio
        recording = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
        sd.wait()
        
        print("[Đang xử lý...]")
        
        # Convert to buffer for SpeechRecognition
        wav_buffer = io.BytesIO()
        sf.write(wav_buffer, recording, samplerate, format='wav')
        wav_buffer.seek(0)
        
        with sr.AudioFile(wav_buffer) as source:
            audio_data = recognizer.record(source)
            
        # Recognize using Google API (requires internet)
        text = recognizer.recognize_google(audio_data, language="vi-VN")
        print(f">> Bạn: {text}")
        return text.lower()
        
    except sr.UnknownValueError:
        # No voice detected or not understood
        return ""
    except Exception as e:
        print(f"Lỗi nhận dạng: {e}")
        return ""

def execute_command(command):
    """
    Parses and executes the voice command.
    """
    if not command:
        return

    # 1. Opening Applications
    if "mở chrome" in command or "mở trình duyệt" in command:
        speak("Đang mở trình duyệt Google Chrome.")
        webbrowser.open("https://www.google.com")
        
    elif "mở máy tính" in command:
        speak("Đang mở ứng dụng máy tính.")
        os.system('calc')
        
    elif "mở notepad" in command or "mở ghi chú" in command:
        speak("Đang mở phần mềm ghi chú Notepad.")
        os.system('notepad')

    elif "mở word" in command:
        speak("Đang mở Microsoft Word.")
        os.system('start winword')

    elif "mở excel" in command:
        speak("Đang mở Microsoft Excel.")
        os.system('start excel')

    elif "mở powerpoint" in command:
        speak("Đang mở Microsoft PowerPoint.")
        os.system('start powerpnt')

    elif "mở access" in command:
        speak("Đang mở Microsoft Access.")
        os.system('start msaccess')

    elif "mở edge" in command or "mở trình duyệt edge" in command:
        speak("Đang mở trình duyệt Microsoft Edge.")
        os.system('start msedge')

    elif "mở vscode" in command or "mở visual studio code" in command:
        speak("Đang mở Visual Studio Code.")
        os.system('code')

    # 2. Searching
    elif "tìm kiếm" in command:
        query = command.split("tìm kiếm", 1)[1].strip()
        if query:
            speak(f"Đang tìm kiếm {query} trên Google.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("Bạn muốn tìm kiếm điều gì?")
            
    elif "tra cứu" in command:
        query = command.split("tra cứu", 1)[1].strip()
        if query:
            speak(f"Đang tra cứu thông tin về {query} trên Wikipedia.")
            try:
                summary = wikipedia.summary(query, sentences=2)
                print(f"Kết quả: {summary}")
                speak(summary)
            except Exception as e:
                speak("Xin lỗi, tôi không tìm thấy thông tin này.")
        else:
            speak("Bạn muốn tra cứu về ai hoặc cái gì?")

    # 3. System Controls (PyAutoGUI)
    elif "chụp ảnh màn hình" in command:
        speak("Đang chụp ảnh màn hình.")
        screenshot = pyautogui.screenshot()
        filename = f"screenshot_{int(time.time())}.png"
        screenshot.save(filename)
        speak(f"Đã lưu ảnh màn hình với tên {filename}")
        
    elif "tăng âm lượng" in command:
        speak("Đang tăng âm lượng.")
        for _ in range(5):
            pyautogui.press("volumeup")
            
    elif "giảm âm lượng" in command:
        speak("Đang giảm âm lượng.")
        for _ in range(5):
            pyautogui.press("volumedown")
            
    elif "thời gian" in command or "mấy giờ" in command:
        t = time.strftime("%H:%M:%S", time.localtime())
        speak(f"Bây giờ là {t}")

    # 4. Exit
    elif "thoát" in command or "tạm biệt" in command or "dừng lại" in command:
        speak("Chào tạm biệt bạn. Hẹn gặp lại!")
        sys.exit(0)
        
    else:
        # Optional: Basic interaction
        if "xin chào" in command:
            speak("Xin chào! Tôi có thể giúp gì cho bạn?")
        else:
            print(f"Hệ thống chưa hỗ trợ lệnh này: {command}")

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("==============================================")
    print("===  HỆ THỐNG ĐIỀU KHIỂN MÁY TÍNH  ===")
    print("===        BẰNG GIỌNG NÓI AI       ===")
    print("==============================================")
    speak("Hệ thống đã sẵn sàng. Hãy nói lệnh của bạn.")
    
    while True:
        try:
            cmd = listen()
            if cmd:
                execute_command(cmd)
            time.sleep(0.5)
        except KeyboardInterrupt:
            speak("Tạm biệt.")
            break
        except Exception as e:
            print(f"Đã xảy ra lỗi: {e}")

if __name__ == "__main__":
    main()
