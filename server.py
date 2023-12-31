import socket
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


print("[SERVER]: STARTED")
server_address = ('127.0.0.1', 12345)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(server_address) # Server
sock.listen(5)

# Deskop Show
class Dekstop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        

    def ChangeImage(self, conn):
        try:
            while True:
                img = ImageGrab.grab()
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                conn.send(img_bytes.getvalue())
        except:
            conn.close()
        

    def Mouse_solving(self, mouse_case, x, y, action, button):
        if mouse_case.startswith("on_move"):
            pyautogui.moveTo(x, y)
        elif mouse_case.startswith("on_click"):
            if action.startwith("Pressed"):
                pyautogui.mouseDown(button)
            elif action.startwith("Released"):
                pyautogui.mouseUp(button)
        elif mouse_case.startswith("on_scroll"):
            pyautogui.scroll(x, y)

    def Character_solving(self, char, action):
        if action.startwwith("on_press"):
            pyautogui.keyDown(char)
        elif action.startwwith("on_release"):
            pyautogui.keyDown(char)

        


    
    def input_from_deviece(self, conn):
        try:
            while(True):
                data_nhận = conn.recv(9999999)
                data = data_nhận.decode('utf-8')
                if data.startswith("keyboard"):
                    key, char, action = data.split(',')
                    self.Character_solving(char)

                elif data.startswith("mouse"):
                    key, mouse_case, x, y, action, button,  = data.split(',')
                    self.Mouse_solving(mouse_case, x, y, action, button)
               
     
        except ConnectionResetError:
            QMessageBox.about(self, "ERROR", "[SERVER]: The remote host forcibly terminated the existing connection!")
            


    def initUI(self):
        while True:
            conn, addr = sock.accept()
            with conn:
                print(f"Connected by {addr}")
                try:
                    # Luồng gửi data
                    self.output_thread = Thread(target = self.ChangeImage(conn), daemon = True)
                    self.output_thread.start()                     
                    # Luông nhận data
                    self.input_thread = Thread(target = self.input_from_deviece(conn), daemon = True)
                    self.input_thread.start()
                except:
                    print(f"Connection with {addr} closed")
                    
        # Luông gửi data 
        
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Dekstop()
    ex.show()
    sys.exit(app.exec())
    

