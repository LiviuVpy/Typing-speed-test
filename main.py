from tkinter import *
import random
import math
from tkinter.simpledialog import askstring
import json

WORDS = 50
timer = None
all_model_text = []
model_text = []
text = ""
typed_text = ""
written_text = ""
corrections = 0
name = ""
total_time_sec = 0
time_sec = 0
errors = 0

def get_name():
    global name
    name = askstring("Name", "\tWhat is your name?\t")
    
def get_all_text():
    with open("typing_speed_test\words.txt", encoding="utf8", mode='r') as file:
        content = file.readlines()
        for item in content:
            striped_words = item.strip()
            all_model_text.append(striped_words)

def get_model_text():
    global text
    random_words = random.sample(all_model_text, WORDS)
    for i in random_words:
        model_text.append(i)
    text = " ".join(model_text)

def count_timer(count):
    global timer
    count_sec = count 
    count_min = math.floor(count_sec/60)
    if count_sec > 59:
        count_sec = count%60
    if count_sec < 10:
        count_sec = f"0{count_sec}"
    if count_min < 10:
        count_min = f"0{count_min}"
    timer_text.config(text=f"{count_min} : {count_sec}")
    timer = root.after(1000, count_timer, count+1)

def speed_test(event):
    global typed_text, written_text, text, model_text, corrections
    typed_text += event.char
    if len(typed_text) == 1:
        count_timer(0)
    written_text = write_text.get("0.0", "end-1c") + event.char
    get_entered_text(event)
    if event.char == "\x08" or event.keysym== "Delete":
        corrections += 1
        corrections_text.config(text=corrections, fg='red')
    if text == written_text:
        root.after_cancel(timer)
        wps()
        words_text.config(text='0')
        save()
        
def get_entered_text(event):
    global compare
    mistakes_list = []
    words = main_text.get(0.0, END)
    words_list = words.split()
    entered_words = write_text.get("0.0", "end-1c") + event.char
    entered_word_list = entered_words.split()
    compare = [i for i in words_list if i in entered_word_list]
    if len(compare) > 0:
        words_text.config(text=len(model_text)-len(compare))
    if len(compare) < 1:
        words_text.config(text=len(model_text))
    written_text_label.config(text=len(compare))
                
def restart():
    global typed_text, written_text, text, model_text, timer, corrections
    root.after_cancel(timer)
    main_text.delete(0.0, END)
    write_text.delete(0.0, END)
    model_text = []
    written_text = "" 
    typed_text = ""
    text = ""
    timer_text.config(text='00 : 00')
    get_model_text()
    main_text.insert(0.0, text)
    words_text.config(text=len(model_text))  
    corrections = 0 
    corrections_text.config(text="00", fg='black')
    wpm_text.config(text="00")
    written_text_label.config(text="00") 
    update_perf()

def wps():
    global total_time_sec, time_sec
    finish_time = timer_text.cget('text') 
    total_time_sec = int(finish_time[-2:])
    time_min = int(finish_time[:2])
    if time_min > 0:
        total_time_sec = total_time_sec + time_min*60
        wps = round(len(compare)*60/total_time_sec, 2)
    else:
        wps = round(len(compare)*60/total_time_sec, 2)
    wpm_text.config(text=wps)

def save():
    global total_time_sec, time_sec
    new_data = {
        name : {
             "time" : timer_text['text'],
             "corrections" : corrections_text['text'],
             "WPM" : wpm_text['text']
        }
    }
    
    try:
        with open("typing_speed_test\details.json", "r") as data_file:  
            # reading old data:
            data = json.load(data_file)   
    except FileNotFoundError:
            with open("typing_speed_test\details.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4) 
    except Exception:
            with open("typing_speed_test\details.json", "w") as data_file:
                json.dump(new_data, data_file, indent=4)  
    else:
        if name in data:
            data_time = data[name]["time"]
            if int(data_time[:2]) > 0:
                total_data_time = int(data_time[-2:])*60 + int(data_time[-2:])
            else:
                total_data_time = int(data_time[-2:])

            if total_data_time > total_time_sec:
            #updating old data with new data:
                data.update(new_data)
                with open("typing_speed_test\details.json", "w") as data_file:
                # saving updated data:
                    json.dump(data, data_file, indent=4)
        else:
            data.update(new_data)
            with open("typing_speed_test\details.json", "w") as data_file:
                # saving updated data:
                json.dump(data, data_file, indent=4) 

def update_perf():
    try:
        with open("typing_speed_test\details.json", "r") as data_file:  
            # reading old data:
            data = json.load(data_file)   
    except FileNotFoundError:
            pass 
    except Exception:
            pass  
    else:
        if name in data:
            timetext.config(text=data[name]['time'])
            prev_corrections_text.config(text=data[name]['corrections'])
            prev_wpm_text.config(text=data[name]['WPM'])

get_all_text()
get_model_text()
get_name()


# main window
root = Tk()

root.title("Typing speed test")
root.config(padx=30, pady=30)
# root.minsize(width=800, height=600)

frame = Frame(root)
frame.grid(row=0, column=0)

title_label = Label(frame, text="Test your typing speed!", font=("Arial", 12, "italic", "underline"))
title_label.grid(row=0, column=0, sticky=W, padx=10, pady=10)

detail_label = Label(frame, 
                     text="The timer will start when you type the first letter and it will stop when the last letter of the text is typed!", 
                     font=("Arial", 11, "italic"), justify="left")
detail_label.grid(row=1, column=0, sticky=W, padx=11)

# main text frame
mode_text_frame = LabelFrame(frame, text="Here is the text!", font=("Arial", 11, "normal"), foreground='blue')  
mode_text_frame.grid(row=2, column=0, columnspan=2, sticky=W, padx=10, pady=10)

main_text = Text(mode_text_frame, height=7, width=80, font=("Arial", 13, "normal"))
main_text.grid(row=1, column=0, columnspan=2, sticky=EW, padx=10, pady=10)
main_text.insert(0.0, text)

# write text frame
write_label = Label(frame, text="Write below as fast as you can!", font=("Arial", 11, "italic"))
write_label.grid(row=3, column=0, sticky=W, padx=10, pady=10)

write_text_frame = LabelFrame(frame, text="Write in this box!", font=("Arial", 11, "normal"), foreground='blue')  
write_text_frame.grid(row=4, column=0, columnspan=2, sticky=W, padx=10, pady=10)

write_text = Text(write_text_frame, height=7, width=80, font=("Arial", 13, "normal"))
write_text.grid(row=4, column=0, columnspan=2, rowspan=2, sticky=EW, padx=10, pady=10)
key_funcid = write_text.bind("<Key>", speed_test, "+")

# performance frame
performance_frame = LabelFrame(frame, text="Current performance", font=("Arial", 11, "normal"), foreground='blue')  
performance_frame.grid(row=0, column=2, rowspan=3, columnspan=2, sticky="news", padx=10, pady=10)

timer_label = Label(performance_frame, text="Timer:", font=("Arial", 11, "normal"))
timer_label.grid(row=1, column=1, sticky=W, padx=10, pady=10)
timer_text = Label(performance_frame, text="00 : 00", font=("Arial", 13, "normal"))
timer_text.grid(row=1, column=2, sticky=E, padx=10, pady=10)

words_label = Label(performance_frame, text="Words to write:", font=("Arial", 11, "normal"))
words_label.grid(row=2, column=1, sticky=W, padx=10, pady=10)
words_text = Label(performance_frame, text=f"{len(model_text)}", font=("Arial", 13, "normal"))
words_text.grid(row=2, column=2, sticky=E, padx=10, pady=10)

corrections_label = Label(performance_frame, text="Corrections:", font=("Arial", 11, "normal"))
corrections_label.grid(row=3, column=1, sticky=W, padx=10, pady=10)
corrections_text = Label(performance_frame, text="00", font=("Arial", 13, "normal"))
corrections_text.grid(row=3, column=2, sticky=E, padx=10, pady=10)

written_label = Label(performance_frame, text="Written words:", font=("Arial", 11, "normal"))
written_label.grid(row=4, column=1, sticky=W, padx=10, pady=10)
written_text_label = Label(performance_frame, text="00", font=("Arial", 13, "normal"))
written_text_label.grid(row=4, column=2, sticky=E, padx=10, pady=10)

wpm_label = Label(performance_frame, text="WPM:", font=("Arial", 11, "normal"))
wpm_label.grid(row=5, column=1, sticky=W, padx=10, pady=10)
wpm_text = Label(performance_frame, text="00", font=("Arial", 13, "normal"))
wpm_text.grid(row=5, column=2, sticky=E, padx=10, pady=10)

# previous performance:
previous_frame = LabelFrame(frame, text="Previous best performance", font=("Arial", 11, "normal"), foreground='blue')  
previous_frame.grid(row=3, column=2, rowspan=2, columnspan=2, sticky="news", padx=10, pady=10)

name_label = Label(previous_frame, text="Name:", font=("Arial", 11, "normal"), fg='purple')
name_label.grid(row=0, column=1, sticky=W, padx=10, pady=10)
name_label_box = Label(previous_frame, text=f"{name}", font=("Arial", 11, "bold"), fg='purple')
name_label_box.grid(row=0, column=2,sticky=E, pady=10, padx=10)

timelabel = Label(previous_frame, text="Time:", font=("Arial", 11, "normal"))
timelabel.grid(row=1, column=1, sticky=W, padx=10, pady=10)
timetext = Label(previous_frame, text="00 : 00", font=("Arial", 13, "normal"))
timetext.grid(row=1, column=2, sticky=E,pady=10, padx=10)

prev_corrections_label = Label(previous_frame, text="Corrections:", font=("Arial", 11, "normal"))
prev_corrections_label.grid(row=2, column=1, sticky=W, padx=10, pady=10)
prev_corrections_text = Label(previous_frame, text="00", font=("Arial", 13, "normal"))
prev_corrections_text.grid(row=2, column=2, sticky=E, padx=10, pady=10)

prev_wpm_label = Label(previous_frame, text="WPM:", font=("Arial", 11, "normal"))
prev_wpm_label.grid(row=3, column=1, sticky=W, padx=10, pady=10)
prev_wpm_text = Label(previous_frame, text="00", font=("Arial", 13, "normal"))
prev_wpm_text.grid(row=3, column=2, sticky=E, pady=10, padx=10)


# buttons:
restart_button = Button(frame, text="Restart", font=("Arial", 10, "normal"), fg='blue', command=restart)
restart_button.grid(row=5, column=0, columnspan=4,  padx=10, pady=20, sticky=EW)

update_perf()

root.mainloop()
