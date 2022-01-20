import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import requests

MIDDLE_URL = 'http://fantasiapp.tech:5101'


# create the root window
root = tk.Tk()
root.title("File categorizer")
root.resizable(False, False)
root.geometry('600x150')

def select_file():
    filetypes = (
        ('pdf files', '*.pdf'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open a file',
        # initialdir="C:\\Users\\Baptiste\\Documents\\Fantasiapp\\middleBatiuni\\assets",
        filetypes=filetypes)

    if filename:
        file_label['text']=filename

def process():
    files = {
        'file' : open(file_label['text'], 'rb')
    }
    data = {
        'title': file_label['text'],
    }
    response = requests.post(MIDDLE_URL, data=data, files=files)

    showinfo(
        title='Document category',
        message=response.content
            )
        # print(response.content)

        # showinfo(
        #     title='Error',
        #     message='An error occured'
        #     )
# file name
file_label = ttk.Label(
    root,
    text='No file selected'
)
file_label.grid(row=0, column=0, columnspan=3)

# open button
open_button = ttk.Button(
    root,
    text='Open a File',
    command=select_file
)

open_button.grid(row=1, column=0, columnspan=1)

# process button
process_button = ttk.Button(
    root,
    text='Process File',
    command=process
)

process_button.grid(row=2, column=0, columnspan=1)


# run the application
root.mainloop()