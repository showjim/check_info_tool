import os, re
from subprocess import run


class ParsePatternSet:
    def __init__(self):
        self.__tset_name = [] # ""
        self.__pattern_set_dict = {}
        self.__cycle_dict = {}
        self.__pattern_set_version = None

    def read_pattern_set(self, pattern_set_path:str, pattern_file_path:str, platform:str="UltraFLEX Plus"):
        pattern = re.compile(r'(\S+)_X\d_\S+', re.IGNORECASE)
        if os.path.isfile(pattern_set_path) == False:
            pattern_set_path = pattern_set_path.replace('%20',' ')
        with open(pattern_set_path, 'r') as pattern_set_file:
            main_pattern_list = []
            last_pattern_set_name = ''
            for line_index, pattern_line in enumerate(pattern_set_file):
                if line_index > 2:
                    line_list = pattern_line.split('\t')
                    if len(line_list) == 0 or line_list[1] == '':
                        break
                    else:
                        pattern_set_name = line_list[1]
                        if pattern_set_name != last_pattern_set_name:
                            main_pattern_list = []
                            self.__cycle_dict[pattern_set_name.upper()] = 0
                            last_pattern_set_name = pattern_set_name
                        else:
                            pass
                        if self.__pattern_set_version == '2.3':
                            main_pattern_index = 4
                        elif self.__pattern_set_version == '1.1':
                            main_pattern_index = 2
                        else:
                            main_pattern_index = 5
                        # main_pattern_index = 4 if self.__pattern_set_version == '2.3' else 5
                        main_pattern_name = line_list[main_pattern_index] #.split('\\')[-1]
                        main_pattern_name_group = re.search(pattern, main_pattern_name)
                        if main_pattern_name_group is not None:
                            main_pattern_name = main_pattern_name_group.group(1)
                            if pattern_file_path != '':
                                if False:
                                    path_list_pre = re.split(r'[/\\]', pattern_file_path)
                                    path_list_post = re.split(r'[/\\]', line_list[main_pattern_index])
                                    path_list = path_list_pre[:-1] + path_list_post[1:]
                                    pattern_path = '/'.join(path_list)
                                    run('patinfo ' + pattern_path + ' -ucodes -1 -1 >pattern.txt', shell=True)
                                    # os.system('"patinfo ' + pattern_path + '" -ucodes -1 -1 >pattern.txt')
                                    self.read_pattern_file('pattern.txt', pattern_set_name)
                            else:
                                pass
                        else:
                            main_pattern_name = main_pattern_name #.split('.')[0]
                        main_pattern_list.append(main_pattern_name)
                        self.__pattern_set_dict[pattern_set_name.upper()] = main_pattern_list
                elif line_index == 0:
                    if "UltraFLEX" in platform:
                        version_pattern = re.compile(r'version=(\S+?):')
                    else:
                        version_pattern = re.compile(r'DFF (\d+(\.\d+)?)')
                    self.__pattern_set_version = re.search(version_pattern, pattern_line).group(1)
                else:
                    pass

    def read_pattern_file(self, pattern_file_path, pattern_set_name):
        vector_count_pattern = re.compile(r'Number\sof\spattern\svectors:\s(\d+)')
        cycle_count_pattern = re.compile(r'repeat\s=\s(\d+)')
        with open(pattern_file_path, 'r') as pattern_file:
            value = 0
            vector_number = '0'
            for pattern_line in pattern_file:
                vector_number_search = re.search(vector_count_pattern, pattern_line)
                if vector_number_search is not None:
                    vector_number = vector_number_search.group(1)
                # if ''
                if re.match(r'\d', pattern_line):
                    repeat = re.search(cycle_count_pattern, pattern_line).group(1)
                    cycle_list = re.split(r'\s+', pattern_line)
                    cycle_count = cycle_list[1]
                    if cycle_count[:6] == '0x0000' or cycle_count[:4] == '0000':
                        pass
                    else:
                        cycle_count = '0'
                    value = value + int(repeat) * int(cycle_count, 16)
            cycle_number = value + int(vector_number)
            self.__cycle_dict[pattern_set_name.upper()] = cycle_number + self.__cycle_dict[pattern_set_name.upper()]

    def read_tset_from_pattern(self, pattern_folder_path: str, pattern_file_path: str):
        if pattern_folder_path != '':
            path_pre = re.split(r'[/\\]', pattern_folder_path)
            path_post = re.split(r'[/\\]', pattern_file_path)
            path_full = path_pre[:-1] + path_post[1:]
            pattern_path = '/'.join(path_full)
            if os.path.exists(pattern_path):
                run('patinfo ' + '"' + pattern_path + '"' + ' -tset > pattern_tset.txt', shell=True)
                # parse pattern_tset.txt
                exract_file_path = "pattern_tset.txt"
                tset_pattern = re.compile("\t(\S+)  \d\n") #("Tset Name Table:\s+----------------(\s+(\S+))+")
                # Using readlines()
                buffer = open(exract_file_path, 'r')
                Lines = buffer.readlines()
                line = "".join(Lines)
                tset_search = re.findall(tset_pattern, line)
                if tset_search is not None:
                    tset_name = tset_search
                    self.__tset_name = tset_name
                    #print(tset_name)
            else:
                self.__tset_name = ["Error: pattern file does not exist"]

    def get_pattern_cycle_info(self):
        return self.__cycle_dict

    def get_pattern_set_info(self):
        return self.__pattern_set_dict

    def get_pattern_tset(self):
        return self.__tset_name

