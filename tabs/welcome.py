import ttkbootstrap as ttk
from PIL import Image, ImageTk
from ttkbootstrap.constants import *






class Welcome_Tab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=10)
        self.main_frame = ttk.Frame(self)
        self.title = ttk.Label(self.main_frame, text='Welcome to Dolar Kuning', font=('Arial', 40, 'bold'))
        self.description = ttk.Label(self.main_frame, text='Youtube utility tool made using Pytube.', font=('Arial', 15))
        
        self.logo = ttk.Label(self.main_frame)
        img = ImageTk.PhotoImage(Image.open('images/yellow-dollar-sign-youtube.png').resize((216,216)))
        self.logo.image = img
        self.logo['image'] = img
        
        self.actions_frame = ttk.Frame(self.main_frame, padding=10)
        self.video_button = ttk.Button(self.actions_frame, text='Download Video', bootstyle = 'outline-primary', padding=10, command=lambda: master.master.create_tabs(1))
        self.playlist_button = ttk.Button(self.actions_frame, text='Download Playlist (WIP)', bootstyle = 'outline-primary', padding=10, command=lambda: master.master.create_tabs(2))
        
        self.main_frame.place(relx=.5, rely=.5, anchor=CENTER)
        self.title.pack()
        self.description.pack(pady=(5,0))
        self.logo.pack(pady=(10,0))
        self.actions_frame.pack(pady=(30,0))
        self.video_button.grid(row=0, column=0, padx=10)
        self.playlist_button.grid(row=0, column=1, padx=10)