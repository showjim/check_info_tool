class ParseTIM:

    def __init__(self):
        self.__timing_period = ''
        self.__clk_dic = {}

    def read_timing(self, timing_path:str, platform:str):
        if "UFLEX" in platform:
            with open(timing_path, 'r') as timing_file:
                for line_index, timing_line in enumerate(timing_file):
                    if line_index >= 7:
                        line_list = timing_line.split('\t')
                        if line_list[5] == 'clock':
                            self.__clk_dic[line_list[3]] = line_list[4].replace('=', '').upper()
                    if line_index == 7:
                        line_list = timing_line.split('\t')
                        period = line_list[2]
                        period = str(period).replace('=', '')
                        self.__timing_period = period.upper()
                    else:
                        pass
        elif "J750" in platform:
            with open(timing_path, 'r') as timing_file:
                for line_index, timing_line in enumerate(timing_file):
                    if line_index >= 6:
                        line_list = timing_line.split('\t')
                        if line_list[5] == 'mcg':
                            self.__clk_dic[line_list[4]] = self.__timing_period + "/" + line_list[4]
                    if line_index == 6:
                        line_list = timing_line.split('\t')
                        period = line_list[2]
                        period = str(period).replace('=', '')
                        self.__timing_period = period.upper()
                    else:
                        pass

    def get_timing_info(self):
        return self.__timing_period

    def get_clk_info(self):
        return self.__clk_dic
