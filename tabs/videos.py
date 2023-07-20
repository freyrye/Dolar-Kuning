from queue import Queue
import ttkbootstrap as ttk
import os
from tkinter.filedialog import askdirectory
import textwrap
from PIL import Image, ImageTk
from ttkbootstrap.constants import *
from tkinter import messagebox
#from ttkbootstrap.dialogs import Messagebox
from downloaders.videos import Video_Downloader
import threading
from datetime import datetime

import config



class Videos_Tab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=(30,10))
        
        self.vd = Video_Downloader(self)
        self.url = ttk.StringVar(value='Insert video URL')
        self.filename = ttk.StringVar()
        self.download_thumbnail = ttk.BooleanVar(value=False)
        self.selected_captions = ttk.StringVar()
        self.caption_is_srt = ttk.BooleanVar(value=True)
        self.video_format = ttk.StringVar(value='mp4')
        self.FORMAT = ''
        self.using_id = ttk.BooleanVar(value=True)
        self.directory = ttk.StringVar(value=self.vd.DIRECTORY)
        self.create_folder = ttk.BooleanVar(value=False)
        self.list_filter = ttk.IntVar()
        self.selected_itag = ''


        entry_frame = ttk.Frame(self)
        self.url_entry = ttk.Entry(entry_frame, bootstyle='primary', width=30, textvariable=self.url, takefocus=0)
        self.url_entry.bind("<FocusOut>", lambda event: self.autofill_entry(1,0))
        self.url_entry.bind("<FocusIn>", lambda event: self.autofill_entry(1,1))
        self.url_entry.bind('<Key>', lambda event: self.url_alert.config(text=''))
        self.url_entry.bind('<Return>', lambda event: threading.Thread(target=self.confirm_input, daemon=True).start())
        
        self.confirm_entry_button = ttk.Button(entry_frame, bootstyle='outline primary', text='confirm', command=lambda: threading.Thread(target=self.confirm_input, daemon=True).start())
        self.url_alert = ttk.Label(entry_frame, text='', bootstyle='warning')
        
        description_frame = ttk.Labelframe(self,text='Video Description', bootstyle='primary', padding=(10, 5, 10, 10))
        self.video_title = ttk.Label(description_frame, text='Title:\t-', wraplength=300)
        self.video_length = ttk.Label(description_frame, text='Length:\t-')
        self.video_author = ttk.Label(description_frame, text='Author:\t-')
        self.publish_date = ttk.Label(description_frame, text='Publish Date:\t-')
        self.views = ttk.Label(description_frame, text='Views:\t-')

        desc_label = ttk.Label(description_frame, text='Description:')
        self.video_desc = ttk.Text(description_frame, width=40, wrap=WORD)

        settings_frame = ttk.Labelframe(self,text='Stream Settings', bootstyle='primary', padding=(10, 5, 10, 10))
        self.thumbnail_label = ttk.Label(settings_frame, text='Thumbnail:')
        self.thumbnail_image = ttk.Label(settings_frame)
        img = ImageTk.PhotoImage(Image.open('images/blank.png'))
        self.thumbnail_image.image = img
        self.thumbnail_image['image'] = img
        self.download_thumbnail_check = ttk.Checkbutton(
            settings_frame,
            text='Download video thumbnail',
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.download_thumbnail,
            state=ttk.DISABLED)
        self.id_label = ttk.Label(settings_frame, text='Generated ID:\t-')
        caption_label = ttk.Label(settings_frame, text='Captions:')
        self.caption_list = ttk.Combobox(settings_frame, textvariable=self.selected_captions, state=ttk.DISABLED)
        self.caption_format_check = ttk.Checkbutton(
            settings_frame,
            text='Download as .srt file',
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.caption_is_srt,
            state=ttk.DISABLED)
        self.filter_label = ttk.Label(settings_frame, text='Filters:')
        
        self.list_frame = ttk.Frame(settings_frame)
        self.video_list = ttk.Treeview(self.list_frame, height=6, columns=['itag', 'res', 'fps','bitrate', 'size', 'type'], show='headings', selectmode='browse')
        self.video_list.heading('itag', text='itag')
        self.video_list.heading('res', text='resolution')
        self.video_list.heading('fps', text='fps')
        self.video_list.heading('bitrate', text='bitrate')
        self.video_list.heading('size', text='size')
        self.video_list.heading('type', text='type')
        self.video_list.column('itag', width=25, anchor=CENTER)
        self.video_list.column('res', width=60, anchor=CENTER)
        self.video_list.column('fps', width=15, anchor=CENTER)
        self.video_list.column('bitrate', width=60, anchor=CENTER)
        self.video_list.column('size', width=35, anchor=CENTER)
        self.video_list.column('type', width=40, anchor=CENTER)

        self.video_vscroll = ttk.Scrollbar(self.list_frame, orient='vertical', bootstyle='primary', command=self.video_list.yview)
        self.video_list.config(yscrollcommand=self.video_vscroll.set)


        
        self.filter_frame = ttk.Frame(settings_frame)
        self.format_radio_1 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.video_format,
            value='mp4',
            text='.mp4',
            bootstyle='primary',
            command=self.change_list_items,
            state=ttk.DISABLED)
        self.format_radio_2 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.video_format,
            value='webm',
            text='.webm',
            bootstyle='primary',
            command=self.change_list_items,
            state=ttk.DISABLED)
        self.format_radio_3 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.video_format,
            value='mov',
            text='.mov',
            bootstyle='primary',
            command=self.change_list_items,
            state=ttk.DISABLED)
        self.format_radio_4 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.video_format,
            value='ogg',
            text='.ogg',
            bootstyle='primary',
            command=self.change_list_items,
            state=ttk.DISABLED)
        self.format_radio_5 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.video_format,
            value='3gp',
            text='.3gp',
            bootstyle='primary',
            command=self.change_list_items,
            state=ttk.DISABLED)
        

        self.filter_radio_1 =ttk.Radiobutton(
            self.filter_frame,
            variable=self.list_filter,
            value=0,
            text='Progressive video (max:720p)',
            command=self.change_list_items,
            state=ttk.DISABLED
        )
        
        second_row = ttk.Frame(self.filter_frame)

        self.filter_radio_2 =ttk.Radiobutton(
            second_row,
            variable=self.list_filter,
            value=1,
            text='Video only',
            command=self.change_list_items,
            state=ttk.DISABLED
        )

        self.filter_radio_3 =ttk.Radiobutton(
            second_row,
            variable=self.list_filter,
            value=2,
            text='Audio only',
            command=self.change_list_items,
            state=ttk.DISABLED
        )

        
        self.itag_label = ttk.Label(settings_frame, text='Selected itag:\t-')


        self.download_frame = ttk.Labelframe(self,text='Download Settings', bootstyle='primary', padding=(10, 5, 10, 10))
        filename_label = ttk.Label(self.download_frame, text='File name:')
        self.filename_entry = ttk.Entry(self.download_frame, bootstyle='primary', width=50, textvariable=self.filename, state=ttk.DISABLED)
        self.naming_check = ttk.Checkbutton(
            self.download_frame,
            text="Add '- [generated_id]' behind file name",
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.using_id,
            state=ttk.DISABLED)
        
        location_label = ttk.Label(self.download_frame, text='File location:')
        self.directory_button = ttk .Button(self.download_frame, text='Select Directory', bootstyle= 'outline primary', command=self.select_directory, state=ttk.DISABLED)
        self.directory_entry = ttk.Entry(self.download_frame, bootstyle='primary', width=50, textvariable=self.directory, state=ttk.DISABLED)
        
        self.create_folder_check = ttk.Checkbutton(
            self.download_frame,
            text="Create folder",
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.create_folder,
            state=ttk.DISABLED)
        
        self.download_button = ttk.Button(self.download_frame, text='Download', bootstyle= 'outline primary', state=ttk.DISABLED, command=self.prepare_download)
        option_frame = ttk.Frame(self)
        self.close_button = ttk.Button(option_frame, text='X', padding=(15,10), bootstyle='outline-primary', command=self.master.master.close_tabs)
        self.close_label = ttk.Label(option_frame, text='Close', bootstyle='primary')


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        entry_frame.grid(row=0,column=0, sticky=NW, pady=(8,0))
        self.url_alert.pack(anchor=NW, pady=5)
        self.url_entry.pack(side=LEFT)
        self.confirm_entry_button.pack(side=LEFT, padx=(10,0))
        self.url_alert.pack(side=BOTTOM)
        description_frame.grid(row=1, column=0, sticky=NW)
        self.video_title.pack(anchor=NW)
        self.video_length.pack(anchor=NW)
        self.video_author.pack(anchor=NW)
        self.publish_date.pack(anchor=NW)
        self.views.pack(anchor=NW)
        desc_label.pack(anchor=NW)
        self.video_desc.pack(pady=(10,0), anchor=NW, expand=TRUE, fill=BOTH)
        settings_frame.grid(row=0,column=1, sticky=NW, rowspan=2)
        self.thumbnail_label.pack(anchor=NW, pady=(0,5))
        self.thumbnail_image.pack(anchor=NW)
        self.download_thumbnail_check.pack(anchor=NW, pady=(5,0))
        self.id_label.pack(anchor=NW, pady=(5,0))
        caption_label.pack(anchor=NW)
        self.caption_list.pack(anchor=NW, expand=TRUE, fill=X, pady=(5,0))
        self.caption_format_check.pack(anchor=NW, pady=(5,0))
        self.filter_label.pack(anchor=NW, pady=(10,0))
        self.filter_frame.pack(anchor=NW, pady=(5,0), expand=TRUE, fill=BOTH)
        self.format_radio_1.grid(row=0, column=0, sticky=NW)
        self.format_radio_2.grid(row=0, column=1, padx=(14,0), sticky=NW)
        self.format_radio_3.grid(row=0, column=2, padx=(14,0), sticky=NW)
        self.format_radio_4.grid(row=0, column=3, padx=(14,0), sticky=NW)
        self.format_radio_5.grid(row=0, column=4, padx=(14,0), sticky=NW)
        self.filter_radio_1.grid(row=1, column=0, pady=(7,0), sticky=NW, columnspan= 5)
        second_row.grid(row=2, column=0, pady=(7,0), sticky=NW, columnspan= 5)
        self.filter_radio_2.grid(row=0, column=0, sticky=NW)
        self.filter_radio_3.grid(row=0, column=1, padx=(14,0), sticky=NW)
        self.list_frame.pack(anchor=NW, pady=(10,0), expand=TRUE, fill=BOTH)
        self.video_vscroll.pack(side=RIGHT, fill=Y)
        self.video_list.pack(anchor=NW, fill=X, expand=True)
        self.itag_label.pack(anchor=NW, pady=(5,0))
        self.download_frame.grid(row=0,column=2, sticky=NW, rowspan=2)
        filename_label.pack(anchor=NW)
        self.filename_entry.pack(anchor=NW, pady=(5,0))
        self.naming_check.pack(anchor=NW, pady=(5,0))
        location_label.pack(anchor=NW, pady=(10,0))
        self.directory_entry.pack(anchor=NW, pady=(5,0))
        self.directory_button.pack(anchor=NW, pady=(5,0))
        self.create_folder_check.pack(anchor=NW, pady=(5,0))
        self.download_button.pack(anchor=NW, pady=(30,0))
        option_frame.grid(row=0, column=4, sticky=NE)
        self.close_button.pack(pady=(8,0))
        self.close_label.pack(pady=(10,0))

        

        self.video_list.bind('<ButtonRelease-1>', lambda event: self.get_list_items())
        self.video_list.bind('<Up>', lambda event: self.get_list_items(index=-1))
        self.video_list.bind('<Down>', lambda event: self.get_list_items(index=1))
        


    def autofill_entry(self, widget, action):
        if widget == 1:
            if self.url.get() == '' and action == 0:
                self.url.set('Insert video URL')
            elif self.url.get() == 'Insert video URL' and action == 1:
                self.url.set('')
        elif widget == 2:
            if self.filename.get() == '':
                self.filename.set(self.vd.FILENAME[0])
        elif widget == 3:
            i = self.directory.get()
            if i == '' or os.path.isdir(i) == False:
                self.vd.DIRECTORY = 'C:/Users/User/Downloads'
                self.directory.set(self.vd.DIRECTORY)
 

    def select_directory(self):
        i = askdirectory(initialdir='C:/Users/User/Downloads', mustexist=True, title='Select Directory')
        if i != '':
            self.vd.DIRECTORY = i
            self.directory.set(self.vd.DIRECTORY)

    def confirm_input(self):
        self.confirm_entry_button['state'] = ttk.DISABLED
        self.download_button['state'] = ttk.DISABLED
        self.url_entry['state'] = ttk.DISABLED
        self.url_alert.config(text='')
        
        retries = 1
        for x in range(retries):
            try:
                i = self.vd.validate_url(self.url.get())
                if i == 'valid':
                    self.vd.get_video_description()
                    self.vd.get_thumbnail()
                    self.display_video_description()
                    break
                else:
                    if i == 'empty':
                        a = 'Insert video URL'
                    elif i == 'invalid':
                        a = 'Invalid URL'
                    elif i == 'age-restricted':
                        a = 'This video is age-restricted'
                    elif i == 'live':
                        a = 'This video is a live stream'
                    elif i == 'blocked':
                        a = 'This video is blocked in your region'
                    elif i == 'private':
                        a = 'This video is private'
                    elif i == 'unavailable':
                        a = 'Video Unavailable'
                    
                    self.url_alert['text'] = 'ERROR: ' + a
                    break
            except Exception as e:
                if x < retries -1:
                    continue
                else:
                    self.url_alert['text'] = f"There's an error when accessing this video:\n{textwrap.shorten(str(e),width=60, placeholder='...')}\n Try checking your internet connection."
            
        self.confirm_entry_button['state'] = ttk.NORMAL
        self.download_button['state'] = ttk.NORMAL
        self.url_entry['state'] = ttk.NORMAL
    
    def display_video_description(self):
        self.video_title.config(text=f'Title:\t{self.vd.DESCRIPTION["title"]}')
        self.video_length.config(text=f'Length:\t{self.vd.DESCRIPTION["length"]} seconds')
        self.video_author.config(text=f'Author:\t{self.vd.DESCRIPTION["author"]}')
        self.publish_date.config(text=f'Publish Date:\t{self.vd.DESCRIPTION["publish_date"].strftime("%c")}')
        self.views.config(text=f'Views:\t{str(self.vd.DESCRIPTION["views"])} views')
        self.video_desc.delete(1.0, END)
        self.video_desc.insert(END, str(self.vd.DESCRIPTION['description']))
        self.thumbnail_image['image'] = self.vd.DESCRIPTION['thumbnail']
        self.download_thumbnail_check['state'] = ttk.NORMAL
        self.caption_format_check['state'] = ttk.NORMAL
        self.id_label.config(text=f'Generated ID:\t{self.vd.DESCRIPTION["random_id"]}')
        self.itag_label['text'] = 'Selected itag:\t-'
        self.selected_itag = ''
        self.filename_entry['state'] = ttk.NORMAL
        self.directory_entry['state'] = ttk.NORMAL
        self.filename.set(self.vd.FILENAME[0])
        self.filename_entry.bind("<FocusOut>", lambda event: self.autofill_entry(2,0))
        self.directory_entry.bind("<FocusOut>", lambda event: self.autofill_entry(3,0))
        self.naming_check['state'] = ttk.NORMAL
        self.directory_button['state'] = ttk.NORMAL
        self.directory_entry['state'] = ttk.NORMAL
        self.create_folder_check['state'] = ttk.NORMAL

        
        a = []
        for i in range(len(self.vd.DESCRIPTION['captions_lang'])):
            a.append(self.vd.DESCRIPTION['captions_lang'][i])
        a.append('none')
        self.caption_list['values'] = a
        self.caption_list.current(0)
        self.caption_list['state'] = ttk.READONLY
        self.format_radio_1['state'] = ttk.NORMAL
        self.format_radio_2['state'] = ttk.NORMAL
        self.format_radio_3['state'] = ttk.NORMAL
        self.format_radio_4['state'] = ttk.NORMAL
        self.format_radio_5['state'] = ttk.NORMAL
        self.filter_radio_1['state'] = ttk.NORMAL
        self.filter_radio_2['state'] = ttk.NORMAL
        self.filter_radio_3['state'] = ttk.NORMAL
        self.change_list_items()
    

    def change_list_items(self):
        
        a = self.video_format.get()

        for row in self.video_list.get_children():
            self.video_list.delete(row)
        
        if not self.vd.STREAM_DATA[a] == []:
            for i, item in enumerate(self.vd.STREAM_DATA[a]):
                if self.list_filter.get() == 0:
                    if item['type'] == 'video' and item['progressive']:
                        self.video_list.insert(parent='', index='end', iid=i, values=(
                            item['itag'],
                            item['res'],
                            item['fps'],
                            "-",
                            item['filesize'],
                            item['type']))
                    
                elif self.list_filter.get() == 1:
                    if item['type'] == 'video' and not item['progressive']:
                        self.video_list.insert(parent='', index='end', iid=i, values=(
                            item['itag'],
                            item['res'],
                            item['fps'],
                            "-",
                            item['filesize'],
                            item['type']))
                
                else:
                    if item['type'] == 'audio':
                        self.video_list.insert(parent='', index='end', iid=i, values=(
                            item['itag'],
                            "-",
                            "-",
                            item['bitrate'],
                            item['filesize'],
                            item['type']))
        
        
    def get_list_items(self, index=0):
        item = self.video_list.focus()
        if not item == '':
            new_item = str(int(item) + index)
            if (int(new_item) > len(self.video_list.get_children())-1 or int(new_item) < 0):
                if int(new_item) > len(self.video_list.get_children())-1:
                    new_item = str(item)
                else:
                    new_item = '0'
            
            self.selected_itag = self.video_list.item(new_item)['values'][0]
            self.FORMAT = self.video_format.get()
            self.itag_label['text']= f'Selected itag:\t{self.selected_itag}'
            self.download_button['state'] = ttk.NORMAL
    
    def prepare_download(self):
        self.download_button['state'] = ttk.DISABLED
        self.vd.FILENAME[0] = self.filename.get()
        self.vd.DIRECTORY = self.directory.get()
        config.IS_DOWNLOADING = True
        if type(self.toplevel) == ttk.Toplevel:
            self.toplevel.destroy()
        self.toplevel = Video_Toplevel(self)
    


class Video_Toplevel(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(title='Downloading...', size=(500,400), resizable=(False, False))
        self.place_window_center()
        self.parent = parent
        self.caption = ''
        self.vd = parent.vd

        if parent.download_thumbnail.get():
            img = parent.thumbnail_image['image']
        else:
            img = parent.thumbnail_image.image
        
        self.main_frame = ttk.Labelframe(self, text= 'Download Details', padding=10)
        self.thumbnail_size_label = ttk.Label(self.main_frame, text='Thumbnail: -')
        self.thumbnail_image = ttk.Label(self.main_frame)
        self.thumbnail_image['image'] = img
        self.caption_size_label = ttk.Label(self.main_frame, text='Captions: -')
        self.progress_frame = ttk.Frame(self.main_frame)
        self.status_label = ttk.Label(self.progress_frame, text='Initializing..')
        self.progress_label = ttk.Label(self.progress_frame, text='-')
        self.progress_bar = ttk.Progressbar(self.progress_frame, orient=HORIZONTAL, mode='determinate', length=480, bootstyle='primary')
        self.time_remaining = ttk.Label(self.progress_frame, text='Time remaining: ')
        

        self.main_frame.pack(expand=TRUE, fill=BOTH, padx=10, pady=(10,20))
        self.thumbnail_size_label.pack(anchor=NW)
        self.thumbnail_image.pack(anchor=NW)
        self.caption_size_label.pack(anchor=NW)
        self.progress_frame.pack(side=BOTTOM, pady=(0,10))
        self.status_label.pack(anchor=NW)
        self.progress_label.pack(anchor=NW)
        self.progress_bar.pack(pady=(5,0))
        self.time_remaining.pack(pady=(5,0), anchor=NW)
        self.protocol('WM_DELETE_WINDOW', self.close_alert)

        a = self.prepare()
        
        if a:
            self.update()
            threading.Thread(target=self.download, daemon=True).start()

    def close_window(self):
        self.parent.download_button['state'] = ttk.NORMAL
        config.IS_DOWNLOADING = False
        self.destroy()


    def close_alert(self):
        i = messagebox.askyesno(
            title='Close Window',
            message='Closing this window will stop the progress. Do you want to continue?',
            parent = self
        )
        if i:
            self.close_window()
    
    
    def prepare(self):
        a = self.vd.prepare_directory(self, self.parent.using_id.get(), self.parent.create_folder.get())
        if a == False:
            self.parent.download_button['state'] = ttk.NORMAL
            config.IS_DOWNLOADING = False
            self.destroy()
        
        b = self.vd.prepare_items(
            self,
            self.parent.FORMAT,
            self.parent.caption_is_srt.get(),
            self.parent.selected_captions.get(),
            self.parent.download_thumbnail.get()
        )

        if b != False:
            thumb_size, sub_size, self.caption = b
            if self.parent.download_thumbnail.get():
                self.thumbnail_size_label['text'] = f'Thumbnail: {thumb_size}'
            if self.caption != '':
                self.caption_size_label['text'] = f'Captions: {self.parent.selected_captions.get()} ({sub_size})'
            return True
        else:
            self.parent.download_button['state'] = ttk.NORMAL
            config.IS_DOWNLOADING = False
            self.destroy()
    

    def download(self):
        try:
            self.start_download_time = datetime.now()
            def on_progress_callback(stream, chunk, bytes_remaining):
                total_size = stream.filesize
                time_elapsed = (datetime.now() - self.start_download_time).total_seconds()
                formatted_size = self.vd.get_formatted_size(total_size)
                bytes_downloaded = total_size - bytes_remaining
                percentage_completed = round(bytes_downloaded / total_size * 100)
                download_speed = bytes_downloaded / time_elapsed
                time_remaining = round(((bytes_remaining / 1024) / 1024) / float(download_speed / 1024 / 1024))
                self.progress_bar['value'] = percentage_completed
                self.progress_label['text'] = f'{percentage_completed}% ({self.vd.get_formatted_size(bytes_downloaded)}/{formatted_size}, speed: {self.vd.get_formatted_size(download_speed, suffix="b")}ps)'
                self.time_remaining['text'] = f'Time remaining: {time_remaining} seconds'
                self.update()
            
            self.vd.VIDEO.register_on_progress_callback(on_progress_callback)
            stream = self.vd.VIDEO.streams.get_by_itag(int(self.parent.selected_itag))

            self.status_label['text'] = 'Downloading video..'
            stream.download(filename=self.vd.FILENAME[0], output_path=self.vd.DIRECTORY)
        
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message=f'There\'s an error while downloading the video:\n{e}\nTry checking your internet connection.'
            )

        
        self.parent.download_button['state'] = ttk.NORMAL
        config.IS_DOWNLOADING = False
        self.destroy()