import socket
import os
from os import getlogin
from PIL import Image, ImageGrab #Import thư viện ImageGrab từ Pillow để chụp ảnh màn hình.
import io
from io import BytesIO
import numpy as np
from random import randint
import pyautogui
from threading import Thread
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt, QThread, pyqtSignal
import time
from queue import Queue
import pickle

print("[SERVER]: STARTED")
server_address = ('172.16.26.138', 12345)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                
sock.bind(server_address) # Server  
sock.listen(5)

# Deskop Show
class Dekstop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def ChangeImage(self, conn): #_________________________________________________________________________________________
        try:
            while True:
                img = ImageGrab.grab()
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                data = {'type': 'image', 'data': img_bytes.getvalue()}
                serialized_data = pickle.dumps(data)
                conn.send(serialized_data)
        except:
            conn.close()

    # Thao tác server gửi file cho client_________________________________________________________________________________________
    def send_file_list(self, client_socket): # Gửi danh sách file trong ổ đĩa___________________________________________________________
        files = os.listdir('This PC:\\')
        data = {'type': 'file_list', 'data': files}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)


    def Queue_solving(self, queue_, conn): # Xử lí Queue______________________________________________________________________________
        try:
            print("Queue Started")
            while True:
                data = queue_.get()
                messages = data.split()  
                for message in messages:
                    if message:
                        print("Processing data:", message)
                        if message.startswith("mouse"):
                            key, mouse_case, x, y, action, button  = message.split(',')
                            self.Mouse_solving(mouse_case, x, y, action, button)
                        elif message.startswith("keyboard"):
                            key, charc, action = message.split(',')
                            self.Character_solving(charc, action, conn)
                        elif message['type'] == 'file_for_re':
                            self.Receive_file(message)
                        elif message['type'] == 'file_list_request':
                            self.send_file_list(conn)
        except Exception as e:
            print(e)
            print("Queue Error")

    def Mouse_solving(self, mouse_case, x, y, action, button): #___________________________________________________________
        try:
            if mouse_case.startswith("on_move"):
                pyautogui.moveTo(int(x), int(y))
            elif mouse_case.startswith("on_click"):
                if action.startswith("Pressed"):
                    if button in ('left', 'right', 'middle'):
                        pyautogui.mouseDown(button = button)
                elif action.startswith("Released"):
                    pyautogui.mouseUp(button = button)
            elif mouse_case.startswith("on_roll"):
                pyautogui.scroll(int(y) * 100)
        except:
            print("Mouse Error")

    def Character_solving(self, charc, action, conn): #______________________________________________________________________
        try:
            if action.startswith("on_press"):
                if charc.startswith("Key"):
                    _, charc = charc.split('.')
                    if(charc == "esc"):
                        conn.close()
                pyautogui.keyDown(charc)

            elif action.startswith("on_release"):
                if charc.startswith("Key"):
                    _, charc = charc.split('.')
                pyautogui.keyUp(charc)
        except:
            print("Keyboard Error")

    def Receive_file(self, data): # Nhận file từ client_______________________________________________________________________________________
        filename = data['file_name']
        file_content = data['file_content']
        filepath = os.path.join("D:\\", filename)
        with open(filepath, 'wb') as f:
            f.write(file_content)

    def initUI(self):
        self.MainProgram = Thread(target = self.Main_Program, daemon = True)
        self.MainProgram.start()
    
    def Main_Program(self):
        # Khởi tạo Queue để xử lí dữ liệu từ Client
        self.queue_ = Queue()

        while True:
            conn, addr = sock.accept()
            with conn:
                print("----------Connected----------")
                print(f"Connected by {addr}")
                # Luồng gửi data ảnh
                self.output_thread = Thread(target = lambda: self.ChangeImage(conn), daemon = True)
                self.output_thread.start()  
                # Luồng nhận data từ Queue
                self.input_thread = Thread(target = lambda: self.Queue_solving(self.queue_, conn), daemon = True)    
                self.input_thread.start()  
                try:
                    while(True):
                        data_nhận = conn.recv(99999)
                        data = data_nhận.decode('utf-8')
                        # print(data)
                        self.queue_.put(data)
                except Exception as e:
                    print(e)
                    print(f"Connection with {addr} closed")              
        
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    sys.exit(app.exec())
    
