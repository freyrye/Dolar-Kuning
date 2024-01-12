import ttkbootstrap as ttk
from tkinter.filedialog import asksaveasfilename
from tkinter.messagebox import showerror
from datetime import datetime
import textwrap
from PIL import Image, ImageTk
from functions import Video, get_formatted_size, get_formatted_time, resource_path
import threading
import os


class Application(ttk.Window):
    def __init__(self):
        try:
            super().__init__(title='Dolar Kuning || YT Video Downloader', themename='solar')
            self.geometry(self.center_window())
            self.resizable(0,0)
            self.overrideredirect(False)
            self.iconbitmap(resource_path('images/logo.ico'))

            self.title_bar = Custom_Titlebar(self)
            self.video_gui = Video_GUI(self)

            self.video_gui.pack(expand=True, fill='both')
        except Exception as e:
            self.error_msg(e)
    
    def center_window(self):
        window_width = 600
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width /2) - (window_width /2)
        y = (screen_height /2) - (window_height /2)
        return '%dx%d+%d+%d'%(window_width, window_height, x, y)
    
    def error_msg(self, msg):
        showerror('Fatal Error', message=f'ERROR:\n{msg}')
        exit()


class Custom_Titlebar(ttk.Frame):
    def __init__(self, master:ttk.Window):
        super().__init__(master, style='warning', height=46)
        font = ('Helvetica',14)

        self.master = master
        self.title = ttk.Label(self, text=self.master.title(), font=font)
        self.close_button = ttk.Label(self, text='X', font=font)
        self.close_button.bind('<Button-1>', self.close)

        self.close_button.pack(side='right', padx=(0,20))

    def close(self, e):
        self.master.quit()
    
    def move(self, e):
        self.master.geometry()

# https://www.youtube.com/watch?v=mlKQP9SY5-Y
        # https://www.youtube.com/shorts/u-QsIa7VdCI?feature=share

class Video_GUI(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=20)
        self.video_obj = Video()
        
        self.VIDEO_URL = ttk.StringVar()

        self.url_entry = ttk.Entry(self, bootstyle='primary', width=40, textvariable=self.VIDEO_URL)
        self.url_alert = ttk.Label(self, text='',  bootstyle='warning')
        img = ImageTk.PhotoImage(Image.open(resource_path('images/blank.png')))
        self.desc_frame = ttk.Frame(self)
        
        self.thumbnail_image = ttk.Label(self.desc_frame)
        self.thumbnail_image.image = img
        self.thumbnail_image['image'] = img

        self.video_title = ttk.Label(self.desc_frame, text='Title:\t-')
        self.video_author = ttk.Label(self.desc_frame, text='Author:\t-')
        self.video_length = ttk.Label(self.desc_frame, text='Length:\t-')
        
        self.file_dropdown = ttk.Combobox(self, width=50, state='disabled')
        self.download_button  = ttk.Button(self, text='Download', style='primary outline', state='disabled', command=self.download_video)

        ttk.Label(self, text='insert video URL here').pack(pady=(0,10))        
        self.url_entry.pack(pady=(0,5))
        self.url_alert.pack(pady=(0,15))
        self.desc_frame.pack(pady=(0,40))
        self.thumbnail_image.grid(row=0, column=0, pady=(0,5))
        self.video_title.grid(row=1, column=0, sticky='nw', padx=(10,0))
        self.video_author.grid(row=2, column=0, sticky='nw', padx=(10,0))
        self.video_length.grid(row=3, column=0, sticky='nw', padx=(10,0))
        self.file_dropdown.pack(pady=(0,25))
        self.download_button.pack()

        self.url_entry.bind('<Return>', lambda e: threading.Thread(target=self.check_url, daemon=True).start())
    
    def error_msg(self, msg):
        showerror('Fatal Error', message=f'ERROR:\n{msg}')
        self.quit()


    def check_url(self):
        self.url_entry['state'] = 'disabled'
        check = self.video_obj.check_url(self.VIDEO_URL.get(), self.error_msg)

        if check == 'empty':
            self.url_alert['text'] = 'Insert video URL'
        elif check == 'invalid':
            self.url_alert['text'] = 'Invalid URL'
        elif check == 'age-restricted':
            self.url_alert['text'] = 'This video is age-restricted'
        elif check == 'live':
            self.url_alert['text'] = 'This video is a live stream'
        elif check == 'blocked':
            self.url_alert['text'] = 'This video is blocked in your region'
        elif check == 'private':
            self.url_alert['text'] = 'This video is private'
        elif check == 'unavailable':
            self.url_alert['text'] = 'This video is unavailable'
        elif check != 'valid':
            self.url_alert['text'] = check
        else:
            self.url_alert['text'] = ''
            self.show_data()
            self.file_dropdown['state'] = 'readonly'
            self.download_button['state'] = 'normal'

        self.url_entry['state'] = 'normal'

    def show_data(self):
        self.video_title['text'] = f'Title:\t{textwrap.shorten(str(self.video_obj.VID_DATA['title']), width=50, placeholder='...')}'
        self.video_author['text'] = f'Author:\t{self.video_obj.VID_DATA['author']}'
        self.video_length['text'] = f'Length:\t{get_formatted_time(self.video_obj.VID_DATA['length'])}'
        self.thumbnail_image.image = self.video_obj.VID_DATA['thumbnail']
        self.thumbnail_image['image'] = self.video_obj.VID_DATA['thumbnail']

        streams = []
        for stream in (self.video_obj.STREAM_DATA):
            if stream.is_progressive:
                streams.append(f'{str(stream.mime_type[6:]).upper()} - {stream.resolution} (progressive)    -    {get_formatted_size(stream.filesize, suffix='B')}')
            else:
                if stream.type == 'video':
                    streams.append(f'{str(stream.mime_type[6:]).upper()} - {stream.resolution} (video only)    -    {get_formatted_size(stream.filesize, suffix='B')}')
                else:
                    streams.append(f'{str(stream.mime_type[6:]).upper()} - {get_formatted_size(stream.bitrate, suffix='bps')} (audio only)    -    {get_formatted_size(stream.filesize, suffix='B')}')
        
        print(streams)
        
        self.file_dropdown['values'] = streams
        self.file_dropdown.current(0)

    def download_video(self):
        selection = self.file_dropdown.get()
        stream = self.video_obj.STREAM_DATA[self.file_dropdown['values'].index(selection)]
        itag = stream.itag
        print(itag)
        extension = stream.mime_type[6:]
        print(extension)
        print(self.video_obj.VID_DATA['title'])
        path = asksaveasfilename(title='Download Video', defaultextension=extension, initialfile=self.video_obj.VID_DATA['title'], filetypes=((f"{extension.upper()} file", f"*.{extension}"),("All Files", "*.*") ))
        print(path)
        print(self.video_obj.separate_path(path))
        if path:
            self.disable_children()
            Download_Toplevel(self, itag, self.video_obj.separate_path(path))
    
    def disable_children(self):
        self.url_entry['state'] = 'disabled'
        self.file_dropdown['state'] = 'disabled'
        self.download_button['state'] = 'disabled'


class Download_Toplevel(ttk.Toplevel):
    def __init__(self, parent:Video_GUI, itag, dir):
        super().__init__(title='Downloading...', size=(600,160), resizable=(False, False))

        self.iconbitmap(resource_path('images/logo.ico'))
        self.main_frame = ttk.Frame(self)
        self.parent = parent
        self.dir = dir
        self.itag = itag
        self.grab_set()

        frame_a = ttk.Frame(self.main_frame)
        self.percentage_label = ttk.Label(frame_a, text='-')
        self.progress_label = ttk.Label(frame_a, text='-/-')

        self.progress_bar = ttk.Progressbar(frame_a, orient='horizontal', mode='determinate', length=560, bootstyle='primary')
        self.time_remaining_label = ttk.Label(frame_a, text='Time remaining:\t-')
        self.speed_label = ttk.Label(frame_a, text='Speed:\t-')
        
        self.main_frame.pack(expand=True, fill='both', padx=20, pady=20)
        ttk.Label(self.main_frame, text='Downloading').pack()
        frame_a.pack(expand=True, fill='both')
        
        self.percentage_label.grid(row=0, column=0, sticky='nw')
        self.progress_label.grid(row=0, column=1, sticky='ne')
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky='nsew')
        self.time_remaining_label.grid(row=2, column=0, columnspan=2, sticky='nw', pady=(5,0))
        self.speed_label.grid(row=3, column=0, columnspan=2, sticky='nw')
        self.start_download_time = datetime.now()

        self.protocol('WM_DELETE_WINDOW', self.close)
        threading.Thread(target=self.download, daemon=True).start()

    def on_progress_callback(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        time_elapsed = (datetime.now() - self.start_download_time).total_seconds()
        formatted_size = get_formatted_size(total_size, factor=1000)
        bytes_downloaded = total_size - bytes_remaining
        percentage_completed = round(bytes_downloaded / total_size * 100)
        download_speed = bytes_downloaded / time_elapsed
        time_remaining = round(((bytes_remaining / 1000) / 1000) / float(download_speed / 1000 / 1000))
        self.progress_bar['value'] = percentage_completed
        self.progress_label['text'] = f'({get_formatted_size(bytes_downloaded, factor=1000)}/{formatted_size})'
        self.time_remaining_label['text'] = f'Time remaining:\t{get_formatted_time(time_remaining)}'
        self.speed_label['text'] = f'Speed:\t{get_formatted_size(bytes_downloaded, factor=1000, suffix='bps')}'
        self.percentage_label['text'] = f'{round(bytes_downloaded / total_size * 100)}%'
        self.update()
    
    def download(self):
        self.parent.video_obj.VIDEO.register_on_progress_callback(self.on_progress_callback)
        stream = self.parent.video_obj.VIDEO.streams.get_by_itag(int(self.itag))
        try:
            stream.download(filename=self.dir[1], output_path=self.dir[0], skip_existing=False)
        except Exception as e:
            self.error_msg(e)
        self.close()
    
    def error_msg(self,msg):
        showerror('Fatal Error', message=f'ERROR:\n{msg}')
        self.close()


    def close(self):
        self.parent.url_entry['state'] = 'normal'
        self.parent.file_dropdown['state'] = 'normal'
        self.parent.download_button['state'] = 'normal'
        self.destroy()




if __name__ == '__main__':
    app = Application()
    app.mainloop()