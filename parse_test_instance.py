import re


class ParseTestInstance:

    def read_test_instance(self, test_instance_path):
        with open(test_instance_path, 'r') as test_instance_file:
            pat_pattern = re.compile(r'\S+_burst\S*', re.IGNORECASE)
            for line_index, test_instance_line in enumerate(test_instance_file):
                if line_index > 3:
                    line_list = test_instance_line.split('\t')
                    if line_list[1] == '':
                        break
                    else:
                        pattern_info_list = re.findall(pat_pattern, test_instance_line)
                        pattern_info = ''
                        if pattern_info_list:
                            pattern_info = ','.join(pattern_info_list)
                        self.__test_instance_dict[line_list[1].upper()] = self.__get_instance_content(line_list,
                                                                                                      pattern_info.upper())
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
