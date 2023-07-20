from pytube import YouTube, Playlist, Channel, exceptions
import os
from PIL import Image, ImageTk
from tkinter import messagebox
import shutil
import sys
import requests
import random
from io import BytesIO


class Video_Downloader:
    def __init__(self, parent):
        self.PARENT = parent
        self.reset_variables()
    

    def reset_variables(self):
        self.URL = ''
        self.VIDEO = None
        self.DESCRIPTION = {}
        self.DIRECTORY = 'C:/Users/User/Downloads'
        self.FILENAME = []
        self.STREAM = ''
        self.CAPTIONS = ''
        self.STREAM_DATA = {
            'mp4': [],
            'mp4v': [],
            'mp4a': [],
            '3gpp': [],
            'webm': []
            }
    
    def validate_url(self, url):
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
        else:
            self.URL = url
            self.VIDEO = vid
            print(self.URL)
            return 'valid'
    
    def get_video_description(self):
        self.DESCRIPTION['title'] = self.VIDEO.title
        self.FILENAME[0] = self.DESCRIPTION['title']
        self.DESCRIPTION['length'] = self.VIDEO.length
        self.DESCRIPTION['author'] = self.VIDEO.author
        self.DESCRIPTION['publish_date'] = self.VIDEO.publish_date
        self.DESCRIPTION['views'] = self.VIDEO.views
        self.DESCRIPTION['description'] = self.VIDEO.description
        self.DESCRIPTION['thumbnail_url'] = self.VIDEO.thumbnail_url
        self.DESCRIPTION['captions']
        self.DESCRIPTION['captions_lang'] = []
        self.DESCRIPTION['captions_codes'] = []
        for a in self.VIDEO.captions:
            self.DESCRIPTION['captions'][a.name]['srt'] = a.generate_srt_captions()
            self.DESCRIPTION['captions'][a.name]['xml'] = a.xml_captions
            self.DESCRIPTION['captions_lang'].append(a.name)
            self.DESCRIPTION['captions_codes'].append(a.code)
        self.get_stream_data()
    
    def get_stream_data(self):
        for st in self.STREAM_DATA:
            for stream in self.VIDEO.streams.filter(file_extension=st).order_by('filesize').desc():
                print(stream)
                a = {}
                a['itag'] = stream.itag
                a['type'] = stream.type
                a['progressive'] = stream.is_progressive
                if a['type'] == 'video':
                    a['res'] = stream.resolution
                    a['fps'] = stream.fps
                else:
                    a['bitrate'] = self.get_formatted_size(stream.bitrate, suffix='b') + 'ps'
                a['filesize'] = self.get_formatted_size(stream.filesize)
                self.STREAM_DATA[st].append(a)
        

        
    def get_formatted_size(self, total_size, factor=1024, suffix='B'):
        # looping through the units
        for unit in ["", "k", "M", "G", "T", "P", "E", "Z"]:
            if total_size < factor:
                return f"{total_size:.2f}{unit}{suffix}"
            total_size /= factor
        # returning the formatted audio file size
        return f"{total_size:.2f}Y{suffix}"    

    def  generate_random_id(self, length):
            char = '012345678ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            id = ''
            for x in range(length):
                id = id + char[random.randint(0, len(char)-1)]
            
            return id
    
    def get_thumbnail(self):
        img_data = requests.get(self.DESCRIPTION['thumbnail_url']).content
        self.DESCRIPTION['thumbnail_data'] = img_data
        self.DESCRIPTION['thumbnail'] = ImageTk.PhotoImage(Image.open(BytesIO(img_data)).resize((340,191)))
    
    def replace_filename(self):
        self.FILENAME[0] = self.FILENAME[0].replace(':','').replace('\\','').replace('/','').replace('?','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','')

    def prepare_directory(self, parent, use_id, create_folder):
        try:
            if use_id:
                self.FILENAME[0] = f'{self.FILENAME[0]} - {self.DESCRIPTION["random_id"]}'
            
            self.replace_filename()
            
            #check if folder already exists and if user chooses to create a folder
            _dir = os.path.join(self.DIRECTORY, self.FILENAME[0])
            if create_folder:
                if os.path.isdir(_dir):
                    warning = messagebox.askokcancel(
                        title='Folder already exists',
                        message=f'Folder "{self.FILENAME[0]}" has already exist. Replace existing folder?',
                        parent = parent
                    )

                    #deletes existing folder an replace it with an empty one
                    if warning:
                        shutil.rmtree(_dir)
                        os.mkdir(_dir)
                        self.DIRECTORY = _dir
                    else:
                        return False
                else:
                    os.mkdir(_dir)
                    self.DIRECTORY = _dir
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message=f'There\'s an error while downloading the video:\n{e}\nTry checking your internet connection.'
            )

    def prepare_items(self, parent, video_format, sub_format, sub_lang, download_thumb, callback):
    
        existing_files = []
        
        sub_size = 0
        thumb_size = 0
        caption = ''
        
        self.FILENAME[1] = ''
        if  download_thumb:
            self.FILENAME[1] = 'thumbnail.png'
            if os.path.exists(os.path.join(self.DIRECTORY, 'thumbnail.png')):
                existing_files.append('thumbnail.png')
        
        
        thumb_size = self.get_formatted_size(sys.getsizeof(self.DESCRIPTION['thumbnail_data']))
        
        #gathering caption info and checking if caption file has already existed
        if sub_lang != 'none':
            
            if sub_format:
                caption = self.DESCRIPTION['captions'][sub_lang].generate_srt_captions()
                if os.path.exists(os.path.join(self.DIRECTORY, 'captions.srt')):
                    existing_files.append('captions.srt')
                self.FILENAME[2] = 'captions.srt'
            else:
                caption = self.DESCRIPTION['captions'][sub_lang].xml_captions
                if os.path.exists(os.path.join(self.DIRECTORY, 'captions.xml')):
                    existing_files.append('captions.xml')
                self.FILENAME[2] = 'captions.xml'
            
            sub_size = self.get_formatted_size(sys.getsizeof(caption))
        

        self.FILENAME[0] = self.FILENAME[0] +'.' + str(video_format)
        
        if os.path.exists(os.path.join(self.DIRECTORY, self.FILENAME[0])):
            existing_files.append(self.FILENAME[0])
        
        print(len(existing_files))
        if len(existing_files) != 0:
            warning_text = 'File '
            for i, a in  enumerate(existing_files):
                if a != '':
                    if i == 0:
                        warning_text= f'{warning_text} "{a}"'
                    else:
                            warning_text= f'{warning_text}, "{a}"'
            
            warning_text = warning_text + ' has already exists. Replace existing files?'

            warning = messagebox.askokcancel(
                    title='File already exists',
                    message=warning_text,
                    parent = parent
                )
            
            if warning:
                for i in existing_files:
                    print(os.path.join(self.DIRECTORY, i))
                    os.remove(os.path.join(self.DIRECTORY, i))
            else:
                return False
        
        self.CAPTIONS = caption
        self.VIDEO.register_on_progress_callback(callback)
        return thumb_size, sub_size
    

    def download_video(self, parent, callback, selected_itag):
        if self.FILENAME[1] != '':
            with open(os.path.join(self.DIRECTORY, 'thumbnail.png'), 'wb') as f:
                    f.write(self.DESCRIPTION['thumbnail_data'])

        if self.FILENAME[2] != '':
            with open(os.path.join(self.DIRECTORY, self.FILENAME[2]), 'w', encoding='utf-8') as f:
                        f.write(self.CAPTIONS)
        

        stream = self.VIDEO.streams.get_by_itag(selected_itag)
        stream.download(filename=self.FILENAME[0], output_path=self.DIRECTORY)
        



        

