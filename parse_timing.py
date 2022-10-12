class ParseTIM:

    def __init__(self):
        self.__timing_period = ''

    def read_timing(self, timing_path):
        with open(timing_path, 'r') as timing_file:
            for line_index, timing_line in enumerate(timing_file):
                if line_index == 7:
                    line_list = timing_line.split('\t')
                    period = line_list[2]
                    period = str(period).replace('=', '')
                    self.__timing_period = period.upper()
                else:
                    pass

    def get_timing_info(self):
        return self.__timing_period
