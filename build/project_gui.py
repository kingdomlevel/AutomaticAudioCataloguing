from Tkinter import *
from tkFileDialog import askopenfilenames
from tkFileDialog import askdirectory
import tkMessageBox
from controller import Control
import os


class GUI:
    def __init__(self, master):
        # set up frames
        frame = Frame(master, bg="#cfeef2")
        frame.grid()
        left_frame = Frame(master)
        left_frame.grid(row=0, column=0, sticky=W, padx=10, pady=10)
        middle_frame = Frame(master, width=600, height=300)
        middle_frame.grid(row=0, column=1, sticky=W+E+N+S, padx=10, pady=10)
        middle_frame.grid_propagate(False)
        right_frame=Frame(master)
        right_frame.grid(row=0, column=2, sticky=E, padx=10, pady=10)

        # left buttons
        self.choose_file_preprocess = Button(left_frame, text="Pre-process file(s)", wraplength=120, command=self.preprocess)
        self.choose_file_preprocess.pack()
        self.choose_file = Button(left_frame, text="Add pre-processed file(s) to DB", wraplength=120, command=self.process)
        self.choose_file.pack()
        # centre text area
        output_label_text = "Output directory: %s" % output_loc
        self.output_label = Label(middle_frame, text=output_label_text)
        self.output_label.grid(sticky=W)
        centre_text = "{:<86}".format("Select files for [pre-]processing...")
        self.log_text = Text(middle_frame, height=12, width=86, bg="#f2defd")
        self.log_text.config(font=("Courier New", 14))
        self.log_text.delete(1.0, END)
        self.log_text.config(state=NORMAL)
        self.log_text.insert(END, centre_text)
        self.scroll = Scrollbar(middle_frame)
        self.log_text.grid()
        self.scroll.grid(sticky=E)
        self.scroll.config(command=self.log_text.yview)
        self.log_text.config(yscrollcommand=self.scroll.set)
        self.log_text.config(state=DISABLED)
        # right buttons
        self.change_output_loc_button = Button(right_frame, text="Change output directory", wraplength=60, command=self.change_output_dir)
        self.change_output_loc_button.pack()
        self.exit_button = Button(right_frame, text="Close", command=master.quit)
        self.exit_button.pack(anchor='center')

    def preprocess(self):
            input_files = askopenfilenames(title='Select file(s) to perform pre-processing on:')
            if not input_files:
                print "No file(s) selected"
            else:
                text_feedback = c.preprocess_input(input_files, output_loc)
                self.log_text.config(state=NORMAL)
                self.log_text.delete(1.0, END)
                self.log_text.insert(END, text_feedback)
                self.log_text.config(state=DISABLED)

    def process(self):
        input_files = askopenfilenames(title='Select file(s) to add to database:')
        if not input_files:
            print "No file(s) selected"
        else:
            text_feedback = c.process_files(input_files, output_loc)
            self.log_text.config(state=NORMAL)
            self.log_text.delete(1.0, END)
            self.log_text.insert(END, text_feedback)
            self.log_text.config(state=DISABLED)

    def change_output_dir(self):
        # choose directory
        while True:
            new_output_dir = askdirectory()
            if os.path.isdir(new_output_dir):
                global c
                global output_loc
                # valid directory: set for logic
                output_loc = new_output_dir
                c = Control(output_loc)
                # update display
                output_label_text = "Output directory: %s" % output_loc
                self.output_label.config(text=output_label_text)
                # self.output_label.grid()
                break
            else:
                # valid directory
                tkMessageBox.showwarning(
                    "Invalid Dirctory!",
                    "%s is not a valid directory to host output files." % new_output_dir
                )


# global variables
output_loc = "/Volumes/AdataHD710/preprocessed/"    # default value
c = Control(output_loc)
root = Tk()
root.wm_title("SMC Graph DB Tool")
root.geometry("900x300+30+30")
gui = GUI(root)

# run GUI
root.mainloop()