from tkinter import *
from tkinter.ttk import *
import main
from tkinter import filedialog
from PIL import ImageTk, Image
import os

class PesGui:
    def __init__(self, master):
        self.frame = Frame(master)
        self.frame.pack(fill=BOTH, padx=4, pady=1)

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
        submenu.add_command(label="Exit", command=self.frame.quit)

        #support menu
        self.support_menu = Menu(self.menu)
        support = self.support_menu
        self.menu.add_cascade(label="Support", menu=support)
        support.add_command(label="Donate", command=self.print_message)

        # ================== Top section =====================

        self.top_section = Frame(self.frame)
        topsection = self.top_section

        # ----------- LOGO ----------------
        self.img = PhotoImage(file="logo.png")
        self.logo = Label(topsection, image=self.img)

        # ----------- Description ----------
        self.description_frame = LabelFrame(topsection, text="About")
        self.description = Label(self.description_frame,wraplength=500, text="Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s")

        # ------------ Layout ---------------
        topsection.pack(side=TOP, fill=X)
        self.logo.pack(side=LEFT)
        self.description_frame.pack(side=LEFT, fill=BOTH, expand=YES)
        self.description.pack(side=TOP)


        # =============== Middle section ===============
        # --------- Layout ------------
        self.midwrap = Frame(self.frame)
        self.stats = LabelFrame(self.midwrap, text="Stats")
        self.actions = LabelFrame(self.midwrap, text="Actions")
        self.pes_settings = LabelFrame(self.midwrap, text="Settings")

        self.midwrap.pack(side=TOP, fill=X)
        self.pes_settings.pack(side=RIGHT, fill=Y)
        self.stats.pack(side=TOP, fill=X)
        self.actions.pack(side=TOP, fill=X)

        # ----------- Stats ------------
        stats_labels = dict(sticky=W, pady=3, padx=4)
        self.games_runtime = Label(self.stats, text="Games played").grid(row=0, column=2, **stats_labels)
        self.games_total = Label(self.stats, text="Games total").grid(row=0, column=4, **stats_labels)
        self.players_runtime = Label(self.stats, text="Players converted").grid(row=1, column=2, **stats_labels)
        self.players_total = Label(self.stats, text="Total converted").grid(row=1, column=4, **stats_labels)
        self.exp_left = Label(self.stats, text="EXP trainers slots left").grid(row=2, column=2, **stats_labels)

        stats_entry = dict(width=4, state=DISABLED)
        self.games_r = Entry(self.stats, **stats_entry)
        self.games_t = Entry(self.stats, **stats_entry)
        self.players_r = Entry(self.stats, **stats_entry)
        self.players_t = Entry(self.stats, **stats_entry)
        self.exp = Entry(self.stats, **stats_entry)

        self.games_r.grid(row=0, column=1)
        self.games_t.grid(row=0, column=3)
        self.players_r.grid(row=1, column=1)
        self.players_t.grid(row=1, column=3)
        self.exp.grid(row=2, column=1)

        #----------- Actions --------------

        actions_label_args = dict(sticky=W, pady=3, padx=4)
        self.team1_name = Label(self.actions, text="Team 1").grid(row=0, column=1, **actions_label_args)
        self.team2_name = Label(self.actions, text="Team 2").grid(row=1, column=1, **actions_label_args)

        self.team1_convert = BooleanVar(value=True)
        self.team2_convert = BooleanVar(value=True)
        self.team1_populate = BooleanVar(value=True)
        self.team2_populate = BooleanVar(value=True)
        self.sign_all = BooleanVar(value=True)

        self.t1_con = Checkbutton(self.actions, text="convert all players", variable=self.team1_convert)
        self.t1_pop = Checkbutton(self.actions, text="populate team", variable=self.team1_populate)
        self.t2_con = Checkbutton(self.actions, text="convert all players", variable=self.team2_convert)
        self.t2_pop = Checkbutton(self.actions, text="populate team", variable=self.team2_populate)
        self.sign_a = Checkbutton(self.actions, text="sign all scouts", variable=self.sign_all)
        self.perform = Button(self.actions, text="Perform", command=self.print_message)

        self.t1_con.grid(row=0, column=2, **actions_label_args)
        self.t1_pop.grid(row=0, column=3, **actions_label_args)
        self.t2_con.grid(row=1, column=2, **actions_label_args)
        self.t2_pop.grid(row=1, column=3, **actions_label_args)
        Separator(self.actions, orient=HORIZONTAL).grid(row=2,sticky="ew",columnspan=4)
        self.sign_a.grid(row=3, column=2, **actions_label_args)
        self.perform.grid(row=3, column=3, **actions_label_args)


        # ------------ Settings  ----------
        self.mail_send_var = BooleanVar(value=False)
        self.azure_vm_var = BooleanVar(value=False)
        self.shutdown_var = BooleanVar(value=False)
        self.players_cost_var = IntVar(value=15)

        self.mail_send = Checkbutton(self.pes_settings, text="Send email when script crashes or completes", variable=self.mail_send_var, command=self.use_mail)
        self.azure_vm = Checkbutton(self.pes_settings, text="Run on azure vm (see documentation)", variable=self.azure_vm_var, command=self.use_azure)
        self.shutdown = Checkbutton(self.pes_settings, text="Shutdown PC/VM when script ends/completes, delay minutes: ", variable=self.shutdown_var, command=self.use_shutdown)


        self.label_sendgrid = Label(self.pes_settings, text="sendgrid_token")
        self.label_mail = Label(self.pes_settings, text="email")

        self.label_client_id = Label(self.pes_settings, text="azure client ID")
        self.label_secret = Label(self.pes_settings, text="azure secret")
        self.label_tenant = Label(self.pes_settings, text="azure tenant")
        self.label_resource_group = Label(self.pes_settings, text="service group name")
        self.label_vm_name = Label(self.pes_settings, text="virtual machine name")

        self.label_players_cost = Label(self.pes_settings, text="Use players of cost (and less):")

        settings_entry = dict(width=35, state=DISABLED)

        self.sendgrid_token = Entry(self.pes_settings, **settings_entry)
        self.email_address = Entry(self.pes_settings, **settings_entry)

        self.az_client_id = Entry(self.pes_settings, **settings_entry)
        self.az_secret = Entry(self.pes_settings, **settings_entry)
        self.az_tenant = Entry(self.pes_settings, **settings_entry)
        self.az_resource_name = Entry(self.pes_settings, **settings_entry)
        self.az_vm = Entry(self.pes_settings, **settings_entry)

        player_cost_choices = [15,20,25,30]
        self.players_cost_select = Combobox(self.pes_settings, textvariable=self.players_cost_var, values=player_cost_choices, state='readonly')

        self.shutdown_delay = Entry(self.pes_settings, width=6, state=DISABLED)

        # Grid layout
        settings_lables = dict(sticky=E, pady=1, padx=4)

        self.mail_send.grid(column=1,row=1, columnspan=5, stick=W)
        self.label_sendgrid.grid(column=2, row=2, **settings_lables)
        self.label_mail.grid(column=2, row=3, **settings_lables)
        self.sendgrid_token.grid(column=3, row=2, columnspan=2)
        self.email_address.grid(column=3, row=3, columnspan=2)

        self.azure_vm.grid(column=1,row=4, columnspan=5, stick=W)
        self.label_client_id.grid(column=2, row=5, **settings_lables)
        self.label_secret.grid(column=2, row=6, **settings_lables)
        self.label_tenant.grid(column=2, row=7, **settings_lables)
        self.label_resource_group.grid(column=2, row=8, **settings_lables)
        self.label_vm_name.grid(column=2, row=9, **settings_lables)
        self.az_client_id.grid(column=3, row=5, columnspan=2)
        self.az_secret.grid(column=3, row=6, columnspan=2)
        self.az_tenant.grid(column=3, row=7, columnspan=2)
        self.az_resource_name.grid(column=3, row=8, columnspan=2)
        self.az_vm.grid(column=3, row=9, columnspan=2)

        self.label_players_cost.grid(column=1, row=10, columnspan=2, stick=W)
        self.players_cost_select.grid(column=4, row=10)

        self.shutdown.grid(column=1,row=11, columnspan=4, stick=W)
        self.shutdown_delay.grid(column=5, row=11)





        # =============== Bottom section ===============
        # --------- Layout ------------
        self.botwrap = Frame(self.frame)
        self.modes = LabelFrame(self.botwrap, text="Modes")
        self.checks = LabelFrame(self.botwrap, text="Checks")

        self.botwrap.pack(side=TOP, fill=X)
        self.modes.pack(side=LEFT, fill=Y)
        self.checks.pack(side=TOP, fill=X)

        # --------- Modes -------------
        self.which_mode = StringVar(value='standard')
        self.continue_serie = BooleanVar(value=True)
        self.games_numbar = IntVar(None,1000)


        self.mode_standard = Radiobutton(self.modes, text="Standard (Continue playing previous serie until exp trainers slot empty)", value='standard', variable=self.which_mode, command=self.toggle_mode)
        self.mode_custom = Radiobutton(self.modes, text='Custom mode: ', value='custom', variable=self.which_mode, command=self.toggle_mode)
        self.mode_limited = Radiobutton(self.modes, text="Limited (Do not convert/sign players, play same squads and renew contracts)", value='limited', variable=self.which_mode, command=self.toggle_mode)

        self.cont_s = Checkbutton(self.modes, text="Continue/start over", variable=self.continue_serie, state=DISABLED)
        self.to_play_val = Entry(self.modes, width=5, justify=RIGHT, textvariable=self.games_numbar, state=DISABLED)
        self.to_play = Label(self.modes, text="games to play")

        modes_grid = dict(sticky=W, pady=3, padx=4)
        self.mode_standard.grid(row=0, column=1, columnspan=4, **modes_grid)
        self.mode_custom.grid(row=1, column=1, **modes_grid)
        self.to_play_val.grid(row=1, column=2, padx=1)
        self.to_play.grid(row=1, column=3, **modes_grid)
        self.cont_s.grid(row=1, column=4, **modes_grid)
        self.mode_limited.grid(row=2, column=1, columnspan=4, **modes_grid)

        # -------- Checks -------------
        # Settings
        self.settings_ready = Label(self.checks, text="Settings are ready: ",  anchor=W, font='bold')
        self.settings_ready["text"] += 'Ok' if main.isthere(main.settings_file) and main.isthere(main.settings_backup) else 'No'
        self.settings_toggle = Button(
            self.checks,
            text="Checking",
            command=self.settings_switch)
        self.settings_toggle["text"] = "Copy settings" if self.settings_ready["text"] == "Settings are ready: No" else "Revert"
        self.settings_ready.config(foreground='red' if self.settings_ready["text"] == "Settings are ready: No" else "green")

        self.settings_ready.grid(row=1, column=1)
        self.settings_toggle.grid(row=1, column=2)

        #Game path
        self.game_path = eval(main.get_pes_exe())
        self.path_found_label = Label(self.checks, text="Game path: ", font='bold')
        self.path_found_label['text'] += 'detected' if len(self.game_path) > 3 else 'unknown'
        self.path_found_label['foreground'] = 'green' if self.path_found_label['text'] == "Game path: detected" else 'red'
        self.path_button = Button(
            self.checks,
            text='Select manually',
            command=self.select_path
        )

        self.path_found_label.grid(row=2, column=1)
        self.path_button.grid(row=2, column=2)


        # -------- Run / quit buttons
        self.insert_button = Button(self.botwrap, text="Start", command=self.start)
        self.insert_button.pack(side=LEFT, padx=2, pady=2)
        self.insert_button = Button(self.botwrap, text="Quit", command=self.frame.quit)
        self.insert_button.pack(side=LEFT, padx=2, pady=2)



        # ----------- Status bar -------------
        self.status = Label(master, text="Path: ", borderwidth=1, relief=SUNKEN, anchor=W)
        self.status['text'] += self.game_path
        self.status.pack(side=BOTTOM, fill=X)


    def settings_switch(self):
        if self.settings_toggle["text"] == "Copy settings":
            main.makebkp()
            self.settings_toggle["text"] = "Revert"
            self.settings_ready["text"] = "Settings are ready: Ok"
            self.settings_ready['foreground'] = "green"
        else:
            main.revertbackup()
            self.settings_ready["text"] = "Settings are ready: No"
            self.settings_toggle["text"] = "Copy settings"
            self.settings_ready['foreground'] = "red"


    def print_message(self):
        print("Wow, this actually worked!")


    def toggle_mode(self):
        if self.which_mode.get() == 'custom':
            self.cont_s['state'] = "!disabled"
            self.to_play_val['state'] = "!disabled"
        else:
            self.cont_s['state'] = "disabled"
            self.to_play_val['state'] = "disabled"

    def use_mail(self):
        if self.mail_send_var.get():
            self.sendgrid_token['state'] = '!disabled'
            self.email_address['state'] = '!disabled'
        else:
            self.sendgrid_token['state'] = 'disabled'
            self.email_address['state'] = 'disabled'


    def use_azure(self):
        if self.azure_vm_var.get():
            self.az_client_id['state'] = '!disabled'
            self.az_secret['state'] = '!disabled'
            self.az_tenant['state'] = '!disabled'
            self.az_resource_name['state'] = '!disabled'
            self.az_vm['state'] = '!disabled'
        else:
            self.az_client_id['state'] = 'disabled'
            self.az_secret['state'] = 'disabled'
            self.az_tenant['state'] = 'disabled'
            self.az_resource_name['state'] = 'disabled'
            self.az_vm['state'] = 'disabled'

    def use_shutdown(self):
        if self.shutdown_var.get():
            self.shutdown_delay['state'] = '!disabled'
        else:
            self.shutdown_delay['state'] = 'disabled'

    def select_path(self):
        self.filename = filedialog.askopenfilename(title="Choose your PES2020.exe file from installation folder", filetypes=[('PES2020.exe','PES2020.exe')])
        self.game_path = self.filename
        if len(self.game_path) > 3:
            self.path_found_label['text'] += 'Game path: detected'
            self.path_found_label['foreground'] = 'green'

    def new_window(self):
        self.window=Toplevel(gui)

    def start(self):
        self.frame.pack_forget()
        self.frame2 = Frame(self.master)



gui = Tk(className=" PES2020 Farmer") #create instance
######################
gui.geometry("800x540")
p = PesGui(gui)
gui.mainloop() # Run it