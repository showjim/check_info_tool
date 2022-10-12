import re


def get_spec_info(line_list, key_list):
    dc_info = {}
    for line_index, key in enumerate(key_list):
        if line_index > 2:
            dc_info[key.upper()] = line_list[line_index].upper()
        else:
            pass
    return dc_info


class ParseSpec:

    def read_spec(self, spec_path):
        with open(spec_path, 'r') as spec_file:
            key_list = []
            for line_index, spec_line in enumerate(spec_file):
                line_list = spec_line.split('\t')
                if line_index == 0:
                    version_pattern = re.compile(r'version=(\S+?):')
                    self.__spec_version = re.search(version_pattern, spec_line).group(1)
                if line_index == 2:
                    for row_index, line_element in enumerate(line_list):
                        if line_element == '' and row_index != 0:
                            line_list[row_index] = line_list[row_index - 1]
                            key_list.append(line_list[row_index])
                        else:
                            key_list.append(line_element)
                elif line_index == 3:
                    for row_index, line_element in enumerate(line_list):
                        key_list[row_index] = key_list[row_index] + ' ' + line_element
                elif line_index > 3:
                    self.__spec_dict[line_list[1].upper()] = get_spec_info(line_list, key_list)
                else:
                    pass

    def get_info(self):
        return self.__spec_dict

    def get_spec_version(self):
        return self.__spec_version

    def __init__(self):
        self.__spec_dict = {}
        self.__spec_version = ''
