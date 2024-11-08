import os, re
from subprocess import run
from typing import List


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
                            # main_pattern_name = main_pattern_name_group.group(1)
                            main_pattern_name = main_pattern_name # add this to ignore "_X\d_" regexp search
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
                exract_file_path = pattern_folder_path + "/pattern_tset.txt"
                run('patinfo ' + '"' + pattern_path + '"' + ' -tset > "' + exract_file_path + '"', shell=True)
                # parse pattern_tset.txt

                tset_pattern = re.compile("\t(\S+) {1,2}\d\n") #("Tset Name Table:\s+----------------(\s+(\S+))+")
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

    # def get_pattern_set_info(self):
    #     result_dict = {}
    #     result_dict = copy.deepcopy(self.__pattern_set_dict)
    #     for patset, pat_list in self.__pattern_set_dict.items():
    #         for i, pat in enumerate(pat_list):
    #             if (not pat.upper().endswith("PATX")) and (not pat.upper().endswith("PAT")):
    #                 if pat.upper() in result_dict.keys():
    #                     result_dict[patset][i] = result_dict[pat.upper()]
    #                 else:
    #                     print("Error: Patset found item without pattern definition: " + pat)
    #     return result_dict #self.__pattern_set_dict

    # def get_pat_path(self, pat_path:str):
    #     result = ""
    #     upper_pat_path = pat_path.upper()
    #     if not (upper_pat_path.endswith("PATX") or upper_pat_path.endswith("PAT") or
    #             upper_pat_path.endswith("PATX.GZ") or upper_pat_path.endswith("PAT.GZ")):
    #         if upper_pat_path in self.__pattern_set_dict:
    #             new_pat_path = self.__pattern_set_dict[upper_pat_path]
    #             result = self.get_pat_path(new_pat_path)
    #         else:
    #             result = "No Path Definition Found!"
    #             raise ValueError(f"Error: Patset found item without pattern definition: {pat_path}")
    #     else:
    #         result = pat_path
    #     return result

    def contains_any_substring(self, s, substrings):
        return any(sub in s for sub in substrings)

    def truncate_after_substring(self, s, substrings):
        # 转换为小写以忽略大小写
        lower_s = s.lower()

        # 查找每个子字符串的位置，并找到第一个匹配的位置
        first_occurrence = len(s)  # 初始化为字符串的长度，如果没有找到匹配，则返回整个字符串
        for sub in substrings:
            pos = lower_s.find(sub.lower())
            if pos != -1 and pos < first_occurrence - len(sub):
                first_occurrence = pos + len(sub)
                break

        # 如果找到子字符串，则截断
        return s[:first_occurrence] if first_occurrence != len(s) else s

    def get_pat_path(self, pat_path: str) -> List[str]:
        """
        Resolve the given pattern file path to a defined path or raise an error if undefined.

        Args:
        pat_path (str): The pattern file path to resolve.

        Returns:
        str: The resolved pattern file path.

        Raises:
        ValueError: If no path definition is found for the given pattern file path.
        """
        # Convert path to uppercase to standardize comparison
        upper_pat_path = pat_path.upper()

        # Define valid file extensions
        valid_extensions = (".PATX.GZ", ".PAT.GZ", ".PATX", ".PAT")
        # # 示例字符串
        # test_strings = ["example.PAT", "filename.PATX.GZ", "data.txt", "archive.PAT.GZ", "some.PATX:module-name"]

        # Check if path ends with a valid extension
        if upper_pat_path.endswith(valid_extensions):
            return [pat_path]

        # check if path contain a valid extension
        if self.contains_any_substring(upper_pat_path, valid_extensions):
            new_pat_path = self.truncate_after_substring(pat_path, valid_extensions)
            return [new_pat_path]

        # Resolve path using a dictionary if not ending with a valid extension
        if upper_pat_path in self.__pattern_set_dict:
            result = []
            new_pat_path_list = self.__pattern_set_dict[upper_pat_path]
            for pat in new_pat_path_list:
                result += self.get_pat_path(pat)
            return result

        # Raise an error if no valid path is found
        raise ValueError(f"Error: Patset found item without pattern definition: {pat_path}")

    def get_pattern_set_info(self):
        result_dict = {}
        for patset, pat_list in self.__pattern_set_dict.items():
            pat_content_list = []
            for pat in pat_list:
                pat_content_list += self.get_pat_path(pat)
            result_dict[patset] = pat_content_list

                # upper_pat = pat.upper()
                # if not (upper_pat.endswith("PATX") or upper_pat.endswith("PAT")):
                #     if upper_pat in self.__pattern_set_dict:
                #         result_dict[patset].append(self.__pattern_set_dict[upper_pat])
                #     else:
                #         # 这里可以抛出异常或者记录日志
                #         raise ValueError(f"Error: Patset '{patset}' found item without pattern definition: {pat}")
                # else:
                #     result_dict[patset].append(pat)  # 保持原始值
        return result_dict

    def get_pattern_tset(self):
        return self.__tset_name

