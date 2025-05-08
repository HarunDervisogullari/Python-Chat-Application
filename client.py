import socket
import threading
import tkinter
import tkinter.scrolledtext
from tkinter import simpledialog, Tk


HOST = '192.168.136.1'
PORT = 9090

class Client:

    def __init__(self, host, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        msg = Tk()
        msg.withdraw()

        self.nickname = simpledialog.askstring("Nickname", "Please choose a nickname", parent=msg)

        if self.nickname is None:
            msg.destroy()
            self.sock.close()
            exit(0)

        self.gui_done = False
        self.running = True

        gui_thread = threading.Thread(target=self.gui_loop)
        receive_thread = threading.Thread(target=self.receive)

        gui_thread.start()
        receive_thread.start()

    def gui_loop(self):
        self.win = Tk()
        self.win.configure(bg="light green")

        self.win.iconbitmap('logo.ico')

        self.win.grid_rowconfigure(1, weight=1)
        self.win.grid_columnconfigure(0, weight=3)  
        self.win.grid_columnconfigure(1, weight=1)  

        self.chat_label = tkinter.Label(self.win, text="Chat:", bg="light green")
        self.chat_label.config(font=("Arial", 12))
        self.chat_label.grid(row=0, column=0, padx=20, pady=5, sticky="w")

        self.text_area = tkinter.scrolledtext.ScrolledText(self.win, font=("Arial", 12))
        self.text_area.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")
        self.text_area.config(state='disabled')

        self.users_label = tkinter.Label(self.win, text="Online Users:", bg="light green")
        self.users_label.config(font=("Arial", 12))
        self.users_label.grid(row=0, column=1, padx=20, pady=5, sticky="w")

        self.users_area = tkinter.scrolledtext.ScrolledText(self.win, font=("Arial", 12), width=20)
        self.users_area.grid(row=1, column=1, padx=20, pady=5, sticky="nsew")
        self.users_area.config(state='disabled')

        self.msg_label = tkinter.Label(self.win, text="Message:", bg="light green")
        self.msg_label.config(font=("Arial", 12))
        self.msg_label.grid(row=2, column=0, padx=20, pady=5, sticky="w")

        self.input_area = tkinter.Text(self.win, height=3, font=("Arial", 12))
        self.input_area.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")

        self.emoji_frame = tkinter.Frame(self.win, bg="light green")
        self.emoji_frame.grid(row=4, column=0, padx=20, pady=5, sticky="w")

        self.send_button = self.create_rounded_button(self.emoji_frame, "Send", self.write)
        self.send_button.pack(side=tkinter.LEFT, padx=(0, 10))

        self.emoji_label = tkinter.Label(self.emoji_frame, text="Emojis:", bg="light green")
        self.emoji_label.config(font=("Arial", 12))
        self.emoji_label.pack(side=tkinter.LEFT)

        emojis = ["😊", "😂", "❤️", "👍", "😭", "🙏", "😘", "🥰", "😍", "😊"]

        for emoji in emojis:
            button = tkinter.Button(self.emoji_frame, text=emoji, font=("Arial", 12), command=lambda e=emoji: self.add_emoji(e))
            button.pack(side=tkinter.LEFT)

        self.button_frame = tkinter.Frame(self.win, bg="light green")
        self.button_frame.grid(row=5, column=0, padx=20, pady=5, sticky="nsew")

        self.exit_frame = tkinter.Frame(self.win, bg="light green")
        self.exit_frame.grid(row=5, column=0, padx=20, pady=5, sticky="e")
        self.exit_button = self.create_rounded_button(self.exit_frame, "Exit", self.stop)

        self.gui_done = True

        self.win.protocol("WM_DELETE_WINDOW", self.stop)

        self.sock.send("USERS".encode('utf-8'))

        self.win.mainloop()

    def create_rounded_button(self, parent, text, command):
        canvas = tkinter.Canvas(parent, height=40, width=100, bg="light green", highlightthickness=0)
        canvas.pack(side=tkinter.LEFT, padx=5, pady=5)

        radius = 20
        x0, y0 = 5, 5
        x1, y1 = 95, 35
        canvas.create_arc((x0, y0, x0 + radius, y0 + radius), start=90, extent=90, fill="yellow", outline="yellow")
        canvas.create_arc((x1 - radius, y0, x1, y0 + radius), start=0, extent=90, fill="yellow", outline="yellow")
        canvas.create_arc((x0, y1 - radius, x0 + radius, y1), start=180, extent=90, fill="yellow", outline="yellow")
        canvas.create_arc((x1 - radius, y1 - radius, x1, y1), start=270, extent=90, fill="yellow", outline="yellow")
        canvas.create_rectangle((x0 + radius / 2, y0, x1 - radius / 2, y1), fill="yellow", outline="yellow")
        canvas.create_rectangle((x0, y0 + radius / 2, x1, y1 - radius / 2), fill="yellow", outline="yellow")

        canvas.create_text((50, 20), text=text, font=("Arial", 12), fill="black")
        canvas.tag_bind("all", "<Button-1>", lambda event: command())

        return canvas

    def add_emoji(self, emoji):
        self.input_area.insert('end', emoji)

    def write(self):
        message = f"{self.nickname}: {self.input_area.get('1.0', 'end')}"
        self.sock.send(message.encode('utf-8'))
        self.input_area.delete('1.0', 'end')

    def stop(self):
        self.running = False
        self.sock.send(f"EXIT {self.nickname}".encode('utf-8'))
        self.win.destroy()
        self.sock.close()
        exit(0)

    def receive(self):
        while self.running:
            try:
                message = self.sock.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.sock.send(self.nickname.encode('utf-8'))
                elif message.startswith('USERS'):
                    users = message[6:].split(',')
                     
                    self.update_users(users)
                else:
                    if self.gui_done:
                        self.text_area.config(state='normal')
                        self.text_area.insert('end', message + '\n')
                        self.text_area.yview('end')
                        self.text_area.config(state='disabled')

            except ConnectionAbortedError:
                break
            except Exception as e:
                print(f"Error: {e}")
                self.sock.close()
                break

    def update_users(self, users):
        
        if self.gui_done:
            self.win.after(0, self._update_users_in_gui, users)

    def _update_users_in_gui(self, users):
        self.users_area.config(state='normal')
        self.users_area.delete('1.0', 'end')
        for user in users:
            self.users_area.insert('end', user + '\n')
        self.users_area.config(state='disabled')

if __name__ == "__main__":
    client = Client(HOST, PORT)
