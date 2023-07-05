#from pytube import YouTube, Playlist, Channel, exceptions
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *
from tkinter import messagebox

from tabs.videos import Videos_Tab
from tabs.playlists import Playlist_Tab
from tabs.welcome import Welcome_Tab



import config


class Application(ttk.Window):
    def __init__(self):
        super().__init__(title='Dolar Kuning', themename='solar')
        self.geometry('1280x720')
        self.iconbitmap('images/yellow-dollar-sign-youtube.ico')
        self.state('zoomed')
        self.tabs = ttk.Notebook(self, padding=10, bootstyle='primary')
        self.tabs.add(Welcome_Tab(self.tabs), text="𝘞𝘦𝘭𝘤𝘰𝘮𝘦", sticky=NSEW)
        self.tabs.add(ttk.Frame(), text="+", sticky=NSEW)
        #self.tabs.add(Videos_Tab(self.tabs), text="Videos", sticky=NSEW)
        self.tabs.pack(expand=TRUE, fill=BOTH)
        self.protocol('WM_DELETE_WINDOW', self.close_alert)
        self.tabs.bind("<<NotebookTabChanged>>", self.add_tab)
    
    def close_alert(self):
        if config.IS_DOWNLOADING:
            i = messagebox.askyesno(
                title='Close Window',
                message='Closing the application will stop the progress. Do you want to continue?',
                parent = self
            )
            if i:
                self.destroy()
        else:
            self.destroy()
    
    def add_tab(self, event):
        if self.tabs.tab(self.tabs.select(), 'text') == '+':
                index = len(self.tabs.tabs())-1
                self.tabs.insert(index, Welcome_Tab(self.tabs), text="𝘞𝘦𝘭𝘤𝘰𝘮𝘦", sticky=NSEW)
                self.tabs.select(index)
    
    def create_tabs(self, tab):
        index = self.tabs.index(self.tabs.select())
        if tab == 1:
            self.tabs.insert(index, Videos_Tab(self.tabs), text="Videos", sticky=NSEW)
        elif tab == 2:
            self.tabs.insert(index, Playlist_Tab(self.tabs), text="Playlist", sticky=NSEW)
        
        self.tabs.forget(self.tabs.select())
        self.tabs.select(index)
            

    
    def close_tabs(self):
        if config.IS_DOWNLOADING:
            i = messagebox.askyesno(
            title='Close Tab',
            message='Closing this tab will stop the progress. Do you want to continue?',
            parent = self)
            if not i:
                return
        
        if len(self.tabs.tabs())>2:
            index = len(self.tabs.tabs())-3
            self.tabs.forget(self.tabs.select())
            print(self.tabs.tab(self.tabs.select(), 'text'))
            if self.tabs.tab(self.tabs.select(), 'text') == '+':
                self.tabs.select(index)
        else:
            self.destroy()









if __name__ == '__main__':
    app = Application()
    app.mainloop() 