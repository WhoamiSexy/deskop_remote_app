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
            old_img = None
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
    def Character_solving(self, data, conn):
        try:
            if data['action'] == 'on_press':
                keyboard.press(data['key_name'])
            elif data['action'] == 'on_release':
                keyboard.release(data['key_name'])

        except Exception as e:
            print("Keyboard Error: ", traceback.format_exc())
    def recvall(self, sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data
    def Receive_file(self, data):
        file_name = data['file_name']
        save_path = data['save_path']
        file_size = data['file_size']

        with open(save_path, 'wb') as file:
            remaining_size = file_size
            while remaining_size > 0:
                chunk = self.recvall(self.conn, min(1024, remaining_size))
                if not chunk:
                    break
                file.write(chunk)
                remaining_size -= len(chunk)

        print(f"File '{file_name}' received and saved at: {save_path}")

        
    def initUI(self):
        self.MainProgram = Thread(target = self.Main_Program, daemon = True)
        self.MainProgram.start()
    
    def Main_Program(self):
        while True:
            self.conn, self.addr = sock.accept()
            with self.conn:
                print("----------Connected----------")
                print(f"Connected by {self.addr}")
                # Luồng gửi data ảnh
                self.output_thread = Thread(target = lambda: self.ChangeImage(self.conn), daemon = True)
                self.output_thread.start()  
                try:
                    while(True):
                        data_received = self.conn.recv(9999)
                        data = pickle.loads(data_received)
                        
                        if data['type'] == 'keyboard':
                            self.Character_solving(data, self.conn)
                        if data['type'] == 'mouse':
                            self.Mouse_solving(data)
                        if data['type'] == 'file_re':
                            self.Receive_file(data)
                        if data['type'] == 'file_check':
                            length = self.conn.recv(4)  # Assume that the length of the pickled object is sent first
                            length = struct.unpack('!I', length)[0]
                            data_received = self.recvall(self.conn, length)
                            data = pickle.loads(data_received)
                except Exception as e:
                    print('mainError: ', e)
                    print(f"Connection with {self.addr} closed")              
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    sys.exit(app.exec())

