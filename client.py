# client.py
import socket
import threading
import tkinter 
from tkinter import simpledialog, scrolledtext

class Client(threading.Thread):
    def __init__(self, host, port):
        self.host = host
        self.port = port

        msg = tkinter.Tk()
        msg.withdraw()
        self.nickname = simpledialog.askstring("Nama", "Masukkan nama!", parent=msg)

        # set up socket
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            print(f"[*] terkoneksi ke {self.host} : {self.port}")
        except Exception as e:
            print(f"[!] error: {e}")
    
        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = tkinter.Tk()
        self.win.configure(bg="#424549")

        self.chat_label = tkinter.Label(self.win, text="Chat App Kelompok 5", fg="#fff", bg="#424549", font=("Arial", 12))
        self.chat_label.pack(padx=20, pady=5)

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, wrap=tkinter.WORD, font=("Arial", 10))
        self.text_area.pack(padx=20, pady=5)
        self.text_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text=f"Halo {self.nickname}", bg="#424549", font=("Arial", 12), fg="#fff")
        self.msg_label.pack(padx=20, pady=5)

        self.input_area = tkinter.Text(self.win, height=3, wrap=tkinter.WORD, font=("Arial", 10))
        self.input_area.pack(pady=5, side='left')

        self.send_button = tkinter.Button(self.win, text="Send", command=self.write, font=("Arial", 12))
        self.send_button.pack(pady=5, side='right')

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.win.mainloop()

    def write(self):
        message = f"{self.input_area.get('1.0','end')}\n"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0','end')

    def stop(self):
        self.running = False
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024)
                if message == b'login':
                    self.sock.send(self.nickname.encode('utf-8'))
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message.decode('utf-8'))
                        self.text_area.yview(tkinter.END)
                        self.text_area.config(state='disabled')
            except ConnectionResetError:
                break
            except:
                print("Error")
                self.sock.close()
                break

host = '127.0.0.1'
port = 3000

client = Client(host, port)
