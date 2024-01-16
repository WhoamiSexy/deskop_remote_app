# Socket
import pickle # Import thư viện pickle để chuyển đổi dữ liệu sang dạng nhị phân.
import os
import time
import socket
from pynput import mouse, keyboard
from pynput.mouse import Button
from PIL import ImageGrab
import io 
import numpy as np 
from random import randint 
import pyautogui 
import threading
from threading import Thread
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QLabel, QPushButton, QAction, QMessageBox, QLineEdit,  QVBoxLayout, QDialog, QFileDialog, QListWidget, QListWidgetItem
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt, pyqtSlot
from PyQt5.QtNetwork import QTcpSocket
import pickle
import struct

class Dekstop(QMainWindow):
    def __init__(self): # def __init__(self):: Hàm khởi tạo của class Dekstop.
        super().__init__()
        self.initUI()

    def initUI(self): # def initUI(self):: Hàm tạo giao diện người dùng của ứng dụng.
        # Khởi tạo pixmap
        self.pixmap = QPixmap()

        # Khởi tạo Dialog mới để hiển thị hình ảnh
        self.newWindow = QDialog()

        # Khởi tạo label mới để đăng nhập
        self.label = QLabel(self)

        # Khởi tạo label2 mới để hiển thị hình ảnh
        self.label2 = QLabel(parent = self.newWindow)

        self.label.setPixmap(self.pixmap)
        self.label.resize(self.width(), self.height())
        self.setGeometry(QRect(pyautogui.size()[0] // 4 + 170, pyautogui.size()[1] // 4, 600, 200))
        self.setFixedSize(self.width(), self.height())
        self.setWindowTitle("[CLIENT] Remote Desktop: " + str(randint(99999, 999999)))

        self.button = QPushButton(self) # nút khởi động chương trình
        self.button.move(150, 100)
        self.button.resize(300, 90)
        self.button.setStyleSheet("font-size: 30px")
        self.button.setText("Start Demo")
        self.button.clicked.connect(self.StartThread)

        self.ip = QLineEdit(self) # edit text để nhập IP
        self.ip.move(70, 5)
        self.ip.resize(460, 45)
        self.ip.setStyleSheet("font-size: 30px")
        self.ip.setPlaceholderText("IP")

        self.port = QLineEdit(self) # edit text để nhập PORT
        self.port.move(70, 55)
        self.port.resize(460, 45)
        self.port.setStyleSheet("font-size: 30px")
        self.port.setPlaceholderText("PORT")

    def StartThread(self): #def StartThread(self):: Hàm được khởi động thread khi nút "Start Demo" được nhấn.
        # Khởi tạo label 2_____________________________________________________________________________
        self.label2.setPixmap(self.pixmap)
        self.label2.resize(1920, 1080)
        self.label2.setFixedSize(self.width(), self.height())
        
        self.newWindow.setGeometry(QRect(0, -5, 400, 90))
        self.newWindow.setFixedSize(1920, 1080)
        self.newWindow.setWindowTitle("[Server] Remote Desktop: " + str(randint(99999, 999999)))
        self.newWindow.show()

        # Khởi tạo label 3_____________________________________________________________________________

        self.window2 = QDialog()
        self.container = QWidget(self.window2)
        self.window2.setWindowTitle("[Server] Chụp ảnh và Thao Tác File: " + str(randint(99999, 999999)))

        self.label3 = QLabel(self.container)  # Tạo container để chứa nút
        self.label3.setPixmap(self.pixmap)
        
        self.CatchImage = QPushButton(self.window2) # Nút chụp ảnh
        self.CatchImage.move(150, 150)
        self.CatchImage.resize(300, 45)
        self.CatchImage.setStyleSheet("font-size: 25px")
        self.CatchImage.setText("Chụp ảnh")
        self.Image_catched = None
        self.CatchImage.clicked.connect(self.Catchimage)

        self.SendFile = QPushButton(self.window2) # Nút gửi file
        self.SendFile.move(70, 5)
        self.SendFile.resize(460, 45)
        self.SendFile.setStyleSheet("font-size: 25px")
        self.SendFile.setText("Gửi file")
        self.SendFile.clicked.connect(self.File_to_server)

        self.ReFile = QPushButton(self.window2) # Nút nhận file
        self.ReFile.move(70, 55)
        self.ReFile.resize(460, 45)
        self.ReFile.setStyleSheet("font-size: 25px")
        self.ReFile.setText("Nhận file")
        self.ReFile.clicked.connect(self.ReFile_From_server)

        self.window2.setGeometry(QRect(0, -5, 600, 200))
        self.window2.setFixedSize(600, 200)
        self.window2.show()
        
        # Khởi tạo Main Program_________________________________________________________________________
        self.mainthread = Thread(target = self.MainProgram, daemon = True)
        self.mainthread.start()

    def check_connection(self, client_socket):
        try:
            client_socket.connect((self.ip.text(), int(self.port.text())))
            return True
        except Exception as e:
            return False
        
    # Thread truyền ảnh _________________________________________________________________________________________________
    def MainProgram(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        if(self.check_connection(client_socket)):
            with client_socket:
                # Thread gửi phím     
                self.thread_keyboard = Thread(target = lambda: self.putkeyboard(self.client_socket), daemon = True)
                self.thread_keyboard.start()
                # Thread gửi chuột
                self.thread_mouse = Thread(target = lambda: self.putkeymouse(self.client_socket), daemon = True)         
                self.thread_mouse.start()

                try:
                    while True:
                        img_size = struct.unpack('<l', self.recvall(client_socket, 4))[0]
                        img_data = self.recvall(client_socket, img_size)

                        self.pixmap.loadFromData(img_data)
                        self.label2.setPixmap(self.pixmap)
                        self.label2.setScaledContents(True)
                        self.label2.setAlignment(Qt.AlignCenter)
                        self.label2.setFixedSize(1920, 1080)       
                except:
                    self.client_socket.close()
        else:
            self.newWindow.close()
            self.ip.clear()
            self.ip.setStyleSheet("font-size: 30px")
            self.ip.setPlaceholderText("Wrong IP or PORT")


    def recvall(self, sock, n):
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n-len(data))
            if not packet:
                return None
            data.extend(packet)
        return data

    
    # Gửi yêu cầu lấy file từ server_________________________________________________________________________________
    def ReFile_From_server(self): # Yêu cầu lấy danh sách file từ server
        data = {'type': 'file_list_request'}
        serialized_data = pickle.dumps(data)
        self.client_socket.send(serialized_data)

    def on_item_clicked(self, item):
        chosen_file = item.text()
        self.request_file_from_server(chosen_file)

    def request_file_from_server(self, file_name):
        data = {'type': 'file_request', 'file_name': file_name}
        serialized_data = pickle.dumps(data)
        self.client_socket.send(serialized_data)

    # Gửi file qua server_____________________________________________________________________________________________
    def File_to_server(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;JPEG (*.jpg *.jpeg);;PNG (*.png)", options=options)
        if filename:
            with open(filename, 'rb') as f:
                file_content = f.read()
                file_name = os.path.basename(filename)
                data = {'type':'file_for_re', 'file_name': file_name, 'file_content': file_content}
                serialized_data = pickle.dumps(data)
                self.client_socket.send(serialized_data)

    # Chụp ảnh_________________________________________________________________________________________________
    def Catchimage(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getSaveFileName(self,"QFileDialog.getSaveFileName()", "","All Files (*);;JPEG (*.jpg *.jpeg);;PNG (*.png)", options=options)
        if filename:
            with open(filename, 'wb') as f:
                f.write(self.Image_catched)
                
    # Thread gửi kí tự _______________________________________________________________________________________________
    def putkeyboard(self, client_socket):
        on_release = True
        while on_release:
            with keyboard.Listener(
                on_press = lambda key: self.keyPressed(key, client_socket),
                on_release = lambda key: self.keyReleased(key, client_socket)
            ) as listener:
                listener.join()

    def keyPressed(self, key, client_socket):
        data = {'type': 'keyboard', 'action': 'on_press', 'key_name': key}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)
        
    def keyReleased(self, key,client_socket):
        data = {'type': 'keyboard', 'action': 'on_press', 'key_name': key}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)
        if key == keyboard.Key.esc:
            return False

    # Thread gửi chuột ____________________________________________________________________________________________
    def putkeymouse(self, client_socket):
        while True:
            with mouse.Listener(
                on_move = lambda x, y: self.on_move(x, y, client_socket),    
                on_scroll = lambda x,y ,dx, dy: self.on_scroll(x,y,dx, dy, client_socket),                                                                           #on_move: Được gọi khi chuột di chuyển.
                on_click = lambda x, y, button, pressed: self.on_click(x, y, button, pressed, client_socket)  
            ) as listener:
                listener.join()
        
    def on_move(self, x, y, client_socket):
        data = {'type':'mouse', 'event_type': 'on_move', 'x': x, 'y': y}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)
        time.sleep(0.02)        

    def on_click(self, x, y, button, pressed, client_socket):
        action = 'Pressed' if pressed else 'Released'
        
        if button == Button.right:
            data = {'type':'mouse', 'event_type': 'on_click', 'x': x, 'y': y, 'action': action, 'button': 'right'}

        if button == Button.left:
            data = {'type':'mouse', 'event_type': 'on_click', 'x': x, 'y': y, 'action': action, 'button': 'left'}

        if button == Button.middle:
            data = {'type':'mouse', 'event_type': 'on_click', 'x': x, 'y': y, 'action': action, 'button': 'middle'}

        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)

    def on_scroll(self,x,y, dx, dy, client_socket):
      
        data = {'type':'mouse', 'event_type': 'on_scroll', 'x': x, 'y': y,'dx':dx,'dy':dy}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Dekstop()
    ex.show()
    sys.exit(app.exec())
    

