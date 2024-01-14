from pytube import YouTube, exceptions
from PIL import Image, ImageTk
import random
from io import BytesIO
import requests
import os, sys
from ctypes import windll


GWL_EXSTYLE=-20
WS_EX_APPWINDOW=0x00040000
WS_EX_TOOLWINDOW=0x00000080

def set_appwindow(root):
    hwnd = windll.user32.GetParent(root.winfo_id())
    style = windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style = style & ~WS_EX_TOOLWINDOW
    style = style | WS_EX_APPWINDOW
    res = windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
    root.wm_withdraw()
    root.after(10, lambda: root.wm_deiconify())





class Video:
    def __init__(self):
        self.VIDEO = None
        self.VID_DATA = {
            'title':str,
            'author':str,
            'length':str,
            'thumbnail':str
        }
        self.STREAM_DATA = []
        
    def check_url(self, url, error_callback):
        if url == '' or url == 'Insert video URL':
            return 'empty'
            
        try:
            vid = YouTube(url)
            print(vid)
        except exceptions.RegexMatchError:
            return 'invalid'
        
        try:
            stream = vid.streams.get_lowest_resolution()
            print(stream)
        except exceptions.VideoPrivate:
            return 'private'
        except exceptions.AgeRestrictedError:
            return 'age-restricted'
        except exceptions.LiveStreamError:
            return 'live'
        except exceptions.VideoRegionBlocked:
            return 'blocked'
        except exceptions.VideoUnavailable:
            return 'unavailable'
        except Exception as e:
            return e
        else:
            self.VIDEO = vid
            self.get_data(error_callback)
            return 'valid'
    
    def get_thumbnail(self, url):
        img_data = requests.get(url).content
        img = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize((420,235)))
        return img

    def get_data(self,error_callback):
        try:
            self.VID_DATA['title'] = self.VIDEO.title
            self.VID_DATA['author'] = self.VIDEO.author
            self.VID_DATA['length'] = self.VIDEO.length
            self.VID_DATA['thumbnail'] = self.get_thumbnail(self.VIDEO.thumbnail_url)
            self.STREAM_DATA = self.VIDEO.streams
        except Exception as e:
            error_callback(e)
    

    def  generate_random_id(self, length):
            char = '012345678ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            id = ''
            for x in range(length):
                id = id + char[random.randint(0, len(char)-1)]
            
            return id

    def separate_path(self, path:str):
        file_name = os.path.basename(path)
        location = os.path.dirname(path)
        return (location, file_name)
    

    
def get_formatted_size(total_size, factor=1024, suffix='B'):
    for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
        if total_size < factor:
            return f"{total_size:.2f}{unit}{suffix}"
        total_size /= factor
    return f"{total_size:.2f}Y{suffix}"

def get_formatted_time(time):
    time = int(time)
    hour = time // 3600
    minute = (time % 3600) // 60
    second = (time % 3600) % 60

    return f'{hour}h {minute}m {second}s' 

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)