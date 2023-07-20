from pytube import YouTube, Playlist, Channel, exceptions
import os
import re
from PIL import Image, ImageTk
from tkinter import messagebox
import shutil
import sys
import requests
import random
from io import BytesIO



class Playlist_Downloader:
    def __init__(self, parent):
        self.PARENT = parent
        self.URL = ''
        self.PLAYLIST = None
        self.VIDEO_LIST = []
        self.VIDEO_STREAMS= []
        self.DESCRIPTION = {}
        self.DIRECTORY = 'C:/Users/User/Downloads'
        self.FILENAME = ''
        self.STREAM = ''
        self.REGEX = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        self.STREAM_DATA = {
            'mp4': [],
            'mp4v': [],
            'mp4a': [],
            '3gpp': [],
            'webm': []
            }
    
    def validate_url(self, url):
        if url == '' or url == 'Insert playlist URL':
            return 'empty'
        
        playlist = Playlist(url)
        try:
            if playlist.length == 0:
                return 'unavailable'
        except:
            return 'invalid'
        
        self.PLAYLIST = playlist
        return 'valid'
        
    
    def get_playlist_description(self):
        self.DESCRIPTION['title'] = self.PLAYLIST.title
        self.FILENAME = self.DESCRIPTION['title']
        self.DESCRIPTION['length'] = self.PLAYLIST.length
        self.DESCRIPTION['owner'] = self.PLAYLIST.owner
        self.DESCRIPTION['last_updated'] = self.PLAYLIST.last_updated
        self.DESCRIPTION['views'] = self.PLAYLIST.views
        
        try:
            if not self.PLAYLIST.description == 'simpleText':
                self.DESCRIPTION['description'] = self.PLAYLIST.description
            else:
                self.DESCRIPTION['description'] = ''
                pass
        except:
            self.DESCRIPTION['description'] = ''
            pass

        self.DESCRIPTION['videos'] = self.PLAYLIST.videos
        self.DESCRIPTION['random_id'] = self.generate_random_id(15)
        self.get_stream_data()
    
    def get_stream_data(self):
        self.STREAM_FORMAT = ['mp4', 'mov', 'webm', 'wav', '3gp']
        self.VIDEO_LIST = []
        self.unavailable_videos = 0
        
        for v in self.PLAYLIST.videos:
            try:
                a = {}
                a['video'] = v
                a['title'] = v.title
                a['author'] = v.author
                a['thumbnail_url'] = v.thumbnail_url
                a['thumbnail_data'] = self.get_thumbnail(a['thumbnail_url'])
                a['length'] = v.length
                a['streams'] = v.streams
                print(a['streams'])
                self.VIDEO_LIST.append(a)
            except :
                self.unavailable_videos += 1
                continue
    
    def retrieve_video_streams(self):
            pass
    

    def get_thumbnail(self, url):
        img_data = requests.get(url).content
        return img_data

        

    def check_stream_availability(self, videos, video_format, filter, res, default_quality, callback):
        self.VIDEO_STREAMS = []
        for video in videos:
            try:
                if filter < 2:
                    if filter == 0:
                        a = self.VIDEO_LIST[video[1]]['streams'].filter(file_extension=video_format, progressive = True).order_by('filesize')
                        print(a)
                    else:
                        a = self.VIDEO_LIST[video[1]]['streams'].filter(file_extension=video_format, only_video = True).order_by('filesize')
                        print(a)

                    if not a == []:
                        b = a.get_by_resolution(f'{res}p')

                        if b == None:
                            if default_quality == 'hi':
                                stream = a.first()
                            else:
                                stream = a.last()
                        else:
                            stream = b
                        
                        self.VIDEO_STREAMS.append(stream)
                    else:
                        self.VIDEO_STREAMS.append('')

                else:
                        a = self.VIDEO_LIST[video[1]]['streams'].filter(file_extension=video_format, only_audio = True).order_by('filesize')
                        if not a == []:
                            print(a)
                            if default_quality == 'hi':
                                stream = a.first()
                            else:
                                stream = a.last()
                            
                            self.VIDEO_STREAMS.append(stream)
                        else:
                            self.VIDEO_STREAMS.append('')

                print(self.VIDEO_STREAMS[videos.index(video)])
                
            except Exception as e:
                print(e)
                self.VIDEO_STREAMS.append('')
            
            
            callback(len(self.VIDEO_STREAMS))

            

                    
            




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
    
    def prepare_directory(self, parent, use_id, create_folder):
        if use_id:
            self.FILENAME = f'{self.FILENAME} - {self.DESCRIPTION["random_id"]}'
        
        self.FILENAME = self.FILENAME.replace(':','').replace('\\','').replace('/','').replace('?','').replace('*','').replace('"','').replace('<','').replace('>','').replace('|','')
        
        #check if folder already exists and if user chooses to create a folder
        _dir = os.path.join(self.DIRECTORY, self.FILENAME)
        if create_folder:
            if os.path.isdir(_dir):
                warning = messagebox.askokcancel(
                    title='Folder already exists',
                    message=f'Folder "{self.FILENAME}" has already exist. Replace existing folder?',
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
    

    def prepare_items(self, parent, video_format, sub_format, sub_lang, download_thumb):
        existing_files = []
        
        sub_size = 0
        thumb_size = 0
        caption = ''
        
        if  download_thumb and os.path.exists(os.path.join(self.DIRECTORY, 'thumbnail.png')):
            existing_files.append('thumbnail.png')
        
        thumb_size = self.get_formatted_size(sys.getsizeof(self.DESCRIPTION['thumbnail_data']))
        
        #gathering caption info and checking if caption file has already existed
        if sub_lang != 'none':
            
            if sub_format:
                caption = self.VIDEO.captions[self.DESCRIPTION['captions_codes'][self.DESCRIPTION['captions_lang'].index(sub_lang)]].generate_srt_captions()
                if os.path.exists(os.path.join(self.DIRECTORY, 'captions.srt')):
                    existing_files.append('captions.srt')
            else:
                caption = self.VIDEO.captions[self.DESCRIPTION['captions_codes'][self.DESCRIPTION['captions_lang'].index(sub_lang)]].xml_captions
                if os.path.exists(os.path.join(self.DIRECTORY, 'captions.xml')):
                    existing_files.append('captions.xml')
            
            sub_size = self.get_formatted_size(sys.getsizeof(caption))
        

        self.FILENAME = self.FILENAME +'.' + str(video_format)
        
        if os.path.exists(os.path.join(self.DIRECTORY, self.FILENAME)):
            existing_files.append(self.FILENAME)
        
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
        
        return thumb_size, sub_size, caption           




    
    
    
    
    
    
