import tkinter as tk
import tkinter.font as tf
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
import threading

_VERSION = "Beta 1.5.7"


class Application(tk.Tk):

    def __init__(self, check_info_instance):
        super().__init__()
        self.createWidgets()
        self.flow_table_set = set()
        self.check_info = check_info_instance
        self.sub_root_flag = False

    def createWidgets(self):
        self.title('Check Info Tool ' + _VERSION)
        self.rowconfigure(0, weight=0, minsize=30)
        self.rowconfigure(1, weight=1, minsize=50)
        self.columnconfigure(0, weight=1, minsize=50)
        self.columnconfigure(1, weight=0)
        self.entry_var = tk.StringVar()
        self.power_var = tk.StringVar()
        self.pattern_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.key_var.set('UltraFLEX Plus')
        items = ['UltraFLEX Plus', 'UltraFLEX', 'J750']
        self.cycle_format_var = tk.StringVar()

        top_frame = tk.Frame(self, borderwidth=1)  # , height=80)
        content_frame = tk.Frame(self, borderwidth=1)

        top_frame.rowconfigure(0, weight=0)
        top_frame.columnconfigure(0, weight=0)
        content_frame.rowconfigure(0, weight=1)
        content_frame.columnconfigure(0, weight=1)

        # top_frame.pack(side=tk.TOP)
        top_frame.grid(row=0, column=0, sticky=tk.W + tk.S + tk.E + tk.N)
        # content_frame.pack(side=tk.TOP)
        content_frame.grid(row=1, column=0, sticky=tk.W + tk.S + tk.E + tk.N)

        label = tk.Label(top_frame, text='Test Program:')
        entry = tk.Entry(top_frame, textvariable=self.entry_var, width=40)
        self.load_button = tk.Button(top_frame, command=self.import_flow, text='Load', width=8)
        self.run_button = tk.Button(top_frame, command=lambda: self.thread_it(self.run), text='Run')  # , width=8
        combobox = ttk.Combobox(top_frame, values=items, textvariable=self.key_var, width=12)
        sep_label = tk.Label(top_frame, text='Report Config:')
        sep = ttk.Separator(top_frame, orient="horizontal")
        check_box_Label = ttk.Label(top_frame, text='Cycle Mode:')
        check_box1 = ttk.Radiobutton(top_frame, text=u'Period', variable=self.cycle_format_var, value='Period')
        check_box2 = ttk.Radiobutton(top_frame, text=u'Frequency', variable=self.cycle_format_var, value='Frequency')
        self.cycle_format_var.set('Period')
        self.progressbarOne = ttk.Progressbar(top_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')  # length=180, style='grey.Horizontal.TProgressbar')

        label.grid(row=0, column=0, padx=5, pady=5)
        entry.grid(row=0, column=1, padx=5, pady=5)
        combobox.grid(row=0, column=2, padx=5, pady=5)
        self.load_button.grid(row=0, column=3, padx=5, pady=5)
        self.run_button.grid(row=0, column=4, padx=5, pady=5)
        sep.grid(row=1, column=0, rowspan=1, columnspan=5, sticky='EW', padx=5, pady=5)
        sep_label.grid(row=2, column=0, sticky='E', padx=5, pady=5)
        check_box_Label.grid(row=2, column=1, sticky='E')
        check_box1.grid(row=2, column=2)  # , sticky='W')
        check_box2.grid(row=2, column=3)  # , sticky='E')
        self.progressbarOne.grid(row=3, column=0, columnspan=5, sticky='EW', padx=5, pady=5)

        right_bar = tk.Scrollbar(content_frame, orient=tk.VERTICAL)
        bottom_bar = tk.Scrollbar(content_frame, orient=tk.HORIZONTAL)
        self.textbox = tk.Text(content_frame, yscrollcommand=right_bar.set, xscrollcommand=bottom_bar.set)
        self.textbox.config()
        # self.textbox.pack(side=tk.LEFT, fill=tk.BOTH)
        self.textbox.grid(row=0, column=0, sticky=tk.W + tk.S + tk.E + tk.N)
        # right_bar.pack(side=tk.RIGHT, fill=tk.Y)
        right_bar.grid(row=0, column=1, sticky=tk.S + tk.N)
        # bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        bottom_bar.grid(row=1, column=0, sticky=tk.W + tk.E)
        right_bar.config(command=self.textbox.yview)
        bottom_bar.config(command=self.textbox.xview)

    def cancel(self, sub_root):
        self.flow_table_set = set()
        self.put_data_log('None of the flows Were Chosen')
        sub_root.withdraw()
        self.sub_root_flag = False

    def select(self, sub_root):
        if self.flow_table_set:
            for flow_table in self.flow_table_set:
                self.put_data_log(flow_table + ' Has Loaded!')
        else:
            self.put_data_log('None of the flows Were Chosen')
        sub_root.withdraw()
        self.sub_root_flag = False

    def run(self):
        self.switchButtonState(self.load_button)
        self.switchButtonState(self.run_button)
        self.check_info.run(self.flow_table_set)
        self.switchButtonState(self.load_button)
        self.switchButtonState(self.run_button)

    def get_flow_selected(self):
        return self.flow_table_set

    def put_data_log(self, data_log):
        self.textbox.insert(tk.END, data_log + '\n')
        self.textbox.see(tk.END)
        self.textbox.update()

    def select_flow_table(self, choose_flag_dict):
        for flow_name, choose_flag in choose_flag_dict.items():
            if choose_flag.get() == 1:
                self.flow_table_set.add(flow_name)
            else:
                if flow_name in self.flow_table_set:
                    self.flow_table_set.remove(flow_name)
                else:
                    pass

    def import_flow(self):
        if not self.sub_root_flag:
            self.sub_root_flag = True
            self.put_data_log('===============================START===============================')

            def send_log(data_log):
                self.textbox.insert(tk.END, data_log + '\n')
                self.textbox.see(tk.END)
                self.textbox.update()
            def update_processbar(val):
                self.progressbarOne['value'] = val
                self.progressbarOne.update_idletasks()
            self.check_info.read_device(self.entry_var.get(), self.power_var.get(), self.pattern_var.get(),
                                        self.key_var.get(), send_log, self.cycle_format_var.get(), update_processbar)
            job_list_dict = self.check_info.get_job_list()
            sub_root = tk.Tk()
            sub_root.title('Select Flow Table')
            sub_frame = tk.Frame(sub_root)
            if job_list_dict:
                job_index = 1
                choose_flag_dict = {}
                self.flow_table_set = set()
                for flow_table_name in job_list_dict.keys():
                    choose_flag_dict[flow_table_name] = tk.IntVar(sub_root)
                    check_button = tk.Checkbutton(sub_frame, text=flow_table_name, anchor='w',
                                                  command=lambda: self.select_flow_table(choose_flag_dict),
                                                  variable=choose_flag_dict[flow_table_name])
                    check_button.grid(row=job_index, column=0, sticky=tk.W, columnspan=2)
                    job_index = job_index + 1
                select_button = tk.Button(sub_frame, text='Select', command=lambda: self.select(sub_root))
                select_button.grid(row=job_index, column=0, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)
                exit_button = tk.Button(sub_frame, text='Cancel', command=lambda: self.cancel(sub_root))
                exit_button.grid(row=job_index, column=1, sticky=tk.E + tk.S + tk.W + tk.N, padx=5, pady=5)
                sub_frame.grid(row=0, column=0, sticky=tk.N)
            else:
                self.put_data_log('Cannot Read Job List File, Please Check!')
        else:
            messagebox.showinfo('Warning', 'Sub Interface has been Generated')

    def add_menu(self, menu):
        menu(self)

    def thread_it(self, func, *args):
        """ 将函数打包进线程 """
        self.myThread = threading.Thread(target=func, args=args)
        self.myThread.daemon = True  # 主线程退出就直接让子线程跟随退出,不论是否运行完成。
        self.myThread.start()

    def switchButtonState(self, button):
        if (button['state'] == tk.NORMAL):
            button['state'] = tk.DISABLED
        else:
            button['state'] = tk.NORMAL


class Menu:

    def __init__(self, root):
        self.menu_bar = tk.Menu(root)
        self.power_order_path = root.power_var
        self.device_path = root.entry_var
        self.pattern_path = root.pattern_var
        ft = tf.Font(family='微软雅黑', size=10)
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Import Program File(.igxl)", command=self.file_open)
        file_menu.add_command(label="Import Program Directory", command=self.directory_open)
        file_menu.add_command(label="Import Pattern Directory(optional)", command=self.pattern_open)
        file_menu.add_command(label="Set Power Order(optional)", command=self.set_power_order)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=root.quit)

        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about)
        help_menu.add_command(label="User Guide", command=self.user_guide)

        self.menu_bar.add_cascade(label="File", menu=file_menu)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

        root.config(menu=self.menu_bar)
        self.put_data_log = root.put_data_log

    def file_open(self):
        target_file = filedialog.askopenfilename()
        self.device_path.set('')
        self.device_path.set(target_file)
        self.put_data_log('Info: Get IG-XL Path: ' + target_file)

    def directory_open(self):
        target_file = filedialog.askdirectory()
        self.device_path.set('')
        self.device_path.set(target_file)
        self.put_data_log('Info: Get IG-XL ASCII Dir Path: ' + target_file)

    def pattern_open(self):
        target_file = filedialog.askdirectory()
        self.pattern_path.set('')
        self.pattern_path.set(target_file)
        self.put_data_log('Info: Get Pattern Dir Path: ' + target_file)

    def set_power_order(self):
        target_file = filedialog.askopenfilename()
        self.power_order_path.set('')
        self.power_order_path.set(target_file)

    def user_guide(self):
        messagebox.showinfo('--', 'Please Wait')

    def about(self):
        messagebox.showinfo('About', 'Thank you for using!\nCreated by Ivan Ding, maintained by Chao Zhou.'
                                     '\nAny suggestions please mail zhouchao486@gmail.com')
