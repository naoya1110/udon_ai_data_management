from turtle import update
import PySimpleGUI as sg
import cv2
import numpy as np
from time import time
import os
import shutil
from datetime import datetime
import pandas as pd

database_filepath = "research/UDON_AI_DATABASE/MAIN_DATABASE/udonya_database_main.xlsx"
df = pd.read_excel(database_filepath)

id_list = df["ID"].tolist()
udonya_name_list = df["udonya_name"].tolist()
udonya_id_names_all = [f"{str(id).zfill(4)}_{udonya_name}" for id, udonya_name in zip(id_list, udonya_name_list)]

target_main_dirpath = "research/UDON_AI_DATABASE/MAIN_DATABASE/IMAGES"

frame_size = 300
thumbnail_size = 150

target_dirpath = None
source_filepath = None

file_move_log = []

logtext = "Welcome!"

def padding_and_resize(img, size=(250, 250)):
    height, width, _ = img.shape
    old_size = max(height, width)
    frame = np.zeros((old_size, old_size, 3), dtype="uint8")
    if height > width:
        frame[:, int(old_size/2-width/2):int(old_size/2+width/2), :] = img
    else:
        frame[int(old_size/2-height/2):int(old_size/2+height/2), :, :] = img
    frame = cv2.resize(frame, size)
    return frame

def create_thumbnails_frame():
    thumbnails = []
    for i in range(2):
        raw = []
        for j in range(3):
            thumbnail = sg.Image(key=f"-thumbnail{i}{j}-",  data=blank_thumbnail)
            raw.append(thumbnail)
        thumbnails.append(raw)
    thumbnails_frame = sg.Frame("pictures", thumbnails)
    return thumbnails_frame

def update_thumbnails(target_dirpath):
    window["-TargetInfo-"].update(target_dirpath)
    filenames = os.listdir(target_dirpath)
    jpg_filenames = [x for x in filenames if ".jpg" in x ]
    for i in range(2):
        for j in range(3):
            k = (i+thumbnail_offset)*3+j
            if k < len(jpg_filenames):
                filepath = os.path.join(target_dirpath, jpg_filenames[k])
                img = imread(filepath)
                img = padding_and_resize(img, (thumbnail_size,thumbnail_size))
                imgbytes = cv2.imencode('.png', img)[1].tobytes()
                window[f'-thumbnail{i}{j}-'].update(data=imgbytes)
            else:
                window[f'-thumbnail{i}{j}-'].update(data=blank_thumbnail)

def clear_thumbnails():
    for i in range(2):
        for j in range(3):
            window[f'-thumbnail{i}{j}-'].update(data=blank_thumbnail)

def update_source_filelist(source_dirpath, search_word=None):
    filenames = os.listdir(source_dirpath)
    jpg_filenames = [x for x in filenames if ".jpg" in x]
    if len(search_word) > 0 :
        found_jpg_filenames = [x for x in jpg_filenames if search_word in x]
        window["-FileList1-"].update(values=found_jpg_filenames)
    else:
        window["-FileList1-"].update(values=jpg_filenames)

# ファイルパスに日本語が含まれる場合の対応
def imread(filename, flags=cv2.IMREAD_COLOR, dtype=np.uint8):
    try:
        n = np.fromfile(filename, dtype)
        img = cv2.imdecode(n, flags)
        return img
    except Exception as e:
        print(e)
        return None

blank_img = np.ones((frame_size, frame_size, 3), dtype="uint8")*255
blank_img = cv2.imencode('.png', blank_img)[1].tobytes()

blank_thumbnail = np.ones((thumbnail_size, thumbnail_size, 3), dtype="uint8")*255
blank_thumbnail = cv2.imencode('.png', blank_thumbnail)[1].tobytes()

sg.theme("System Default")

title1 = sg.Text("Source")
input1 = sg.Input("", size=(50,2), key="-DIR1-" )
folderbrowse1 = sg.FolderBrowse(enable_events=True, key="-FolderBrowse1-", size=(7,1))
open_button1 = sg.Button("Open", key="-Open1-", size=(7,1))
search_word1_el = sg.Input("", size=(50,2), key="-SearchWord1-" )
search_button1_el = sg.Button("Search", key="-SearchButton1-", size=(7,1))
clear_button1_el = sg.Button("Clear", key="-ClearButton1-", size=(7,1))
file_list1 = sg.Listbox(values=[], enable_events=True, size=(70, 10), key="-FileList1-", horizontal_scroll=True)
source_filename = sg.Multiline("", key="-SourceFilename-", size=(70,2))
image1 = sg.Image(key='-IMAGE1-', data=blank_img)
move_button = sg.Button("Move >>>", key="-Move-", size=(10,2))
undo_button = sg.Button("Undo", key="-Undo-", size=(10,2))
button_column1 = sg.Column([[move_button],
                            [undo_button]])


title2 = sg.Text("Target")
udonya_names_list_el = sg.Listbox(values=udonya_id_names_all, enable_events=True, size=(30, 10), key="-UdonyaNamesList-", horizontal_scroll=True)
udonya_id_txt = sg.Text("ID", size=(5, 1))
udonya_id_el = sg.Input("", key="-UdonyaID-", size=(30, 1))
udonya_name_txt = sg.Text("Name", size=(5, 1))
udonya_name_el = sg.Input("", key="-UdonyaName-", size=(30, 1))
udonya_tag_txt = sg.Text("Tag", size=(5, 1))
udonya_tag_el = sg.Input("", key="-UdonyaTag-", size=(30, 1))
udonya_area_txt = sg.Text("Area", size=(5, 1))
udonya_area_el = sg.Input("", key="-UdonyaArea-", size=(30, 1))
udonya_address_txt = sg.Text("Address", size=(5, 1))
udonya_address_el = sg.Input("", key="-UdonyaAddress-", size=(30, 1))
udonya_lat_txt = sg.Text("Lat", size=(5, 1))
udonya_lat_el = sg.Input("", key="-UdonyaLat-", size=(30, 1))
udonya_lon_txt = sg.Text("Lon", size=(5, 1))
udonya_lon_el = sg.Input("", key="-UdonyaLon-", size=(30, 1))

udonya_info_column = sg.Column([[udonya_id_txt, udonya_id_el],
                                [udonya_name_txt, udonya_name_el],
                                [udonya_tag_txt, udonya_tag_el],
                                [udonya_area_txt, udonya_area_el ],
                                [udonya_address_txt, udonya_address_el],
                                [udonya_lat_txt, udonya_lat_el],
                                [udonya_lon_txt, udonya_lon_el]])

target_info = sg.Multiline("", key="-TargetInfo-", size=(70, 2))
thumbnails_frame = create_thumbnails_frame()
thumbnail_offset = 0

title3 = sg.Text("Search Udonya")
search_word_el = sg.Input("", size=(40, 1), key="-SearchWord-")
search_button_el = sg.Button("Search", key="-Search-", size=(7,1))
search_button = sg.Button("Search", key="-Search-", size=(7,1))
clear_search_result_button_el = sg.Button("Clear", key="-ClearSearchResult-", size=(7,1))

add_new_udonya_button_el = sg.Button("Add New Udonya", key="-AddNewUdonya-", size=(7,2))

num_files_el = sg.Text("", size=(7,1), key="-NumFiles-")
top_button_el = sg.Button("Top", size=(7,2), key="-Top-")
up_button_el = sg.Button("Up", size=(7,2), key="-Up-")
down_button_el = sg.Button("Down", size=(7,2), key="-Down-")
bottom_button_el = sg.Button("Bottom", size=(7,2), key="-Bottom-")
button_column2 = sg.Column([[num_files_el],
                            [top_button_el],
                            [up_button_el],
                            [down_button_el],
                            [bottom_button_el]])

log_message = sg.Multiline(logtext, key="-LogMessage-", size=(400, 5), autoscroll=True)
quit_button = sg.Button("Quit", key="-Quit-", size=(7,1))

column1 = sg.Column([[title1],
                     [input1, folderbrowse1, open_button1],
                     [search_word1_el, search_button1_el, clear_button1_el],
                     [file_list1],
                     [source_filename],
                     [image1, button_column1]])

column2 = sg.Column([[title2],
                     [search_word_el, search_button_el, clear_search_result_button_el],
                     [udonya_names_list_el, udonya_info_column, add_new_udonya_button_el],
                     [target_info],
                     [thumbnails_frame, button_column2]])


layout = [[column1, column2],
          [log_message],
          [quit_button]]
            


window = sg.Window("test", layout, size=(1200,800))

while True:
    event, values = window.read(timeout=20)
    
    if event == "-FolderBrowse1-":
        window["-FileList1"].update([])

    if event == "-Open1-":
        print("open")
        source_dirpath = values["-FolderBrowse1-"]
        update_source_filelist(source_dirpath, search_word=values["-SearchWord1-"])

    if event == "-SearchButton1-":
        update_source_filelist(source_dirpath, search_word=values["-SearchWord1-"])
    
    if event == "-ClearButton1-":
        window["-SearchWord1-"].update("")
        update_source_filelist(source_dirpath, search_word="")

    if event == "-FileList1-":
        filename = values["-FileList1-"][0]
        source_filepath = os.path.join(source_dirpath, filename)
        img = imread(source_filepath)
        img = padding_and_resize(img, (frame_size,frame_size))
        imgbytes = cv2.imencode('.png', img)[1].tobytes()
        window['-IMAGE1-'].update(data=imgbytes)
        window["-SourceFilename-"].update(filename)
    
    if event == "-UdonyaNamesList-":
        selected_udonya = values["-UdonyaNamesList-"][0]
        print(selected_udonya)
        selected_udonya_id = int(selected_udonya.split("_")[0])
        df_selected_udonya = df[df["ID"]==selected_udonya_id]
        udonya_id = str(df_selected_udonya["ID"].iloc[0]).zfill(4)
        udonya_name = df_selected_udonya["udonya_name"].iloc[0]
        udonya_tag = df_selected_udonya["tag"].iloc[0]
        udonya_address = df_selected_udonya["address"].iloc[0]
        udonya_area = df_selected_udonya["area"].iloc[0]
        udonya_lat = df_selected_udonya["lat"].iloc[0]
        udonya_lon = df_selected_udonya["lon"].iloc[0]
        selected_udonya_dir = f'{udonya_id}_{udonya_tag}_{udonya_area}'
        window["-UdonyaID-"].update(udonya_id)
        window["-UdonyaName-"].update(udonya_name)
        window["-UdonyaTag-"].update(udonya_tag)
        window["-UdonyaArea-"].update(udonya_area)
        window["-UdonyaAddress-"].update(udonya_address)
        window["-UdonyaLat-"].update(udonya_lat)
        window["-UdonyaLon-"].update(udonya_lon)

        
        target_dirpath = os.path.join(target_main_dirpath, selected_udonya_dir)
        filenames = os.listdir(target_dirpath)
        jpg_filenames = [x for x in filenames if ".jpg" in x ]
        num_files = len(jpg_filenames)
        window["-NumFiles-"].update(num_files)
        thumbnail_offset = 0
        update_thumbnails(target_dirpath)

#----------------------------------------#
# control visible thumbnails
    if event == "-Top-":
        thumbnail_offset = 0
        update_thumbnails(target_dirpath)       

    if event == "-Down-":
        thumbnail_offset += 1
        update_thumbnails(target_dirpath)

    if event == "-Up-":
        if thumbnail_offset > 0: thumbnail_offset -= 1
        update_thumbnails(target_dirpath)

    if event == "-Bottom-":
        thumbnail_offset = num_files//3-1
        update_thumbnails(target_dirpath) 
#----------------------------------------#

#----------------------------------------#
# move an image file
    if event == "-Move-":
        if (target_dirpath != None) and (source_filepath != None):
            if os.path.normpath(target_dirpath) != os.path.normpath(source_dirpath):
                shutil.move(source_filepath, target_dirpath)
                print("Source File:", source_filepath)
                print("Target Directory:", target_dirpath)
                update_thumbnails(target_dirpath)
                filenames = os.listdir(target_dirpath)
                jpg_filenames = [x for x in filenames if ".jpg" in x ]
                num_files = len(jpg_filenames)
                window["-NumFiles-"].update(num_files)
                update_source_filelist(source_dirpath, search_word=values["-SearchWord1-"])
                window['-IMAGE1-'].update(data=blank_img)
                window["-SourceFilename-"].update("")
                now = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                logtext += f"\n{now} FILE MOVE: From {source_filepath} To {target_dirpath}"
                window["-LogMessage-"].update(logtext)
                file_move_log.append([source_dirpath, target_dirpath, filename])
                print(file_move_log)
            else:
                print("source and target direcories are same")
        else:
            print("you cannot move a file")
#----------------------------------------#

#----------------------------------------#
# undo moving an image file    
    if event == "-Undo-":
        if len(file_move_log) != 0:
            print("undo")
            source_dirpath, target_dirpath, filename = file_move_log[-1]
            source_filepath = os.path.join(source_dirpath, filename)
            undo_source_filepath = os.path.join(target_dirpath, filename)
            undo_target_dirpath = source_dirpath
            shutil.move(undo_source_filepath, undo_target_dirpath)
            file_move_log.pop(-1)
            update_source_filelist(source_dirpath, search_word=values["-SearchWord1-"])
            update_thumbnails(target_dirpath)
            logtext += f"\n{now} UNDO FILE MOVE: From {source_filepath} To {target_dirpath}"
            window["-LogMessage-"].update(logtext)
#----------------------------------------#
    
    if event == "-Search-":
        search_word = values["-SearchWord-"]

        found_udonya_id_names = [x for x in udonya_id_names_all if search_word in x]

        #df_found = df[df["udonya_name"].str.contains(search_word)]
        #found_udonya_names = df_found["udonya_name"].tolist()
        window["-UdonyaNamesList-"].update(found_udonya_id_names)
    
    if event == "-ClearSearchResult-":
        window["-UdonyaNamesList-"].update(udonya_id_names_all)
        window["-UdonyaID-"].update("")
        window["-UdonyaName-"].update("")
        window["-UdonyaTag-"].update("")
        window["-UdonyaArea-"].update("")
        window["-UdonyaAddress-"].update("")
        window["-UdonyaLat-"].update("")
        window["-UdonyaLon-"].update("")
        window["-TargetInfo-"].update("")
        clear_thumbnails()


    if event == "-AddNewUdonya-":
        print("add new udonya")
        new_udonya_id = int(df["ID"].tolist()[-1])+1
        new_udonya_name = values["-UdonyaName-"]
        new_udonya_tag = values["-UdonyaTag-"]
        new_udonya_area = values["-UdonyaArea-"]
        new_udonya_address = values["-UdonyaAddress-"]
        new_udonya_lat = values["-UdonyaLat-"]
        new_udonya_lon = values["-UdonyaLon-"]

        new_udonya ={"ID":new_udonya_id,
                     "udonya_name":new_udonya_name,
                     "tag":new_udonya_tag,
                     "area":new_udonya_area,
                     "address":new_udonya_address,
                     "lat":new_udonya_lat,
                     "lon":new_udonya_lon,
                    }
        new_udonya_text = f"ID:{str(new_udonya_id).zfill(4)}\n\
                            udonya_name:{new_udonya_name}\n\
                            tag:{new_udonya_tag}\n\
                            area:{new_udonya_area}\n\
                            address:{new_udonya_address}\n\
                            lat:{new_udonya_lat}\n\
                            lon:{new_udonya_lon}"

        if sg.popup_yes_no(f"新しいうどん屋さんを追加しますか?\n{new_udonya_text}") == "Yes":
            df = df.append(new_udonya, ignore_index=True)
            df.to_excel(database_filepath, index=False)
            id_list = df["ID"].tolist()
            udonya_name_list = df["udonya_name"].tolist()
            udonya_id_names_all = [f"{str(id).zfill(4)}_{udonya_name}" for id, udonya_name in zip(id_list, udonya_name_list)]
            window["-UdonyaNamesList-"].update(udonya_id_names_all)
            new_udonya_dirname = f'{str(new_udonya_id).zfill(4)}_{new_udonya_tag}_{new_udonya_area}'
            new_udonya_dirpath = os.path.join(target_main_dirpath, new_udonya_dirname)
            os.mkdir(new_udonya_dirpath)



    if event in (sg.WIN_CLOSED, "-Quit-"):
        break

