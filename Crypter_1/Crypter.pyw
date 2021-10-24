# -*- coding: utf-8 -*-
#!/usr/bin/env python
import os
import platform
import threading
import inspect
import pyperclip
import pyAesCrypt
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext


class MainWindow(tk.Frame):
    slesh = "\\"

    def __init__(self, root):
        super().__init__(root)
        self.img_cache = []
        self.thread_count = 0
        self.path_error = False
        lb_dir = Label(text = u"Path : ")
        lb_dir.pack()
        self.ent_value_dir = Entry(width = 50)
        self.ent_value_dir.pack()
        lb_pass = Label(text = u"Password : ")
        lb_pass.pack()
        ent_value_pass = Entry(width = 50)
        ent_value_pass.pack()
        if (platform.uname() == "Unix" or platform.uname() == "Linux" or platform.uname() == "Mac"):
            self.slesh = "/"
        crypt_img = PhotoImage(file = "Crypter resources" + self.slesh + "1.png")
        self.img_cache.append(crypt_img)
        btn_crypt = ttk.Button(text = "CRYPT", image = self.img_cache[0], compound = "left", command = lambda: self.crypting(self.ent_value_dir.get(), ent_value_pass.get()))
        btn_crypt.place(x = 5, y = 20)
        decrypt_img = PhotoImage(file = "Crypter resources" + self.slesh  + "2.png")
        self.img_cache.append(decrypt_img)
        btn_decrypt = ttk.Button(text = "DECRYPT", image = self.img_cache[1], compound = "left", command = lambda: self.decrypting(self.ent_value_dir.get(), ent_value_pass.get()))
        btn_decrypt.place(x = 5, y = 80)
        paste_img = PhotoImage(file = "Crypter resources" + self.slesh  + "3.png")
        self.img_cache.append(paste_img)
        btn_stop = ttk.Button(text = "PASTE", image=self.img_cache[2], compound = "left", command=lambda: self.paste_dir_to_entry())
        btn_stop.place(x = 465, y = 20)
        stop_img = PhotoImage(file = "Crypter resources" + self.slesh  + "4.png")
        self.img_cache.append(stop_img)
        btn_stop = ttk.Button(text = "GO OUT", image = self.img_cache[3], compound = "left", command = lambda: self.close_crypter())
        btn_stop.place(x = 465, y = 80); 
        self.console = scrolledtext.ScrolledText(fg = "red", bg = "black", state = "disable")
        self.console.place(y = 145, width = 600)

    def close_crypter(self):
        quit()

    def insert_to_console(self, text):
        self.console.configure(state = "normal")  #Разрешение вывода
        self.console.insert(END, text)
        self.console.yview(END)                   #Автопрокрутка
        self.console.configure(state = "disabled")

    def paste_dir_to_entry(self):
        self.ent_value_dir.insert(tk.END, pyperclip.paste())

    def crypt_file(self, file, password):
        bufferSize = 512 * 1024
        try:
            pyAesCrypt.encryptFile(str(file), str(file) + ".crypt",
                                   password, bufferSize)
            self.insert_to_console("ENCRYPTED >>> " + str(file) + ".crypt" + "\n")
            os.remove(file)
        except Exception as e:
            if inspect.stack()[2][3] != "decrypt_disk":
                self.insert_to_console("Ошибка шифрования, или не верный путь(" + str(e) + ")\n")
            else:
                self.insert_to_console("Ошибка шифрования <Unknown_Error> (" + str(e) + ")\n")
        if inspect.stack()[2][3] != "crypt_disk":
            self.thread_count=-1

    def crypt_disk(self, dir, password):
        try:
            for file in os.listdir(dir):
                if os.path.isdir(dir + self.slesh + file):
                    self.crypt_disk(dir + self.slesh + file, password)
                if os.path.isfile(dir + self.slesh + file):
                    try:
                        self.crypt_file(dir + self.slesh + file, password)
                    except Exception as ex:
                        self.insert_to_console(ex)
        except OSError:
            self.path_error = True
            return
        self.thread_count=-1

    def decrypt_file(self, file, password):
        bufferSize = 512 * 1024
        try:
            pyAesCrypt.decryptFile(str(file), str(os.path.splitext(file)[0]),
                                   password, bufferSize)
            self.insert_to_console('DECRYPTED >>> ' + str(os.path.splitext(file)[0]) + '\n')
            os.remove(file)
        except Exception as e:
            if inspect.stack()[2][3] != "decrypt_disk":
                self.insert_to_console("Ошибка расшифровки, файл не зашифрован, неверный пароль, файл поврежден или не верный путь(" + str(e) + ")\n")
            else:
                self.insert_to_console("Ошибка расшифровки, файлы не зашифрованы, неверный пароль или файл поврежден (" + str(e) + ")\n")
        if inspect.stack()[2][3] != "decrypt_disk":
            self.thread_count=-1

    def decrypt_disk(self, dir, password):
        try:
            for file in os.listdir(dir):
                if os.path.isdir(dir + self.slesh + file):
                    self.decrypt_disk(dir + self.slesh + file, password)
                if os.path.isfile(dir + self.slesh + file):
                    try:
                        self.decrypt_file(dir + self.slesh + file, password)
                        self.thread_count=-1
                    except Exception as ex:
                        self.insert_to_console(ex)
        except OSError:
            self.path_error = True
        self.thread_count=-1
        

    #Необходимо ускорение процесса шифрования
    def crypting(self, dir, password):
        if self.path_error or password == '':
            self.path_error = False
            self.thread_count = 0
            self.insert_to_console("Ошибка : Неправильный путь или нет пароля !\n")
            return
        else:
            self.thread_count += 1
            if self.thread_count > 1:
                self.insert_to_console("Ограничение потока, запущено : "  + self.thread_count + "\n")
                return
        if os.path.isdir(dir):
            pycrypt = threading.Thread(target = self.crypt_disk, args = (dir, password))
        else:
             pycrypt = threading.Thread(target = self.crypt_file, args = (dir, password))
        pycrypt.start()

    def decrypting(self, dir, password):
        if self.path_error or password == '':
            self.path_error = False
            self.thread_count = 0
            self.insert_to_console("Ошибка : Неправильный путь или нет пароля !\n")
            return
        else:
            self.thread_count += 1
            if self.thread_count > 1:
                self.insert_to_console("Ограничение потока, запущено : " + self.thread_count + "\n")
                return
        if os.path.isdir(dir):
            pycrypt = threading.Thread(target = self.decrypt_disk, args = (dir, password))
        else:
            pycrypt = threading.Thread(target = self.decrypt_file, args = (dir, password))
        pycrypt.start()

    def run_app():
        root = tk.Tk()
        root.resizable(width = False, height = False)
        MainWindow(root)
        root.title("Cool cripter")
        root.geometry("600x500")
        root.mainloop()

if __name__ == '__main__':
    zv = MainWindow
    zv.run_app()