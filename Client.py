
  
    Cách 1:
     def File_to_server(self):
        options = QFileDialog.Options()
        # options |= QFileDialog.DontUseNativeDialog
        filename, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "", options = options)
        if filename:
            with open(filename, 'rb') as f:
                file_content = f.read()
                file_name = os.path.basename(filename)
                data = {'type':'file_re', 'file_name': file_name, 'file_content': file_content}
                serialized_data = pickle.dumps(data)
                self.client_socket.send(serialized_data)
    cách 2
    self.SendFile = QPushButton(self.window2) # Nút gửi file
        self.SendFile.move(70, 5)
        self.SendFile.resize(460, 45)
        self.SendFile.setStyleSheet("font-size: 25px")
        self.SendFile.setText("Gửi file")
        self.SendFile.clicked.connect(self.File_to_ser)
    def File_to_ser(self):
        self.Thread = Thread(target = File_to_server(), daemoion= true)
        self.ThreadThread.start()
    ype': 'on_scroll', 'x': x, 'y': y,'dx':dx,'dy':dy}
        serialized_data = pickle.dumps(data)
        client_socket.send(serialized_data)
    

