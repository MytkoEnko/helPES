from tkinter import *
from tkinter.ttk import *
import main
from PIL import ImageTk, Image
import os

class PesGui:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        # ----------- Menu ------------
        self.menu = Menu(master) # create menu
        menu = self.menu
        master.config(menu=menu) #point menu to created menu

        self.sub_menu = Menu(menu) # declare submenu (also menu
        submenu = self.sub_menu
        self.menu.add_cascade(label="Edit", menu=submenu) # Make menu expandable, it's objects are sub_menu
        submenu.add_command(label="Settings", command=self.print_message)
        submenu.add_command(label="About", command=self.print_message)
        submenu.add_separator()
        submenu.add_command(label="Exit", command=frame.quit)

        #support menu
        self.support_menu = Menu(self.menu)
        support = self.support_menu
        self.menu.add_cascade(label="Support", menu=support)
        support.add_command(label="Donate", command=self.print_message)

        # ----------- Toolbar ----------------

        self.tool_bar = Frame(master)
        toolbar = self.tool_bar
        toolbar.pack(side=TOP, fill=X)

        # ----------- LOGO ----------------
        self.img = PhotoImage(file="logo.png")
        self.panel = Label(toolbar, image=self.img)
        self.panel.pack(side=TOP, fill=BOTH, expand=YES)

        # ------------ Buttons ----------
        self.insert_button = Button(toolbar, text="Enable button", command=self.enable_button)
        self.insert_button.pack(padx=2, pady=2)

        self.print_button = Button(toolbar, text="Check path", command=self.print_message)
        self.print_button.pack(side=TOP)

        self.quit_button = Button(toolbar, text="Quit", command=frame.quit)
        self.quit_button.pack(side=TOP)

        # ----------- Status Section ----------
        self.status_section = Frame(master)
        self.status_section.pack(side=TOP, fill=Y)
        self.settings_ready = Label(self.status_section, text="Settings are ready: ",  anchor=W)
        self.settings_ready["text"] += 'Ok' if main.isthere(main.settings_file) and main.isthere(main.settings_backup) else 'No'
        self.settings_ready.pack(side=LEFT)
        self.settings_toggle = Button(
            self.status_section,
            text="Checking",
            command=self.settings_switch)
        self.settings_toggle["text"] = "Apply settings" if self.settings_ready["text"] == "Settings are ready: No" else "Revert"
        self.settings_toggle.pack(side=LEFT)

        # -----------  Run section -------------
        self.main_section = Frame(master)
        self.main_section.pack(side=TOP, fill=Y)

        # Entry sample
        self.smart_loop = Entry(self.main_section)
        self.smart_loop.insert(0,"Nr of games")
        self.smart_loop.pack()

        # Checkbutton settings
        flagvar = StringVar()
        self.loop_params = Checkbutton(
            self.main_section,
            text="Check me",
            variable=flagvar,
            state=DISABLED)
        self.loop_params.pack()

        # Radio button
        which_mode = StringVar()
        self.mode_standard = Radiobutton(self.main_section, text="Standard mode", value='standard')
        self.mode_custom = Radiobutton(self.main_section, text='Custom mode', value='custom')
        self.mode_limited = Radiobutton(self.main_section, text="Limited mode", value='limited')
        self.mode_standard.pack()
        self.mode_custom.pack()
        self.mode_limited.pack()


        # ----------- Status bar -------------
        self.status = Label(master, text="Path: ", borderwidth=1, relief=SUNKEN, anchor=W)
        self.status['text'] += eval(main.get_pes_exe())
        self.status.pack(side=BOTTOM, fill=X)


    def settings_switch(self):
        if self.settings_toggle["text"] == "Apply settings":
            main.makebkp()
            self.settings_toggle["text"] = "Revert"
            self.settings_ready["text"] = "Settings are ready: Ok"
        else:
            main.revertbackup()
            self.settings_ready["text"] = "Settings are ready: No"
            self.settings_toggle["text"] = "Apply settings"


    def print_message(self):
        print("Wow, this actually worked!")

    def enable_button(self):
        self.loop_params['state'] = '!disabled'
        print(f'Button enabled')


gui = Tk(className=" PES2020 Farmer") #create instance
######################
gui.geometry("600x400")
p = PesGui(gui)
gui.mainloop() # Run it