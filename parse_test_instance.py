import os, re


class ParseTestInstance:

    def find_pat_path(self, pat_pattern, test_instance_line, line_list):
        pattern_info_list = re.findall(pat_pattern, test_instance_line)
        pattern_info = ''
        if pattern_info_list:
            pattern_info = ','.join(pattern_info_list)
        self.__test_instance_dict[line_list[1].upper()].append(self.__get_instance_content(line_list, pattern_info))


    def read_test_instance(self, test_instance_path:str, pattern_set_dict, platform:str='UltraFLEX Plus'):
        if os.path.isfile(test_instance_path) == False:
            test_instance_path = test_instance_path.replace('%20',' ')
        if platform == 'UltraFLEX Plus':
            pat_pattern = re.compile(r'\t([\S ]+\.patx)', re.IGNORECASE)
        else:
            pat_pattern = re.compile(r'\t([\S ]+\.pat)', re.IGNORECASE)
        with open(test_instance_path, 'r') as test_instance_file:
            if len(pattern_set_dict) == 0:
                for line_index, test_instance_line in enumerate(test_instance_file):
                    if line_index > 3:
                        line_list = test_instance_line.split('\t')
                        if line_list[1] == '':
                            break
                        else:
                            if "UltraFLEX" in platform:
                                test_instance_line = "\t".join(line_list[:144])
                            else:
                                test_instance_line = "\t".join(line_list[:93])
                            self.find_pat_path(pat_pattern, test_instance_line, line_list)
                    else:
                        pass
            else:
                for line_index, test_instance_line in enumerate(test_instance_file):
                    if line_index > 3:
                        line_list = test_instance_line.split('\t')
                        if line_list[1] == '':
                            break
                        else:
                            pattern_info = ''
                            hit_cnt = 0
                            inst_name = line_list[1].upper()
                            # Incase one instance wih multiple test conditions/parameters
                            if inst_name not in self.__test_instance_dict.keys():
                                self.__test_instance_dict[inst_name] = []
                            for i in range(14, 20):
                                if line_list[i].upper() in pattern_set_dict.keys():
                                    # pattern_info = line_list[i]
                                    if hit_cnt == 0:
                                        pattern_info = ','.join(pattern_set_dict[line_list[i].upper()])
                                    else:
                                        pattern_info = pattern_info + ',' + ','.join(pattern_set_dict[line_list[i].upper()])
                                    hit_cnt += 1
                            if pattern_info != "":
                                self.__test_instance_dict[inst_name].append(self.__get_instance_content(line_list, pattern_info))
                            else:
                                self.find_pat_path(pat_pattern, test_instance_line, line_list)
                    else:
                        pass

    def __get_instance_content(self, line_list, pattern_info):
        instance_info = {'DC Category': line_list[5], 'DC Selector': line_list[6], 'TimeSet': line_list[9],
                         'AC Category': line_list[7], 'AC Selector': line_list[8], 'PinLevel': line_list[11], 'Pattern': pattern_info}
        return instance_info

    def get_instance_info(self):
        return self.__test_instance_dict

    def __init__(self):
        self.__test_instance_dict = {}
