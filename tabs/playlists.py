from queue import Queue
import ttkbootstrap as ttk
import os
from tkinter.filedialog import askdirectory
import textwrap
from PIL import Image, ImageTk
from ttkbootstrap.constants import *
from tkinter import messagebox
#from ttkbootstrap.dialogs import Messagebox
from downloaders.playlists import Playlist_Downloader
import threading
from datetime import datetime

import config



class Playlist_Tab(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding=(30,10))
        
        self.vd = Playlist_Downloader(self)
        self.url = ttk.StringVar(value='Insert playlist URL')
        self.selected_videos = []
        self.filename = ttk.StringVar()
        self.download_thumbnail = ttk.BooleanVar(value=False)
        self.caption_is_srt = ttk.BooleanVar(value=True)
        self.playlist_format = ttk.StringVar(value='mp4')
        self.playlist_res = ttk.StringVar(value='hi')
        self.playlist_custom_res = ttk.IntVar(value=0)
        self.FORMAT = ''
        self.using_id = ttk.BooleanVar(value=True)
        self.directory = ttk.StringVar(value=self.vd.DIRECTORY)
        self.create_folder = ttk.BooleanVar(value=False)
        self.list_filter = ttk.IntVar()


        entry_frame = ttk.Frame(self)
        self.url_entry = ttk.Entry(entry_frame, bootstyle='primary', width=30, textvariable=self.url, takefocus=0)
        self.url_entry.bind("<FocusOut>", lambda event: self.autofill_entry(1,0))
        self.url_entry.bind("<FocusIn>", lambda event: self.autofill_entry(1,1))
        self.url_entry.bind('<Key>', lambda event: self.url_alert.config(text=''))
        self.url_entry.bind('<Return>', lambda event: threading.Thread(target=self.confirm_input, daemon=True).start())
        
        self.confirm_entry_button = ttk.Button(entry_frame, bootstyle='outline primary', text='confirm', command=lambda: threading.Thread(target=self.confirm_input, daemon=True).start())
        self.url_alert = ttk.Label(entry_frame, text='', bootstyle='warning')
        
        description_frame = ttk.Labelframe(self,text='Playlist Description', bootstyle='primary', padding=(10, 5, 10, 10))
        self.playlist_title = ttk.Label(description_frame, text='Title:\t-', wraplength=300)
        self.playlist_length = ttk.Label(description_frame, text='Length:\t-')
        self.playlist_author = ttk.Label(description_frame, text='Owner:\t-')
        self.publish_date = ttk.Label(description_frame, text='Last Updated:\t-')
        self.views = ttk.Label(description_frame, text='Views:\t-')

        desc_label = ttk.Label(description_frame, text='Description:')
        self.playlist_desc = ttk.Text(description_frame, width=40, wrap=WORD)

        settings_frame = ttk.Labelframe(self,text='Stream Settings', bootstyle='primary', padding=(10, 5, 10, 10))
        self.unavailable_vid_label = ttk.Label(settings_frame, text='Unavailable Videos:\t')
        self.download_thumbnail_check = ttk.Checkbutton(
            settings_frame,
            text='Download video thumbnail',
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.download_thumbnail,
            state=ttk.DISABLED)
        self.id_label = ttk.Label(settings_frame, text='Generated ID:\t-')
        #self.caption_label = ttk.Label(settings_frame, text='Captions:')
        #self.caption_list = ttk.Combobox(settings_frame, textvariable=self.selected_captions, state=ttk.DISABLED)
        self.caption_format_check = ttk.Checkbutton(
            settings_frame,
            text='Download as .srt file',
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.caption_is_srt,
            state=ttk.DISABLED)
        self.filter_label = ttk.Label(settings_frame, text='Format:')
        
        self.list_frame = ttk.Frame(settings_frame)
        self.playlist_list = ttk.Treeview(self.list_frame, height=8, columns=['title', 'author', 'length'], show='headings', selectmode='extended')
        self.playlist_list.heading('title', text='title')
        self.playlist_list.heading('author', text='author')
        self.playlist_list.heading('length', text='length')
       
        self.playlist_list.column('title', width=175, anchor=NW, stretch=False)
        self.playlist_list.column('author', width=105, anchor=NW, stretch=False)
        self.playlist_list.column('length', width=60, anchor=CENTER, stretch=True)

        self.playlist_hscroll = ttk.Scrollbar(self.list_frame, orient='horizontal', bootstyle='primary', command=self.playlist_list.xview)
        self.playlist_list.config(xscrollcommand=self.playlist_hscroll.set)
        
        self.playlist_vscroll = ttk.Scrollbar(self.list_frame, orient='vertical', bootstyle='primary', command=self.playlist_list.yview)
        self.playlist_list.config(yscrollcommand=self.playlist_vscroll.set)


        self.selection_label = ttk.Label(settings_frame, text='Selected videos:\t-')

        
        self.filter_frame = ttk.Frame(settings_frame)
        self.format_radio_1 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.playlist_format,
            value='mp4',
            text='.mp4',
            bootstyle='primary',
            state=ttk.DISABLED)
        self.format_radio_2 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.playlist_format,
            value='webm',
            text='.webm',
            bootstyle='primary',
            state=ttk.DISABLED)
        self.format_radio_3 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.playlist_format,
            value='mov',
            text='.mov',
            bootstyle='primary',
            state=ttk.DISABLED)
        self.format_radio_4 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.playlist_format,
            value='ogg',
            text='.ogg',
            bootstyle='primary',
            state=ttk.DISABLED)
        self.format_radio_5 = ttk.Radiobutton(
            self.filter_frame,
            variable=self.playlist_format,
            value='3gp',
            text='.3gp',
            bootstyle='primary',
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


        res_label = ttk.Label(settings_frame, text='Resolution:')
        self.res_frame = ttk.Frame(settings_frame)

        default_res = ttk.Label(self.res_frame, text='Default quality:')

        self.res_radio_1 = ttk.Radiobutton(
            self.res_frame,
            variable=self.playlist_res,
            value='hi',
            text='Hi',
            bootstyle='primary',
            state=ttk.DISABLED)
        self.res_radio_2 = ttk.Radiobutton(
            self.res_frame,
            variable=self.playlist_res,
            value='lo',
            text='Lo',
            bootstyle='primary',
            state=ttk.DISABLED)
        
        self.SCALE_LABELS = {
            0: 144,
            1: 240,
            2: 360,
            3: 480,
            4: 720,
            5: 1080,
            6: 1440,
            7: 2160,
        }
        
        self.res_label = ttk.Label(settings_frame, text='-')

        custom_res = ttk.Label(self.res_frame, text='Video resolution (if available):')

        self.custom_res_slider = ttk.Scale(
            settings_frame,
            variable=self.playlist_custom_res,
            from_=min(self.SCALE_LABELS),
            to= max(self.SCALE_LABELS),
            orient=HORIZONTAL,
            command=self.display_scale_value,
            state=ttk.DISABLED
        )




        download_frame = ttk.Labelframe(self,text='Download Settings', bootstyle='primary', padding=(10, 5, 10, 10))
        self.filename_label = ttk.Label(download_frame, text='File name:')
        self.filename_entry = ttk.Entry(download_frame, bootstyle='primary', width=50, textvariable=self.filename, state=ttk.DISABLED)
        self.naming_check = ttk.Checkbutton(
            download_frame,
            text="Add '- [generated_id]' behind file name",
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.using_id,
            state=ttk.DISABLED)
        
        location_label = ttk.Label(download_frame, text='File location:')
        self.directory_button = ttk .Button(download_frame, text='Select Directory', bootstyle= 'outline primary', command=self.select_directory, state=ttk.DISABLED)
        self.directory_entry = ttk.Entry(download_frame, bootstyle='primary', width=50, textvariable=self.directory, state=ttk.DISABLED)
        
        self.create_folder_check = ttk.Checkbutton(
            download_frame,
            text="Create folder",
            bootstyle='primary',
            offvalue=False,
            onvalue=True,
            variable=self.create_folder,
            state=ttk.DISABLED)
        
        self.download_button = ttk.Button(download_frame, text='Download', bootstyle= 'outline primary', state=ttk.DISABLED, command=self.prepare_download)
        option_frame = ttk.Frame(self)
        self.close_button = ttk.Button(option_frame, text='X', padding=(15,10), bootstyle='outline-primary', command=self.master.master.close_tabs)
        self.close_label = ttk.Label(option_frame, text='Close', bootstyle='primary')


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)

        entry_frame.grid(row=0,column=0, sticky=NW, pady=(8,0))
        self.url_alert.pack(anchor=NW, pady=(5,0))
        self.url_entry.pack(side=LEFT)
        self.confirm_entry_button.pack(side=LEFT, padx=(10,0))
        self.url_alert.pack(side=BOTTOM)
        description_frame.grid(row=1, column=0, sticky=NW)
        self.playlist_title.pack(anchor=NW)
        self.playlist_length.pack(anchor=NW)
        self.playlist_author.pack(anchor=NW)
        self.publish_date.pack(anchor=NW)
        self.views.pack(anchor=NW)
        desc_label.pack(anchor=NW)
        self.playlist_desc.pack(pady=(10,0), anchor=NW, expand=TRUE, fill=BOTH)
        settings_frame.grid(row=0,column=1, sticky=NW, rowspan=2)
        self.list_frame.pack(anchor=NW, pady=(5,0), expand=TRUE, fill=BOTH)
        self.playlist_vscroll.pack(side=RIGHT, fill=Y)
        self.playlist_hscroll.pack(side=BOTTOM, fill=X)
        self.playlist_list.pack(anchor=NW, fill=X, expand=True)
        self.unavailable_vid_label.pack(anchor=NW, pady=(5,0))
        self.selection_label.pack(anchor=NW, pady=(5,0))
        self.download_thumbnail_check.pack(anchor=NW, pady=(5,0))
        self.id_label.pack(anchor=NW, pady=(5,0))
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


        res_label.pack(anchor=NW, pady=(10,0))
        self.res_frame.pack(anchor=NW, pady=(5,0), expand=TRUE, fill=BOTH)
        default_res.grid(row=0, column=0, columnspan=2, sticky=NW)
        self.res_radio_1.grid(row=1, column=0,pady=(7,0), sticky=NW)
        self.res_radio_2.grid(row=1, column=1, padx=(14,0),pady=(7,0), sticky=NW)
        custom_res.grid(row=2, column=0, columnspan=2, pady=(7,0), sticky=NW)
        self.custom_res_slider.pack(fill=X, expand=TRUE, anchor=NW, pady=(5,0))
        self.res_label.pack(anchor=NW)
        
        download_frame.grid(row=0,column=2, sticky=NW, rowspan=2)
        self.filename_label.pack(anchor=NW)
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

        

        self.playlist_list.bind('<ButtonRelease-1>', lambda event: self.get_list_items())
        


    def autofill_entry(self, widget, action):
        if widget == 1:
            if self.url.get() == '' and action == 0:
                self.url.set('Insert playlist URL')
            elif self.url.get() == 'Insert playlist URL' and action == 1:
                self.url.set('')
        elif widget == 2:
            if self.filename.get() == '':
                self.filename.set(self.vd.FILENAME)
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
                i = self.vd.validate_url(self.url.get())
                if i == 'valid':
                    self.vd.get_playlist_description()
                    #self.vd.get_thumbnail()
                    self.display_playlist_description()
                    break
                else:
                    if i == 'empty':
                        a = 'Insert playlist URL'
                    elif i == 'invalid':
                        a = 'Invalid URL'
                    elif i == 'unavailable':
                        a = 'Playlist Unavailable'
                    
                    self.url_alert['text'] = 'ERROR: ' + a
                    break
            
            
            
        self.confirm_entry_button['state'] = ttk.NORMAL
        self.download_button['state'] = ttk.NORMAL
        self.url_entry['state'] = ttk.NORMAL
    
    def display_playlist_description(self):
        self.playlist_title.config(text=f'Title:\t{self.vd.DESCRIPTION["title"]}')
        self.playlist_length.config(text=f'Length:\t{self.vd.DESCRIPTION["length"]} videos')
        self.playlist_author.config(text=f'Owner:\t{self.vd.DESCRIPTION["owner"]}')
        self.publish_date.config(text=f'Last Updated:\t{str(self.vd.DESCRIPTION["last_updated"])}')
        self.views.config(text=f'Views:\t{str(self.vd.DESCRIPTION["views"])} views')
        self.playlist_desc.delete(1.0, END)
        self.playlist_desc.insert(END, str(self.vd.DESCRIPTION['description']))
        self.unavailable_vid_label.config(text=f'Unavailable Videos:\t{self.vd.unavailable_videos}')
        self.download_thumbnail_check['state'] = ttk.NORMAL
        self.caption_format_check['state'] = ttk.NORMAL
        self.id_label.config(text=f'Generated ID:\t{self.vd.DESCRIPTION["random_id"]}')
        self.selection_label['text'] = 'Selected videos:\t-'
        self.res_radio_1['state'] = ttk.NORMAL
        self.res_radio_2['state'] = ttk.NORMAL
        self.custom_res_slider['state'] = ttk.NORMAL
        self.filename_entry['state'] = ttk.NORMAL
        self.directory_entry['state'] = ttk.NORMAL
        self.filename.set(self.vd.FILENAME)
        self.filename_entry.bind("<FocusOut>", lambda event: self.autofill_entry(2,0))
        self.directory_entry.bind("<FocusOut>", lambda event: self.autofill_entry(3,0))
        self.naming_check['state'] = ttk.NORMAL
        self.directory_button['state'] = ttk.NORMAL
        self.directory_entry['state'] = ttk.NORMAL
        self.create_folder_check['state'] = ttk.NORMAL
        self.download_button['state'] = ttk.NORMAL
        self.custom_res_slider.set(0)
        self.change_list_items()
        self.display_scale_value(0)

        #self.toplevel = Video_Toplevel(self)

    

    def change_list_items(self):
        
        #a = self.playlist_format.get()

        for row in self.playlist_list.get_children():
            self.playlist_list.delete(row)
        
        for i, item in enumerate(self.vd.VIDEO_LIST):
            self.playlist_list.insert(parent='', index='end', iid=i, values=(
                item['title'],
                item['author'],
                F'{item["length"]} seconds'
            ))

        
    def display_scale_value(self, value):
        print(value)
        self.res_label['text'] = f'{self.SCALE_LABELS[int(self.custom_res_slider.get())]}p'

    def get_list_items(self, index=0):
        selection = self.playlist_list.selection()
        
        self.selected_videos.clear()
        print(selection)
        
        for i in selection:
            a = (self.playlist_list.item(item=selection[selection.index(i)], option='values')[0], selection.index(i))
            self.selected_videos.append(a)
            
        print(self.selected_videos)

        self.selection_label['text']= f'Selected videos:\t{len(self.selected_videos)}'
        self.download_button['state'] = ttk.NORMAL
    
    def prepare_download(self):
        self.download_button['state'] = ttk.DISABLED
        self.vd.FILENAME = self.filename.get()
        self.vd.DIRECTORY = self.directory.get()
        config.IS_DOWNLOADING = True
        self.toplevel = Video_Toplevel(self)
    


class Video_Toplevel(ttk.Toplevel):
    def __init__(self, parent):
        super().__init__(title='Downloading...', size=(500,400), resizable=(False, False))
        self.place_window_center()
        self.parent = parent
        self.caption = ''
        self.vd = parent.vd

        self.main_frame = ttk.Labelframe(self, text= 'Checking Availability', padding=10)
        status_label = ttk.Label(self.main_frame, text='Checking video availability..')
        self.progress_frame = ttk.Frame(self.main_frame, padding=10)
        self.video_count = ttk.Label(self.progress_frame, text=f'0 of {len(self.vd.VIDEO_LIST)} videos')
        self.count_bar = ttk.Progressbar(self.progress_frame, orient=HORIZONTAL, mode='determinate', length=480, bootstyle='primary', maximum=len(self.parent.selected_videos))

        self.main_frame.pack(expand=TRUE, fill=BOTH, padx=10, pady=(10,20))
        status_label.pack()
        self.progress_frame.pack(pady=(0,10))
        self.video_count.pack()
        self.count_bar.pack(pady=(5,0))
        
        def increment_value(percentage_completed):
            self.count_bar['value'] = percentage_completed
            self.video_count['text'] = f'{percentage_completed} of {len(self.parent.selected_videos)} videos'
            self.update()
        
        a = self.vd.check_stream_availability(self.parent.selected_videos, self.parent.FORMAT, self.parent.list_filter.get(), self.parent.SCALE_LABELS[int(self.parent.custom_res_slider.get())], self.parent.playlist_res, increment_value)

        status_label.destroy()
        for a in self.progress_frame.winfo_children():
            a.destroy
        self.progress_frame.destroy()

        list_frame = ttk.Frame(self.main_frame, borderwidth=3)
        self.availability_list = ttk.Treeview(list_frame, height=12 , columns=['video', 'available?'], show='headings', selectmode='none')
        self.availability_list.heading('video', text='video')
        self.availability_list.heading('available?', text='available?')
       
        self.availability_list.column('video', width=200, anchor=NW)
        self.availability_list.column('available?', width=50, anchor=CENTER)

        self.vscroll = ttk.Scrollbar(list_frame, orient='vertical', bootstyle='primary', command=self.availability_list.yview)
        self.availability_list.config(yscrollcommand=self.vscroll.set)


        unavailable_vid_label = ttk.Label(self.main_frame, text='Unavailable videos: ')

        list_frame.pack(expand=TRUE, fill=X)
        self.vscroll.pack(side=RIGHT, fill=Y)
        self.availability_list.pack(anchor=NW, fill=X, expand=True)
        unavailable_vid_label.pack(anchor=NW, padx=(20,0))

        vid = 0
        for video in self.parent.selected_videos:
            if self.vd.VIDEO_STREAMS[self.parent.selected_videos.index(video)] != '':
                self.availability_list.insert(parent='', index='end', iid=video[1], values=(
                    video[0],
                    '✓'
                ))
            else:
                self.availability_list.insert(parent='', index='end', iid=video[1], values=(
                    video[0],
                    '✗'
                ))
                vid += 1
        
        unavailable_vid_label['text'] = f'Unavailable videos: {vid}'
        
        """
        a = self.prepare()
        
        if a:
            self.update()
            threading.Thread(target=self.download, daemon=True).start()
        """
    
    def close_alert(self):
        i = messagebox.askyesno(
            title='Close Window',
            message='Closing this window will stop the progress. Do you want to continue?',
            parent = self
        )
        if i:
            self.parent.download_button['state'] = ttk.NORMAL
            config.IS_DOWNLOADING = False
            self.destroy()
    
    
    def prepare(self):
        
        b = self.vd.prepare_directory(self, self.parent.using_id.get(), self.parent.create_folder.get())
        if b == False:
            self.parent.download_button['state'] = ttk.NORMAL
            config.IS_DOWNLOADING = False
            self.destroy()
        
        c = self.vd.prepare_items(
            self,
            self.parent.FORMAT,
            self.parent.caption_is_srt.get(),
            self.parent.selected_captions.get(),
            self.parent.download_thumbnail.get()
        )

        if c != False:
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
            if self.parent.download_thumbnail.get():
                self.status_label['text'] = 'Downloading thumbnail..'
                with open(os.path.join(self.vd.DIRECTORY, 'thumbnail.png'), 'wb') as f:
                    f.write(self.vd.DESCRIPTION['thumbnail_data'])
                
            if self.caption != '':
                self.status_label['text'] = 'Downloading captions..'
                if self.parent.caption_is_srt.get():
                    with open(os.path.join(self.vd.DIRECTORY, 'captions.srt'), 'w', encoding='utf-8') as f:
                        f.write(self.caption)
                else:
                    with open(os.path.join(self.vd.DIRECTORY, 'captions.xml'), 'w', encoding='utf-8') as f:
                        f.write(self.caption)
        

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
            stream.download(filename=self.vd.FILENAME, output_path=self.vd.DIRECTORY)
        
        except Exception as e:
            messagebox.showerror(
                title='Error',
                message=f'There\'s an error while downloading the video:\n{e}\nTry checking your internet connection.'
            )

        
        self.parent.download_button['state'] = ttk.NORMAL
        config.IS_DOWNLOADING = False
        self.destroy()