import socket
import os
from PIL import Image, ImageGrab
import io
from io import BytesIO
import numpy as np
from random import randint
import pynput
from pynput.keyboard import Controller as KeyboardController, Key
from pynput.mouse import Controller as MouseController, Button
import traceback

import threading
from threading import Thread
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt, QThread, pyqtSignal
import struct
import pickle
from PyQt5.QtWidgets import QFileDialog

print("[SERVER]: STARTED")

server_address = ('192.168.0.103', 1234)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)                
sock.bind(server_address) # Server  
sock.listen(5)
keyboard = KeyboardController()
mouse = MouseController()

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
                img_data = img_bytes.getvalue()

                # Send the size of the image first
                conn.send(struct.pack('<L', len(img_data)))

                # Then send the image data
                conn.send(img_data)
        except:
            conn.close()       
    def Mouse_solving(self, data):
        try:
            if data['event_type'] == 'on_move':
                mouse.position = (int(data['x']), int(data['y']))
            elif data['event_type'] == 'on_click':
                if data['action'] == 'Pressed':
                    if data['button'] in ('left', 'right', 'middle'):
                        mouse.press(getattr(Button, data['button']))
                elif data['action'] == 'Released':
                    mouse.release(getattr(Button, data['button']))
            elif data['event_type'] == 'on_scroll':
                mouse.scroll(0, int(data['dy'])*10)
        except Exception as e:
            print("Mouse Error: ", e)
    def Character_solving(self, data):
        try:
            if data['action'] == 'on_press':
                keyboard.press(data['key_name'])
            elif data['action'] == 'on_release':
                keyboard.release(data['key_name'])

        except Exception as e:
            print("Keyboard Error: ", traceback.format_exc())
    
    def Receive_file(self, data):
        filename, _ = QFileDialog.getSaveFileName(self, "Lưu file", data['file_name'], options=QFileDialog.DontUseNativeDialog)
        if filename:
            file_content = data['file_content']
            with open(filename, 'wb') as f:
                f.write(file_content)
 
    def initUI(self):
        self.MainProgram = Thread(target = self.Main_Program, daemon = True)
        self.MainProgram.start()
    
    def Main_Program(self):
        while True:
            conn, addr = sock.accept()
            with conn:
                print("----------Connected----------")
                print(f"Connected by {addr}")
                # Luồng gửi data ảnh
                self.output_thread = Thread(target = lambda: self.ChangeImage(conn), daemon = True)
                self.output_thread.start()  
                try:
                    while(True):
                        data_received = conn.recv(999999)
                        data = pickle.loads(data_received)
                        print(data)
                        if data['type'] == 'keyboard':
                            self.Character_solving(data)
                        elif data['type'] == 'mouse':
                            self.Mouse_solving(data)
                        elif data['type'] == 'file_re':
                            self.Receive_file(data)
                      
                except Exception as e:
                    print('mainError: ', e)
                    print(f"Connection with {addr} closed")              
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    sys.exit(app.exec())


