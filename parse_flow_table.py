import os
import os.path


def get_flow_content(line_list, platform):
    if "UltraFLEX" in platform:
        flow_info = {'Opcode':line_list[6], 'Parameter':line_list[7].upper(), 'TestNumber':line_list[9],
                     'HardBin':line_list[16], 'SoftBin':line_list[18]}
    else: #J750
        flow_info = {'Opcode': line_list[6], 'Parameter': line_list[7].upper(), 'TestNumber': line_list[9],
                     'HardBin': line_list[11], 'SoftBin': line_list[13]}
    return flow_info


class ParseFlowTable:

    def read_flow_table(self, flow_path:str, platform:str):

        with open(flow_path, 'r') as flow_file:
            lines = flow_file.readlines()
            for line_index in range(len(lines)):
                flow_table_line = lines[line_index]
            #for line_index, flow_table_line in enumerate(flow_file):
                if line_index > 3:
                    line_list = flow_table_line.split('\t')
                    if line_list[6] == '':
                        break
                    elif (line_list[6] == 'Test' or line_list[6] == "Test-defer-limits") and line_list[5] == '':
                        tmp_dict = get_flow_content(line_list, platform)
                        if tmp_dict["HardBin"] == "" or tmp_dict["SoftBin"] == "":
                            line_list = lines[line_index+1].split('\t')
                            tmp_next_line_dict = get_flow_content(line_list, platform)
                            if tmp_next_line_dict["Opcode"] == 'Use-Limit' and tmp_next_line_dict["HardBin"] != "" and tmp_next_line_dict["SoftBin"] != "":
                                tmp_dict["HardBin"] = tmp_next_line_dict["HardBin"]
                                tmp_dict["SoftBin"] = tmp_next_line_dict["SoftBin"]
                                tmp_dict["TestNumber"] = tmp_next_line_dict["TestNumber"]
                            else:
                                print("No SortBin test found: " + flow_table_line)
                        self.__test_suite_list.append(tmp_dict)
                    elif line_list[6] == 'call' and line_list[5] == '':
                        filepath, filename = os.path.split(flow_path)
                        sub_flow_path = filepath + '/' + line_list[7] + '.txt'
                        tmp = self.read_flow_table(sub_flow_path, platform)
                        if tmp != None:
                            self.__test_suite_list.append(tmp)
                    else:
                        pass
                else:
                    pass

    def get_test_suite_info(self):
        return self.__test_suite_list

    def __init__(self):
        self.__test_suite_list = []

