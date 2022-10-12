import tkinter as tk
import tkinter.font as tf
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox


class Application(tk.Tk):

    def __init__(self, check_info_instance):
        super().__init__()
        self.createWidgets()
        self.flow_table_set = set()
        self.check_info = check_info_instance
        self.sub_root_flag = False

    def createWidgets(self):
        self.title('Check Info V2.00')
        self.columnconfigure(0, minsize=50)
        self.entry_var = tk.StringVar()
        self.power_var = tk.StringVar()
        self.pattern_var = tk.StringVar()
        self.key_var = tk.StringVar()
        self.key_var.set('Ultra Flex')
        items = ['Ultra Flex']

        top_frame = tk.Frame(self, height=80)
        content_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP)
        content_frame.pack(side=tk.TOP)

        label = tk.Label(top_frame, text='Test Program:')
        entry = tk.Entry(top_frame, width=40, textvariable=self.entry_var)
        load_button = tk.Button(top_frame, width=8, command=self.import_flow, text='Load')
        run_button = tk.Button(top_frame, width=8, command=self.run, text='Run')
        combobox = ttk.Combobox(top_frame, width=10, values=items, textvariable=self.key_var)
        label.grid(row=0, column=0, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)
        entry.grid(row=0, column=1, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)
        combobox.grid(row=0, column=2, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)
        load_button.grid(row=0, column=3, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)
        run_button.grid(row=0, column=4, sticky=tk.W + tk.S + tk.E + tk.N, padx=5, pady=5)

        right_bar = tk.Scrollbar(content_frame, orient=tk.VERTICAL)
        bottom_bar = tk.Scrollbar(content_frame, orient=tk.HORIZONTAL)
        self.textbox = tk.Text(content_frame, yscrollcommand=right_bar.set, xscrollcommand=bottom_bar.set)
        right_bar.pack(side=tk.RIGHT, fill=tk.Y)
        bottom_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.textbox.pack(side=tk.LEFT, fill=tk.BOTH)
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
        self.check_info.run(self.flow_table_set)

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
            self.check_info.read_device(self.entry_var.get(), self.power_var.get(), self.pattern_var.get(), self.textbox)
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

    def file_open(self):
        target_file = filedialog.askopenfilename()
        self.device_path.set('')
        self.device_path.set(target_file)

    def directory_open(self):
        target_file = filedialog.askdirectory()
        self.device_path.set('')
        self.device_path.set(target_file)

    def pattern_open(self):
        target_file = filedialog.askdirectory()
        self.pattern_path.set('')
        self.pattern_path.set(target_file)

    def set_power_order(self):
        target_file = filedialog.askopenfilename()
        self.power_order_path.set('')
        self.power_order_path.set(target_file)

    def user_guide(self):
        messagebox.showinfo('--', 'Please Wait')

    def about(self):
        messagebox.showinfo('About', 'Thank you for using!\nAny suggestions please mail ivan.ding@teradyne-china.com')
