import re

class ParseGlobalSpec():

    def read_spec(self, spec_path):
        with open(spec_path, 'r') as spec_file:
            self.__spec_dict = {}
            for line_index, spec_line in enumerate(spec_file):
                line_list = spec_line.split('\t')
                if line_index == 0:
                    version_pattern = re.compile(r'version=(\S+?):')
                    self.__spec_version = re.search(version_pattern, spec_line).group(1)
                elif line_index > 3:
                    self.__spec_dict[line_list[1].upper()] = line_list[3].upper()
                else:
                    pass

    def get_info(self):
        return self.__spec_dict