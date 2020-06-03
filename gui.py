from tkinter import *
from tkinter.ttk import *
import main
from tkinter import filedialog
from tkinter import messagebox
from PIL import ImageTk, Image
import os
import json
import threading
import logging

pes_config = main.pes_config



class PesGui:
    def __init__(self, master):
        global pes_config
        main.pes_gui = True

        # ================== Top section =====================

        self.top_section = Frame(master)
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

        # =================  FRAME 1 =========================
        self.frame = Frame(master)
        self.frame.pack(fill=BOTH, padx=4, pady=1)

        # ----------- Menu ------------
        self.menu = Menu(master) # create menu
        menu = self.menu
        master.config(menu=menu) #point menu to created menu

        self.sub_menu = Menu(menu) # declare submenu (also menu
        submenu = self.sub_menu
        self.menu.add_cascade(label="Edit", menu=submenu) # Make menu expandable, it's objects are sub_menu
        submenu.add_command(label="Settings", command=self.home_stats_collect)
        submenu.add_command(label="About", command=self.initial_stats_collect)
        submenu.add_separator()
        submenu.add_command(label="Exit", command=self.frame.quit)

        #support menu
        self.support_menu = Menu(self.menu)
        support = self.support_menu
        self.menu.add_cascade(label="Support", menu=support)
        support.add_command(label="Donate", command=self.print_message)


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

        #set variables and trace them
        stats_variables = (
            "games_played_var",
            "games_total_var",
            "players_runtime_var",
            "players_total_var",
            "exp_left_var"
        )

        for variable in stats_variables:
            setattr(self, variable, IntVar(value=pes_config['gui'][variable]))
            getattr(self, variable).trace_variable("w", self.save_configs)

        stats_labels = dict(sticky=W, pady=3, padx=4)
        self.games_runtime = Label(self.stats, text="Games played").grid(row=0, column=2, **stats_labels)
        self.games_total = Label(self.stats, text="Games total").grid(row=0, column=4, **stats_labels)
        self.players_runtime = Label(self.stats, text="Players converted").grid(row=1, column=2, **stats_labels)
        self.players_total = Label(self.stats, text="Total converted").grid(row=1, column=4, **stats_labels)
        self.exp_left = Label(self.stats, text="EXP trainers (of 150)").grid(row=2, column=2, **stats_labels)

        #Reset runtime to 0
        self.games_played_var.set(0)
        self.players_runtime_var.set(0)

        stats_entry = dict(width=4, state=DISABLED)
        self.games_r = Entry(self.stats, **stats_entry, textvariable=self.games_played_var)
        self.games_t = Entry(self.stats, **stats_entry, textvariable=self.games_total_var)
        self.players_r = Entry(self.stats, **stats_entry, textvariable=self.players_runtime_var)
        self.players_t = Entry(self.stats, **stats_entry, textvariable=self.players_total_var)
        self.exp = Entry(self.stats, **stats_entry, textvariable=self.exp_left_var)

        self.games_r.grid(row=0, column=1)
        self.games_t.grid(row=0, column=3)
        self.players_r.grid(row=1, column=1)
        self.players_t.grid(row=1, column=3)
        self.exp.grid(row=2, column=1)

        #----------- Actions --------------

        actions_label_args = dict(sticky=W, pady=3, padx=4)
        self.team1_name = Label(self.actions, text="Team 1").grid(row=0, column=1, **actions_label_args)
        self.team2_name = Label(self.actions, text="Team 2").grid(row=1, column=1, **actions_label_args)
        #variables
        self.team1_convert = BooleanVar(value=pes_config['gui']['team1_convert'])
        self.team2_convert = BooleanVar(value=pes_config['gui']['team2_convert'])
        self.team1_populate = BooleanVar(value=pes_config['gui']['team1_populate'])
        self.team2_populate = BooleanVar(value=pes_config['gui']['team2_populate'])
        self.convert_all = BooleanVar(value=pes_config['gui']['convert_all'])
        self.sign_all = BooleanVar(value=pes_config['gui']['sign_all'])
        self.sign_skip = IntVar(value=pes_config['gui']['sign_skip'])
        #add callback
        actions_variables = (
            "team1_convert",
            "team2_convert",
            "team1_populate",
            "team2_populate",
            "convert_all",
            "sign_all",
            "sign_skip"
        )

        for variable in actions_variables:
            #setattr(self, variable, IntVar(value=pes_config['gui'][variable]))
            getattr(self, variable).trace_variable("w", self.save_configs)
        # non standard callback

        self.t1_con = Checkbutton(self.actions, text="convert all players", variable=self.team1_convert)
        self.t1_pop = Checkbutton(self.actions, text="populate team", variable=self.team1_populate)
        self.t2_con = Checkbutton(self.actions, text="convert all players", variable=self.team2_convert)
        self.t2_pop = Checkbutton(self.actions, text="populate team", variable=self.team2_populate)
        self.conv_a = Checkbutton(self.actions, text="convert all players (of max cost -> settings)", variable=self.convert_all, command=self.use_convert_all)
        self.sign_a = Checkbutton(self.actions, text="sign scouts, skip: ", variable=self.sign_all, command=self.use_sign_all)
        self.sign_a_skip = Entry(self.actions, textvariable=self.sign_skip, justify=RIGHT, width=4, state=DISABLED)
        self.perform = Button(self.actions, text="Perform", command= lambda: self.start(perform=True))

        self.t1_con.grid(row=0, column=2, **actions_label_args)
        self.t1_pop.grid(row=0, column=3, **actions_label_args)
        self.t2_con.grid(row=1, column=2, **actions_label_args)
        self.t2_pop.grid(row=1, column=3, **actions_label_args)
        Separator(self.actions, orient=HORIZONTAL).grid(row=2,sticky="ew",columnspan=4)
        self.conv_a.grid(row=3, column=2, columnspan=2, **actions_label_args)
        self.sign_a.grid(row=4, column=2, **actions_label_args)
        self.sign_a_skip.grid(row=4, column=3, sticky=W)
        self.perform.grid(row=4, column=4, **actions_label_args)


        # ------------ Settings  ----------
        #variables
        self.mail_send_var = BooleanVar(value=pes_config['gui']['mail_send_var'])
        self.azure_vm_var = BooleanVar(value=pes_config['gui']['azure_vm_var'])
        self.shutdown_var = BooleanVar(value=pes_config['gui']['shutdown_var'])
        self.players_cost_var = IntVar(value=pes_config['gui']['players_cost_var'])
        self.delay_var = IntVar(value=pes_config['gui']['delay_var'])
        self.sendgrid_api_key = StringVar(value=pes_config['secrets']['sendgrid_api_key'])
        self.email_address = StringVar(value=pes_config['general']['email_address'])
        self.az_client_id = StringVar(value=pes_config['secrets']['az_client_id'])
        self.az_secret = StringVar(value=pes_config['secrets']['az_secret'])
        self.az_tenant = StringVar(value=pes_config['secrets']['az_tenant'])
        self.az_subscription_id = StringVar(value=pes_config['secrets']['az_subscription_id'])
        self.az_group_name = StringVar(value=pes_config['general']['az_group_name'])
        self.az_vm_name = StringVar(value=pes_config['general']['az_vm_name'])

        #add callback
        settings_callbacks = (
            "mail_send_var",
            "azure_vm_var",
            "shutdown_var",
            "players_cost_var",
            "delay_var",
            "sendgrid_api_key",
            "email_address",
            "az_client_id",
            "az_secret",
            "az_tenant",
            "az_subscription_id",
            "az_group_name",
            "az_vm_name",
        )

        for variable in settings_callbacks:
            getattr(self, variable).trace_variable("w", self.save_configs)

        self.mail_send = Checkbutton(self.pes_settings, text="Send email when script crashes or completes", variable=self.mail_send_var, command=self.use_mail)
        self.azure_vm = Checkbutton(self.pes_settings, text="Run on azure vm (see documentation)", variable=self.azure_vm_var, command=self.use_azure)
        self.shutdown = Checkbutton(self.pes_settings, text="Shutdown PC/VM when script ends/completes, delay minutes: ", variable=self.shutdown_var, command=self.use_shutdown)


        self.label_sendgrid = Label(self.pes_settings, text="sendgrid_token")
        self.label_mail = Label(self.pes_settings, text="email")

        self.email_test = Button(self.pes_settings, text="test email", command=self.test_email, state=DISABLED)
        self.azure_test = Button(self.pes_settings, text="test azure", command=self.test_azure, state=DISABLED)

        self.label_client_id = Label(self.pes_settings, text="azure client ID")
        self.label_secret = Label(self.pes_settings, text="azure secret")
        self.label_tenant = Label(self.pes_settings, text="azure tenant")
        self.label_subscription = Label(self.pes_settings, text="azure subscription id")
        self.label_resource_group = Label(self.pes_settings, text="service group name")
        self.label_vm_name = Label(self.pes_settings, text="virtual machine name")

        self.label_players_cost = Label(self.pes_settings, text="Use players of max cost:")

        settings_entry = dict(width=35, state=DISABLED)

        self.sendgrid_token = Entry(self.pes_settings, **settings_entry, textvariable=self.sendgrid_api_key)
        self.email_addr = Entry(self.pes_settings, **settings_entry, textvariable=self.email_address)

        self.az_cl_id = Entry(self.pes_settings, **settings_entry, textvariable=self.az_client_id)
        self.az_sec = Entry(self.pes_settings, **settings_entry, textvariable=self.az_secret)
        self.az_ten = Entry(self.pes_settings, **settings_entry, textvariable=self.az_tenant)
        self.az_subs = Entry(self.pes_settings, **settings_entry, textvariable=self.az_subscription_id)
        self.az_resource_name = Entry(self.pes_settings, **settings_entry, textvariable=self.az_group_name)
        self.az_vm = Entry(self.pes_settings, **settings_entry, textvariable=self.az_vm_name)

        player_cost_choices = [15,20,25,30]
        self.players_cost_select = Combobox(self.pes_settings, textvariable=self.players_cost_var, values=player_cost_choices, state='readonly')

        self.shutdown_delay = Entry(self.pes_settings, width=6, state=DISABLED, textvariable=self.delay_var)

        # Grid layout
        settings_lables = dict(sticky=E, pady=1, padx=4)

        self.mail_send.grid(column=1,row=1, columnspan=5, stick=W)
        self.email_test.grid(column=4, row=1, stick=E)
        self.label_sendgrid.grid(column=2, row=2, **settings_lables)
        self.label_mail.grid(column=2, row=3, **settings_lables)
        self.sendgrid_token.grid(column=3, row=2, columnspan=2)
        self.email_addr.grid(column=3, row=3, columnspan=2)

        self.azure_vm.grid(column=1,row=4, columnspan=5, stick=W)
        self.azure_test.grid(column=4, row=4, stick=E)
        self.label_client_id.grid(column=2, row=5, **settings_lables)
        self.label_secret.grid(column=2, row=6, **settings_lables)
        self.label_tenant.grid(column=2, row=7, **settings_lables)
        self.label_subscription.grid(column=2, row=8, **settings_lables)
        self.label_resource_group.grid(column=2, row=9, **settings_lables)
        self.label_vm_name.grid(column=2, row=10, **settings_lables)
        self.az_cl_id.grid(column=3, row=5, columnspan=2)
        self.az_sec.grid(column=3, row=6, columnspan=2)
        self.az_ten.grid(column=3, row=7, columnspan=2)
        self.az_subs.grid(column=3, row=8, columnspan=2)
        self.az_resource_name.grid(column=3, row=9, columnspan=2)
        self.az_vm.grid(column=3, row=10, columnspan=2)

        self.label_players_cost.grid(column=1, row=11, columnspan=2, stick=W)
        self.players_cost_select.grid(column=4, row=11)

        self.shutdown.grid(column=1,row=12, columnspan=4, stick=W)
        self.shutdown_delay.grid(column=5, row=12)



        # =============== Bottom section ===============
        # --------- Layout ------------
        self.botwrap = Frame(self.frame)
        self.modes = LabelFrame(self.botwrap, text="Modes")
        self.checks = LabelFrame(self.botwrap, text="Checks")

        self.botwrap.pack(side=TOP, fill=X)
        self.modes.pack(side=LEFT, fill=Y)
        self.checks.pack(side=TOP, fill=X)

        # --------- Modes -------------
        #variables
        self.which_mode = StringVar(value=pes_config['gui']['which_mode'])
        self.continue_serie = BooleanVar(value=pes_config['gui']['continue_serie'])
        self.games_number = IntVar(None,pes_config['gui']['games_number'])
        #callback
        self.which_mode.trace_variable("w", self.save_configs)
        self.continue_serie.trace_variable("w", self.save_configs)
        self.games_number.trace_variable("w", self.save_configs)

        self.mode_standard = Radiobutton(self.modes, text="Standard (Continue playing previous serie until exp trainers slot empty)", value='standard', variable=self.which_mode, command=self.toggle_mode)
        self.mode_custom = Radiobutton(self.modes, text='Custom mode: ', value='custom', variable=self.which_mode, command=self.toggle_mode)
        self.mode_limited = Radiobutton(self.modes, text="Limited (Do not convert/sign players, play same squads and renew contracts)", value='limited', variable=self.which_mode, command=self.toggle_mode)

        self.cont_s = Checkbutton(self.modes, text="Continue/start over", variable=self.continue_serie, state=DISABLED)
        self.to_play_val = Entry(self.modes, width=5, justify=RIGHT, textvariable=self.games_number, state=DISABLED)
        self.to_play = Label(self.modes, text="games to play")
        # Enable if custom is default
        self.toggle_mode()

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
        self.game_path = StringVar(value=eval(main.get_pes_exe()))
        self.path_found_label = Label(self.checks, text="Game path: ", font='bold')
        self.path_found_label['text'] += 'detected' if len(self.game_path.get()) > 3 else 'unknown'
        self.path_found_label['foreground'] = 'green' if self.path_found_label['text'] == "Game path: detected" else 'red'
        self.path_button = Button(
            self.checks,
            text='Select manually',
            command=self.select_path
        )

        self.path_found_label.grid(row=2, column=1)
        self.path_button.grid(row=2, column=2)

        # Tesseract check
        self.tesseract_label = Label(self.checks, text="Tesseract version:", font='bold')
        self.tesseract_version = Label(self.checks, text="Checking..")
        self.tesseract_check()

        self.tesseract_label.grid(row=3, column=1)
        self.tesseract_version.grid(row=3, column=2)


        # -------- Run / quit buttons
        self.start_button = Button(self.botwrap, text="Start", command=self.start)
        self.start_button.pack(side=LEFT, padx=2, pady=2)
        self.quit_button = Button(self.botwrap, text="Quit", command=self.frame.quit)
        self.quit_button.pack(side=LEFT, padx=2, pady=2)



        # ----------- Status bar -------------
        self.status = Label(master, text="Path: ", borderwidth=1, relief=SUNKEN, anchor=W)
        self.status['text'] += self.game_path.get()
        self.status.pack(side=BOTTOM, fill=X)

        # ================== FRAME 2 ==================#
        self.frame2 = Frame(master)
        self.frame2.pack_forget()

        # --------- Layout ------------
        self.runwrap = Frame(self.frame2)
        self.runstats = LabelFrame(self.runwrap, text="Live stats")
        self.logs = LabelFrame(self.runwrap, text="Logs")
        self.controls = LabelFrame(self.runwrap, text="Controls")


        self.runwrap.pack(side=TOP, fill=X)
        self.runstats.pack(side=TOP, fill=X)
        self.logs.pack(side=TOP, fill=X)
        self.controls.pack(side=TOP, fill=X)

        # ---------- PLay stats ----------

        #variables
        play_variables = (
            "team1_contract_var",
            "team2_contract_var",
            "manager_contract_var",
            "gp_balance_var"
        )
        for variable in play_variables:
            setattr(self, variable, IntVar(value=pes_config['gui'][variable]))
            getattr(self, variable).trace_variable("w", self.save_configs)

        # not standard variables:
        self.current_team_var = IntVar(value=pes_config['gui']['current_team_var'])
        self.errors_var = IntVar(value=0)
        self.run_status = StringVar(value='Starting')
        self.run_status.trace_variable('w', self.run_status_changes)

        self.current_team_var.trace_variable("w", self.mark_team)

        self.label_games_stats = Label(self.runstats, text="Games played/planned")
        self.label_current_team = Label(self.runstats, text="Team playing now")
        self.label_manager_stat = Label(self.runstats, text="Manager contract left")
        self.label_error = Label(self.runstats, text="Errors occured")
        self.label_team_contract = Label(self.runstats, text="Teams contracts left")
        self.label_gp_balance = Label(self.runstats, text="GP balance")
        self.label_script_status = Label(self.runstats, textvar=self.run_status, foreground="light steel blue", font='bold')

        pl_stats_entry = dict(width=5, justify=RIGHT, state=DISABLED)
        self.games_played = Entry(self.runstats, **pl_stats_entry, textvariable=self.games_played_var)
        self.games_planned = Entry(self.runstats, **pl_stats_entry, textvariable=self.games_number)
        self.current_team1 = Label(self.runstats, font='bold', text='1', **pl_stats_entry, anchor=CENTER)
        self.current_team2 = Label(self.runstats, font='bold', text='2', **pl_stats_entry, anchor=CENTER)
        self.current_team = Entry(self.runstats, **pl_stats_entry, textvariable=self.current_team_var)
        self.manager_stats = Entry(self.runstats, **pl_stats_entry, textvariable=self.manager_contract_var)
        self.error = Entry(self.runstats, **pl_stats_entry, textvariable=self.errors_var)
        self.team1_contract = Entry(self.runstats, **pl_stats_entry, textvariable=self.team1_contract_var)
        self.team2_contract = Entry(self.runstats, **pl_stats_entry, textvariable=self.team2_contract_var)
        self.gp_balance = Entry(self.runstats, width=12, justify=RIGHT, state=DISABLED, textvariable=self.gp_balance_var)

        # Grid layout
        pl_stats_labels = dict(sticky=E, pady=2, padx=4)

        self.label_games_stats.grid(row=1, column=1, **pl_stats_labels)
        self.label_error.grid(row=2, column=1, **pl_stats_labels)
        self.label_current_team.grid(row=1, column=4, **pl_stats_labels)
        self.label_team_contract.grid(row=2, column=4, **pl_stats_labels)
        self.label_manager_stat.grid(row=1, column=7, **pl_stats_labels)
        self.label_gp_balance.grid(row=2, column=7, **pl_stats_labels)
        self.label_script_status.grid(row=1, rowspan=2, column=10)

        self.games_played.grid(row=1, column=2)
        self.games_planned.grid(row=1, column=3)
        self.error.grid(row=2, column=2, columnspan=2)
        self.current_team1.grid(row=1, column=5)
        self.current_team2.grid(row=1, column=6)
        self.team1_contract.grid(row=2, column=5)
        self.team2_contract.grid(row=2,column=6)
        self.manager_stats.grid(row=1, column=8)
        self.gp_balance.grid(row=2, column=8)


        # ----------- LOGS -------------
        self.logs = Text(self.logs, background="black", foreground='white', height=18)
        self.logs.insert(END,'''
 /$$                 /$$ /$$$$$$$  /$$$$$$$$  /$$$$$$ 
| $$                | $$| $$__  $$| $$_____/ /$$__  $$
| $$$$$$$   /$$$$$$ | $$| $$  \ $$| $$      | $$  \__/
| $$__  $$ /$$__  $$| $$| $$$$$$$/| $$$$$   |  $$$$$$ 
| $$  \ $$| $$$$$$$$| $$| $$____/ | $$__/    \____  $$
| $$  | $$| $$_____/| $$| $$      | $$       /$$  \ $$
| $$  | $$|  $$$$$$$| $$| $$      | $$$$$$$$|  $$$$$$/
|__/  |__/ \_______/|__/|__/      |________/ \______/ 
                                                      
\n''')
        self.logs.pack(fill=X, expand=1)

        #  actual logging section
        from main import logger as logger

        # Set format for logs
        formatter = logging.Formatter('[%(levelname)s:%(asctime)s:]: %(message)s', datefmt='%H:%M:%S')

        # Gui handler
        text_handler = self.TextHandler(self.logs)
        text_handler.setFormatter(formatter)
        text_handler.setLevel(logging.DEBUG)

        # Add handlers to logger
        logger.addHandler(text_handler)


        # ----------- Controls ----------
        self.abort = Button(self.controls, text="Abort", command=self.abort_pressed)
        self.gracefull_stop = Button(self.controls, text="Gracefull stop", command=self.do_gracefull_stop)
        self.poweroff = Checkbutton(self.controls, text="Poweroff after finish, delay m: ", variable=self.shutdown_var, command=self.use_shutdown)
        self.delay = Entry(self.controls, width=6, state=DISABLED, justify=RIGHT, textvariable=self.delay_var)
        self.countdown = Label(self.controls, text="Waiting.." )
        self.go_back = Button(self.controls, text="Go back", command=self.back, state=DISABLED)

        self.abort.grid(row=1, column=1)
        self.gracefull_stop.grid(row=1, column=2)
        self.poweroff.grid(row=1, column=3)
        self.delay.grid(row=1, column=4, sticky=E, pady=2, padx=4)
        self.countdown.grid(row=1, column=5, sticky=E, pady=2, padx=4)
        self.go_back.grid(row=1, column=6)


        #Refresh once loading
        self.use_azure()
        self.use_mail()
        self.use_shutdown()
        self.use_sign_all()
        self.use_convert_all()



        #================= END of the class ==================

    def test_azure(self):
        print("Azure test")

    def test_email(self):
        print("Email test")
        response = main.send_mail(
            sendgrid_api_key=pes_config['secrets']['sendgrid_api_key'],
            to_email=pes_config['general']['email_address'],
            alt_content="helPES test mail confirmation"
        )

        if response == 202:
            message = "202 Accepted \n Check your email to verify"
        else:
            message = "Could not send message, please check token, email address and sendgrid settings"
        messagebox.showinfo('Email test response', message=message)



    def test(self, *args):
        print('Abort pressed -> test result:')
        if self.current_team_var.get() == 1:
            self.current_team_var.set(2)
        else:
            self.current_team_var.set(1)

    def mark_team(self, *args):
        self.current_team1['state'] = '!disabled'
        self.current_team2['state'] = '!disabled'
        if self.current_team_var.get() < 2:
            self.current_team1.config(borderwidth=2, relief="groove")
            self.current_team2.config(borderwidth=0, relief="")
        else:
            self.current_team2.config(borderwidth=2, relief="groove")
            self.current_team1.config(borderwidth=0, relief="")
        self.current_team1['state'] = 'disabled'
        self.current_team2['state'] = 'disabled'
        self.save_configs()

    def start_toggle(self):
        # disable if mail wrong
        if self.mail_send_var.get() and '' in [self.sendgrid_api_key.get(), self.email_address.get()]:
            self.start_button['state'] = 'disabled'
        # disable if azure wrong
        elif self.azure_vm_var.get() and '' in [
            self.az_client_id.get(),
            self.az_secret.get(),
            self.az_tenant.get(),
            self.az_subscription_id.get(),
            self.az_group_name.get(),
            self.az_vm_name.get()
        ]:
            self.start_button['state'] = 'disabled'
        # disable if shutdown is wrong
        elif self.shutdown_var.get() and self.delay_var.get() < 1:
            self.start_button['state'] = 'disabled'
        else:
            self.start_button['state'] = '!disabled'

    def save_configs(self, *args):
        global pes_config
        for section in pes_config.keys():
            for key,value in pes_config[section].items():
                pes_config[section][key] = getattr(self, key).get()
        main.write_configurations()
        self.start_toggle()

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

    def tesseract_check(self):
        try:
            tess_version = main.pytesseract.get_tesseract_version()
            self.tesseract_version.config(foreground='green', text=tess_version)
            self.tesseract_label.config(foreground='green')
        except:
            self.tesseract_label.config(foreground='red')
            self.tesseract_version.config(foreground='red', text="Not installed or not in PATH")


    def print_message(self):
        print("Wow, this actually worked!")



    def toggle_mode(self):
        if self.which_mode.get() == 'custom':
            self.cont_s['state'] = "!disabled"
            self.to_play_val['state'] = "!disabled"
        else:
            self.games_number.set(1000)
            self.cont_s['state'] = "disabled"
            self.to_play_val['state'] = "disabled"

    def use_mail(self):
        if self.mail_send_var.get():
            self.sendgrid_token['state'] = '!disabled'
            self.email_addr['state'] = '!disabled'
            self.email_test['state'] = '!disabled'
        else:
            self.sendgrid_token['state'] = 'disabled'
            self.email_addr['state'] = 'disabled'
            self.email_test['state'] = 'disabled'


    def use_azure(self):
        fields_list = (
            'az_cl_id',
            'az_sec',
            'az_ten',
            'az_subs',
            'az_resource_name',
            'az_vm',
            'azure_test'
        )
        if self.azure_vm_var.get():
            for field in fields_list:
                getattr(self, field)['state'] = '!disabled'
        else:
            for field in fields_list:
                getattr(self, field)['state'] = 'disabled'

    def use_shutdown(self):
        if self.shutdown_var.get():
            self.delay['state'] = '!disabled'
            self.shutdown_delay['state'] = '!disabled'
            main.shutdown = True
            self.countdown.config(text='Waiting..')
        else:
            main.shutdown = False
            self.delay['state'] = 'disabled'
            self.shutdown_delay['state'] = 'disabled'
            self.countdown.config(text='Waiting..')

    def use_sign_all(self):
        if self.sign_all.get():
            self.sign_a_skip['state'] = '!disabled'
            self.save_configs()
        else:
            self.sign_a_skip['state'] = 'disabled'
            self.save_configs()

    def use_convert_all(self):
        if self.convert_all.get():
            self.t1_pop['state'] = 'disabled'
            self.t2_pop['state'] = 'disabled'
            self.t1_con['state'] = 'disabled'
            self.t2_con['state'] = 'disabled'
            messagebox.showinfo('helPES: Potential risk', message="""
Actions: 'convert all players' is selected
            
    This action will convert to EXP trainers all your players (of cost specified in Settings and below)
Please double check - go to your team, filter players by costs you've chose in "Settings" and make sure you don't need listed players
""")
        else:
            self.t1_pop['state'] = '!disabled'
            self.t2_pop['state'] = '!disabled'
            self.t1_con['state'] = '!disabled'
            self.t2_con['state'] = '!disabled'
        print('TODO')

    def select_path(self):
        self.filename = filedialog.askopenfilename(title="Choose your PES2020.exe file from installation folder", filetypes=[('PES2020.exe','PES2020.exe')])
        self.game_path.set(self.filename)
        if len(self.game_path.get()) > 3:
            self.path_found_label['text'] += 'Game path: detected'
            self.path_found_label['foreground'] = 'green'
            global pes_config
            pes_config['general']['game_path'] = self.game_path.get()
            self.save_configs()

    def new_window(self):
        self.window=Toplevel(gui)

    def start(self, perform=False):
        self.frame.pack_forget()
        self.frame2.pack(fill=BOTH, padx=4, pady=1)
        main.time.sleep(1)

        #Prepare threads
        if perform:
            self.script = threading.Thread(name='pes_run', target=self.perform_actions)
        else:
            self.script = threading.Thread(name='pes_run', target=self.play)

        self.status_watcher_job = threading.Thread(name='watcher', target=self.status_watcher)

        # Update status and buttons
        self.run_status.set('Starting')
        self.abort.config(state='normal')
        self.gracefull_stop.config(state='normal')
        self.go_back.config(state='disabled')
        # Run threads
        self.script.start()
        self.status_watcher_job.start()

        #self.play()

    def back(self):
        self.frame2.pack_forget()
        self.frame.pack(fill=BOTH, padx=4, pady=1)

    ###################### RUN GAME #######################
    def perform_actions(self):
        main.aborted = False
        main.gracefull_stop = False
        main.time.sleep(2)
        self.gui_actions_loop()

    def play(self):
        main.aborted = False
        main.gracefull_stop = False
        main.time.sleep(2)
        main.dummy_playing_loop()

    # --------- Playing loop -----------
    def gui_playing_loop(self):
        logging.info('helPES playing loop started')
        self.gui_start_pes()


    # --------- Actions playing loop -------
    def gui_actions_loop(self):
        logging.info('helPES actions loop started')
        self.gui_start_pes()
        if self.sign_all.get():
            main.sign_all(self.sign_skip.get())
        main.smart_players_convert(1, self.team1_populate.get(),self.team1_convert.get())
        main.smart_players_convert(2, self.team2_populate.get(), self.team2_convert.get())
        self.run_status.set('Done')
        if self.shutdown_var.get():
            self.do_shutdown()

    # --- Reusable ----

    def gui_start_pes(self):
        main.initialize_pes()
        if main.base_ok():
            logging.info('Game is on, no need to start')
        else:
            main.start_game()

    def gui_shift_change(self, team=12):
        main.sign_all()
        main.smart_players_convert(team)

    def home_stats_collect(self):
        main.initialize_pes()
        main.base_ok()
        print('MONEY')
        #GP
        self.gp_balance['state'] = '!disabled'
        self.gp_balance_var.set(int(float(main.recognize('money'))*1000))
        self.gp_balance['state'] = 'disabled'
        # EXP trainers
        self.exp['state'] ='!disabled'
        self.exp_left_var.set(int(main.recognize('exp_trainers')))
        self.exp['state'] = 'disabled'

    def initial_stats_collect(self):
        main.initialize_pes()
        main.base_ok()
        logging.info('Checking teams and manager contracts duration')
        formations = ''
        for i in range(2):
            main.base_ok()
            main.press_X()
            if formations == '':
                # Recognize and check formations
                message, first, second = '', True, True
                main.time.sleep(1) #Wait until team list opens
                if main.recognize('formation1') != '4-3-3':
                    message += "First team doesn't have 4-3-3 formation. "
                    first = False
                else:
                    formations = '4-3-3'
                if main.recognize('formation2') != '4-3-3':
                    message += "Second team doesn't have 4-3-3 formation. "
                    second = False
                else:
                    formations = '4-3-3'
                if not first and second:
                    message += "Please, select same coach with 4-3-3 for both teams and try again"
                    logging.error(f'{message}')
                    break
            if main.isok('img/squad-list.JPG', 60):
                main.turn_down(i+1)
                main.time.sleep(0.5)
                main.press_A()
            if main.base_ok():
                main.press_A()
                main.to_reserves()
                main.turn_up(1)
                if i+1 == 1:
                    self.team1_contract_var.set(int(main.recognize('contract_duration')))
                elif i+1 == 2:
                    self.team2_contract_var.set(int(main.recognize('contract_duration')))
                main.turn_up(2)
                main.turn_left(1)
                self.manager_contract_var.set(int(main.recognize('coach_contract')))
            while not main.base_ok():
                main.press_B()





    ####################### END RUN GAME #####################
    def abort_pressed(self):
        main.aborted = True
        self.run_status.set('Aborting')


    def status_watcher(self):
        watched_vars = {
            # variable in main, (runtime or single var, total or placeholder var)
            'game_number' : ('games_played_var', 'games_total_var'),
            'converted_nr' : ('players_runtime_var', 'players_total_var'),
            'error_count' : ('errors_var', '@'),
            'team_nr' : ('current_team_var', '@')
        }
        while self.script.is_alive() and self.run_status.get() not in ('Aborting', 'Stopping'):
            self.run_status.set('Script is running')
            main.time.sleep(2)
            print('status watcher is good')
            ## Here goes runtime variables updates
            for main_vars, gui_vars in watched_vars.items():
                if getattr(main, main_vars) != getattr(self, gui_vars[0]).get():
                    getattr(self, gui_vars[0]).set(getattr(main, main_vars))
                    if gui_vars[1] != '@':
                        getattr(self, gui_vars[1]).set( 1 + getattr(self, gui_vars[1]).get())

        else:
            print('status watcher else cond')
            self.abort.config(state='disabled')
            self.gracefull_stop.config(state='disabled')
            main.time.sleep(1)
            if self.run_status.get() in ('Aborting', "Stopping"):
                print('status watcher detected aborted')
                self.run_status.set('Aborted')
                self.go_back.config(state='normal')
            elif self.run_status.get() not in ('Done', 'Aborted', 'Aborting'):
                self.run_status.set('Failed')
                self.go_back.config(state='normal')
                print('status watcher detected failure')
                self.do_shutdown()
            else:
                self.go_back.config(state='normal')
            #TODO: find good place for that one.


    def run_status_changes(self, *args):
        status_color = {
            "Script is running" : 'green',
            'Aborting' : 'coral',
            'Stopping' : 'coral',
            'Aborted' : 'red',
            'Done' : 'blue',
            'Failed' : 'red',
            'Starting' : 'light steel blue'
        }

        status = self.run_status.get()
        for status_name,color in status_color.items():
            if status == status_name:
                self.label_script_status.config(foreground=color)

    def do_shutdown(self):
        sec_delay = int(self.delay_var.get() * 60)
        logging.info(f'Shutting down after {self.delay_var.get()} minutes')
        while self.shutdown_var.get():
            if sec_delay == 0:
                os.system('shutdown -s')
            else:
                mins, secs = divmod(sec_delay,60)
                hours, remain = divmod(mins, 60)
                timeformat = "{:02d}:{:02d}:{:02d}".format(hours, mins, secs)
                self.countdown.config(text=timeformat)
                sec_delay -= 1
                main.time.sleep(1)

    def do_gracefull_stop(self):
        main.gracefull_stop = True
        self.run_status.set('Stopping')



    #################### Logging class ######################
    class TextHandler(logging.Handler):
        """This class allows you to log to a Tkinter Text or ScrolledText widget"""

        def __init__(self, text):
            # run the regular Handler __init__
            logging.Handler.__init__(self)
            # Store a reference to the Text it will log to
            self.text = text

        def emit(self, record):
            msg = self.format(record)

            def append():
                self.text.configure(state='normal')
                self.text.insert(END, msg + '\n')
                self.text.configure(state='disabled')
                # Autoscroll to the bottom
                self.text.yview(END)

            # This is necessary because we can't modify the Text from other threads
            self.text.after(0, append)


gui = Tk(className=" PES2020 Farmer") #create instance
######################
gui.geometry("800x540")
p = PesGui(gui)
gui.mainloop() # Run it