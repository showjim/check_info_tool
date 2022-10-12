import collections


def get_job_list_content(line_list):
    job_list_info = {'TestInstanceList': line_list[3].split(','), 'DC Spec': line_list[6], 'AC Spec': line_list[5],
                     'PatternSet': line_list[7]}
    return job_list_info


class ParseJobList:

    def read_job_list(self, job_list_path):
        with open(job_list_path, 'r') as job_list_file:
            for line_index, job_line in enumerate(job_list_file):
                if line_index > 3:
                    line_list = job_line.split('\t')
                    flow_table_file = line_list[4]
                    if flow_table_file != '':
                        self.__job_list_dict[flow_table_file] = get_job_list_content(line_list)
                    else:
                        pass
                else:
                    pass

    def get_test_job_list_info(self):
        return self.__job_list_dict

    def __init__(self):
        self.__job_list_dict = collections.OrderedDict()
