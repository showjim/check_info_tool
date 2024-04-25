class ParseTIM:

    def __init__(self):
        self.__timing_period = {}
        self.__clk_dic = {}

    def read_timing(self, timing_path:str, platform:str):
        with open(timing_path, 'r') as timing_file:
            for line_index, timing_line in enumerate(timing_file):
                if (line_index >= 7 and len(timing_line.strip()) == 0) or timing_line == "\n":
                    break
                line_list = timing_line.split('\t')
                if "UltraFLEX" in platform:
                    if line_index >= 7:
                        tmp_tset = line_list[1].upper()
                        if tmp_tset not in self.__clk_dic.keys():
                            self.__clk_dic[tmp_tset] = {}
                        period = line_list[2]
                        period = str(period).replace('=', '')
                        if tmp_tset not in self.__timing_period.keys():
                            self.__timing_period[tmp_tset] = period.upper()
                        if line_list[5] == 'clock':
                            self.__clk_dic[tmp_tset][line_list[3]] = line_list[4].replace('=', '').upper()
                    else:
                        pass
                elif "J750" in platform:
                    if line_index >= 6:
                        tmp_tset = line_list[1].upper()
                        if tmp_tset not in self.__clk_dic.keys():
                            self.__clk_dic[tmp_tset] = {}
                        period = line_list[2]
                        period = str(period).replace('=', '')
                        if tmp_tset not in self.__timing_period.keys():
                            self.__timing_period[tmp_tset] = period.upper()
                        if line_list[5] == 'mcg':
                            self.__clk_dic[tmp_tset][line_list[4]] = period.upper() + "/" + line_list[4]
                    else:
                        pass


    def get_timing_info(self):
        return self.__timing_period

    def get_clk_info(self):
        return self.__clk_dic
