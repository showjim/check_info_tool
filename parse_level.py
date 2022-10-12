import re
import collections


class ParsePinLevel:

    def read_pin_level(self, pin_level_path):
        with open(pin_level_path, 'r') as pin_level_file:
            for line_index, level_line in enumerate(pin_level_file):
                if line_index > 2:
                    line_list = level_line.split('\t')
                    if line_list[1] == '':
                        break
                    elif line_list[3] == 'VMain' or line_list[3] == 'Vps':
                        pin_value = re.search(re.compile(r'=?(\S+)'), line_list[4]).group(1)
                        self.__pin_level_dict[line_list[1].upper()] = pin_value.upper()
                    else:
                        pass
                else:
                    pass

    def get_pin_level_info(self):
        return self.__pin_level_dict

    def __init__(self):
        self.__pin_level_dict = collections.OrderedDict()
