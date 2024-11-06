from src.parse_flow_table import ParseFlowTable
from src.parse_dc_spec import ParseDCSpec
from src.parse_ac_spec import ParseACSpec
from src.parse_glob_spec import ParseGlobalSpec
from src.parse_level import ParsePinLevel
from src.parse_timing import ParseTIM
from src.parse_job_list import ParseJobList
from src.parse_pattern_set import ParsePatternSet
from src.parse_test_instance import ParseTestInstance
from src.common import unzip, format_str, export_sheets_to_txt
import collections
import os
import re
import datetime
import xlrd
import traceback
import xlsxwriter
from itertools import chain


class LastFlowInfo:
    dc_spec_name = None
    glob_spec_name = None
    ac_spec_name = None
    pattern_set_name = None


class CheckInfo:
    def __init__(self, temp_directory):
        self.power_order_path = ''
        self.pattern_path = ''
        self.job_list_dict = ''
        self.flow_table_set = set()
        self.device_directory = temp_directory
        self.work_sheet = None
        self.text = None
        self.last_flow_info = LastFlowInfo()
        self.glob_spec_dict = {}
        self.MAX_DSP_CNT = 0
        self.pattern_set_dict = {}
        self.dc_spec_dict = {}
        self.platform = 'UltraFLEX'
        self.tsb_dict = {}
        self.clock_dic = {}
        self.print_inst_info_col_cnt = 6
        self.write_row_index = 0
        self.cycle_mode = ""
        self.tset_dict = {}
        self.pat2inst_dict ={}
        self.progressbarOne = None
        self.power_list = []
        self.sort_bin_dscrp = []

    def reset(self):
        self.power_order_path = ''
        self.pattern_path = ''
        self.job_list_dict = ''
        self.flow_table_set = set()
        # self.device_directory = temp_directory
        self.work_sheet = None
        self.text = None
        self.last_flow_info = LastFlowInfo()
        self.glob_spec_dict = {}
        self.MAX_DSP_CNT = 0
        self.pattern_set_dict = {}
        self.dc_spec_dict = {}
        self.platform = 'UltraFLEX'
        self.tsb_dict = {}
        self.clock_dic = {}
        self.print_inst_info_col_cnt = 6
        self.write_row_index = 0
        self.cycle_mode = ""
        self.tset_dict = {}
        self.pat2inst_dict = {}
        self.progressbarOne = None
        self.power_list = []
        self.sort_bin_dscrp = []

    def read_device(self, device_path:str, power_order_path:str, pattern_path:str, platform, text, cycle_mode, progressbarOne):
        self.reset()
        self.text = text
        self.platform = platform
        self.cycle_mode = cycle_mode
        self.progressbarOne = progressbarOne
        if power_order_path != '':
            self.__put_data_log("Import Power Order File: " + power_order_path)
        self.power_order_path = power_order_path
        if self.pattern_path != '':
            self.__put_data_log("Import Pattern Path: " + pattern_path)
        self.pattern_path = pattern_path
        if os.path.isdir(device_path):
            self.device_directory = device_path
        else:
            if device_path.lower().endswith(".igxl") or device_path.lower().endswith(".zip"):
                unzip(device_path, self.device_directory)
            elif device_path.lower().endswith(".xlsm"):
                export_sheets_to_txt(device_path, self.device_directory)
            else:
                self.__put_data_log("Error: file extension is not supported.")
            device_name = os.path.join(self.device_directory, os.path.basename(device_path))
            device_name = os.path.splitext(device_name)[0]
            if os.path.isdir(device_name):
                self.device_directory = device_name
            else:
                pass
        job_list_pattern = re.compile(r'job.*list', re.IGNORECASE)
        job_list_path = ''
        for file_name in os.listdir(self.device_directory):
            job_list_name = re.search(job_list_pattern, file_name)
            if job_list_name is not None:
                job_list_path = os.path.join(self.device_directory, file_name)
                break
            else:
                pass
        pjl = ParseJobList()
        try:
            pjl.read_job_list(job_list_path)
        except FileNotFoundError:
            pass
        self.job_list_dict = pjl.get_test_job_list_info()

    def get_job_list(self):
        return self.job_list_dict

    def run(self, flow_table_set, work_dir="./"):
        time = datetime.datetime.now()
        current_time = str(datetime.date.today()) + "__" + str(time.hour) + str(time.minute) + str(time.second)
        output_name = os.path.join(work_dir, 'CheckInfo_' + current_time + '.xlsm')
        work_book = xlsxwriter.Workbook(output_name)
        self.format_red = work_book.add_format({'bg_color': '#FFC7CE'})
        self.format_yellow = work_book.add_format({'bg_color': '#F7D674'})
        self.format_orange = work_book.add_format({'bg_color': '#FFAA33'})
        self.format_bold = work_book.add_format({'bold': True})
        self.update_progressbar(0)
        try:
            for flow_name in flow_table_set:
                self.work_sheet = work_book.add_worksheet(flow_name)
                self.work_sheet.outline_settings(True, False, True, False)
                flow_path = self.device_directory + '/' + flow_name + '.txt'
                self.__run_each_flow(flow_path)
                self.excel_file_optimise(self.work_sheet)
            tset_work_sheet = work_book.add_worksheet("PatTsetMap_" + flow_name[0:20])
            self.write_pat_tset_map(self.pat2inst_dict, self.tset_dict, tset_work_sheet)
            bin_descrp_sheet = work_book.add_worksheet("SortBinDescrp") # + flow_name)
            self.write_bin_descrp(bin_descrp_sheet)
            inst_para_check_sheet = work_book.add_worksheet("InstParametersCheck")
            self.write_inst_para(inst_para_check_sheet)
            work_book.add_vba_project('./bin/vbaProject.bin')
            work_book.close()
            self.__put_data_log('Output file path is: ' + output_name)
            self.__put_data_log('Execution successful!!!')
            self.__put_data_log('===============================END===============================')
        except Exception as e:
            self.__put_data_log('An exception occurred!Please check!!!')
            self.__put_data_log(str(e))
            traceback.print_exc()
            work_book.close()
        return output_name

    def excel_file_optimise(self, worksheet):
        worksheet.autofilter(0, 0, 0, 100)
        worksheet.freeze_panes('C2')
        worksheet.set_row(0, 20, self.format_bold)

    def write_pat_tset_map(self, pat2inst_dict, my_dict, worksheet):
        worksheet.write(0, 0, 'Instances')
        worksheet.write(0, 1, 'Pattern')
        worksheet.write(0, 2, 'Tset_0')
        if self.cycle_mode == "Period":
            worksheet.write(0, 3, 'Period_0')
        else:
            worksheet.write(0, 3, 'Frequency_0')
        row_num = 1
        for key, value in my_dict.items():
            worksheet.write(row_num, 0, ",".join(pat2inst_dict[key]))
            worksheet.write(row_num, 1, key)
            tmp_list = list(chain.from_iterable(zip(value.keys(), value.values())))
            if len(value.keys()) > 1:
                for i in range(len(value.keys())):
                    worksheet.write(0, 2 + i * 2, 'Tset_' + str(i))
                    if self.cycle_mode == "Period":
                        worksheet.write(0, 2 + i * 2 + 1, 'Period_' + str(i))
                    else:
                        worksheet.write(0, 2 + i * 2 + 1, 'Frequency_' + str(i))
            worksheet.write_row(row_num, 2, tmp_list)
            row_num += 1
            self.update_progressbar(90 + 10*row_num/len(my_dict))

    def write_bin_descrp(self, worksheet):
        for i in range(len(self.sort_bin_dscrp)):
            line = self.sort_bin_dscrp[i]
            worksheet.write_row(i, 0, line)
        worksheet.conditional_format(0, 0, len(self.sort_bin_dscrp)-1, 0, {'type':   'duplicate', 'format':  self.format_red})

    def write_inst_para(self, worksheet):
        row_num = 0
        for key, value in self.test_instance_dict.items():
            if row_num == 0:
                worksheet.write(row_num, 0, 'Comment')
                worksheet.write(row_num, 1, 'Test Instance')
                worksheet.write_row(row_num, 2, value[0].keys())
                row_num += 1
            worksheet.write(row_num, 1, key)
            for i in range(len(value)):
                k_list = list(value[i].keys())
                for j in range(len(k_list)):
                    k = k_list[j]
                    v = value[i][k]
                    if k == 'ArgDetails':
                        worksheet.write_row(row_num, j + 2, v) #write info from column 2
                        worksheet.conditional_format(row_num, j + 2, row_num, j + len(v) + 1,
                                                     {'type': 'blanks',
                                                      'format': self.format_red})
                    else:
                        worksheet.write(row_num, j + 2, v) #write info from column 2
            row_num += 1
        self.excel_file_optimise(worksheet)


    def __put_data_log(self, data_log):
        self.text(data_log)
        # self.text.insert(tk.END, data_log + '\n')
        # self.text.see(tk.END)
        # self.text.update()

    def __init(self):
        self.work_sheet.write(0, 0, 'Opcode')
        self.work_sheet.write(0, 1, 'Parameter')
        self.work_sheet.write(0, 2, 'TestNumber')
        self.work_sheet.write(0, 3, 'HardBinNumber')
        self.work_sheet.write(0, 4, 'SortBinNumber')
        self.work_sheet.write(0, 5, 'Result')
        # self.work_sheet.write(0, 6, 'MCG CLK(ns)')

        self.work_sheet.set_column(1, 1, 20)
        self.work_sheet.set_column(2, 5, 15)
        self.write_row_index = 0


    def __test_table_process(self, flow_table_index, flow_table_info):
        test_suite_name = flow_table_info['Parameter']
        if test_suite_name in self.test_instance_dict.keys():
            for single_inst in self.test_instance_dict[test_suite_name]:
                self.work_sheet.write(flow_table_index + 1, 0, flow_table_info['Opcode'])
                self.work_sheet.write(flow_table_index + 1, 1, flow_table_info['Parameter'])
                self.work_sheet.write(flow_table_index + 1, 2, flow_table_info['TestNumber'])
                self.work_sheet.write(flow_table_index + 1, 3, flow_table_info['HardBin'])
                self.work_sheet.write(flow_table_index + 1, 4, flow_table_info['SortBin'])
                # self.work_sheet.write(flow_table_index + 1, 5, flow_table_info['Result'])

                if flow_table_info['Opcode'] == "nop":
                    self.work_sheet.set_row(row=flow_table_index + 1, cell_format=self.format_red)
                if flow_table_info['Result'] == "None" or flow_table_info['Result'] == "":
                    self.work_sheet.write(flow_table_index + 1, 5, flow_table_info['Result'], self.format_yellow)
                else:
                    self.work_sheet.write(flow_table_index + 1, 5, flow_table_info['Result'])
                flow_table_index += 1

    def __spec_calculation(self, target, spec_dict, category_name, selector_name):
        target = target.replace('=', '')
        target_list = re.split(r'[\+\-\*\/\(\)]', target)
        sample_list = re.findall(r'[\+\-\*\/\(\)]', target)
        sample_len = len(sample_list)
        for target_index, target_value in enumerate(target_list):
            if '_' in target_value:
                target_value_strip = target_value.replace('_', '', 1).replace(' ','')
                if target_value_strip in self.glob_spec_dict.keys():
                    result_value = self.glob_spec_dict[target_value_strip]
                else:
                    if self.spec_version == '3.0':
                        try:
                            spec_type = spec_dict[target_value_strip.upper()]['SELECTORS ' + selector_name.upper()]
                        except Exception as e:
                            self.__put_data_log("Error: Can not parse spec variable: " + target_value_strip)
                            # os.system('pause')
                    else:
                        spec_type = spec_dict[target_value_strip.upper()]['SELECTOR VAL']
                    result_value = spec_dict[target_value_strip][category_name.upper() + ' ' + spec_type]
                result_value = self.__spec_calculation(result_value, spec_dict, category_name, selector_name)
                if sample_list:
                    if target_index == sample_len:
                        pre_sample = sample_list[target_index - 1]
                        target = target.replace(pre_sample + target_value, pre_sample + result_value)
                    elif target_index == 0:
                        post_sample = sample_list[target_index]
                        target = target.replace(target_value + post_sample, result_value + post_sample, 1)
                    else:
                        post_sample = sample_list[target_index]
                        pre_sample = sample_list[target_index - 1]
                        target = target.replace(pre_sample + target_value + post_sample,
                                                pre_sample + result_value + post_sample)
                else:
                    target = target.replace(target_value, result_value)
            else:
                pass
        return target

    def add_unit(self, val):
        unit_dict = {
            '1000000000': 'G',
            '1000000': 'M',
            '1000': 'K',
            '0.001': 'm',
            '0.000001': 'u',
            '0.000000001': 'n',
            '0.000000000001': 'p'
        }

        for k,v in unit_dict.items():
            if val >= eval(k):
                value = float(val) / eval(k)
                return '%.3f%s' % (value, v)
        return

    def __extract_per_clk(self, pattern_name: str, timing_name: str, category_name: str, selector_name: str):
        # get tset from pattern
        period_val, clk_val = "", ""
        period_val_list, clk_val_list, period_val_tsetdict_list = [], [], []
        if self.pattern_path != "":
            if pattern_name in self.tset_dict.keys():
                tset_name_list = self.tset_dict[pattern_name].keys()
            else:
                ppat = ParsePatternSet()
                ppat.read_tset_from_pattern(self.pattern_path, pattern_name)
                tset_name_list = ppat.get_pattern_tset()
                # self.tset_dict[pattern_name] = tset_name_list

            for tset_name in tset_name_list:
                if tset_name.upper() in self.tsb_dict[timing_name].keys():
                    timing_period = self.tsb_dict[timing_name][tset_name.upper()]
                    mcg_clk_dic = self.clock_dic[timing_name][tset_name.upper()]

                    period_value = ""
                    try:
                        period_value = self.__spec_calculation(timing_period, self.ac_spec_dict, category_name, selector_name)
                        if self.cycle_mode == "Frequency":
                            period_value = "1/(" + period_value + ")"
                        period_val = self.add_unit(eval(format_str(period_value)))
                    except Exception as e:
                        period_val = "Error: cannot parse AC variables: " + timing_period + "=" + period_value
                        # self.__put_data_log("Error: cannot parse AC variables: " + timing_period)
                        # print("Error: cannot parse AC variables: " + timing_period)

                    clk_val = ""
                    if len(mcg_clk_dic) > 0:
                        tmpStr = ''
                        for k, v in mcg_clk_dic.items():
                            try:
                                mcg_clk_dic[k] = self.__spec_calculation(v, self.ac_spec_dict, category_name, selector_name)
                                if self.cycle_mode == "Frequency":
                                    mcg_clk_dic[k] = "1/(" + mcg_clk_dic[k] + ")"
                                tmp_clk = self.add_unit(eval(format_str(mcg_clk_dic[k])))
                            except Exception as e:
                                tmp_clk = "Error: cannot parse AC variables: " + k + "=" + mcg_clk_dic[k]
                            tmpStr = tmpStr + k + ":" + tmp_clk + ";"
                        clk_val = tmpStr
                    # break
                else:
                    period_val, clk_val = "", ""
                    self.__put_data_log("Warning: Tset(" + tset_name + ") in pattern(" + pattern_name + ") is not list in TSB: " + timing_name)
                    print("Warning: Tset(" + tset_name + ") in pattern(" + pattern_name + ") is not list in TSB: " + timing_name)
                # in case same pattern with diff AC spec, which leads to diff period
                if pattern_name in self.tset_dict.keys():
                    # if period_val not in self.tset_dict[pattern_name][tset_name]:
                    period_val_for_tset_dict = self.tset_dict[pattern_name][tset_name] + "," + period_val
                else:
                    period_val_for_tset_dict = period_val
                period_val_list.append(period_val)
                clk_val_list.append(clk_val)
                period_val_tsetdict_list.append(period_val_for_tset_dict)
            self.tset_dict[pattern_name] = dict(zip(tset_name_list, period_val_tsetdict_list))
        else:
            period_val_list, clk_val_list, period_val_tsetdict_list = [""], [""], [""]
        return period_val_list, clk_val_list

    def __pattern_period_clk_process(self, dps_count, write_row_start, flow_table_info, flow_table_directory):
        test_suite_name = flow_table_info['Parameter']
        flow_table_index = write_row_start
        if test_suite_name in self.test_instance_dict.keys():
            # if inst with multiple conditions/parameters
            if len(self.test_instance_dict[test_suite_name]) > 1:
                self.work_sheet.set_row(flow_table_index + 1, None, None, {'collapsed': True})
            for single_inst in self.test_instance_dict[test_suite_name]:
                pattern_name = single_inst['Pattern']
                timing_name = single_inst['TimeSet']
                category_name = single_inst['AC Category']
                selector_name = single_inst['AC Selector']
                if pattern_name != '' and timing_name != '':
                    # get timing & tset info
                    pt = ParseTIM()
                    pt.read_timing(os.path.join(flow_table_directory, timing_name.split(',')[0] + '.txt'), self.platform)
                    self.tsb_dict[timing_name] = pt.get_timing_info()
                    self.clock_dic[timing_name] = pt.get_clk_info()

                    # print pattern name & period
                    pattern_index = self.print_inst_info_col_cnt + dps_count
                    self.work_sheet.write(0, pattern_index, 'PatternName_0')
                    self.work_sheet.write(0, pattern_index + 1, 'Period_0')
                    if self.cycle_mode == "Frequency":
                        self.work_sheet.write(0, pattern_index + 1, 'Freq_0')
                    self.work_sheet.write(0, pattern_index + 2, 'Clock_0')
                    self.work_sheet.set_column(pattern_index, pattern_index, 40)
                    if ',' not in pattern_name:
                        # get period & clk
                        try:
                            period_val_list, clk_val_list = self.__extract_per_clk(pattern_name, timing_name, category_name, selector_name)
                            # store pat2inst map
                            if pattern_name not in self.pat2inst_dict.keys():
                                self.pat2inst_dict[pattern_name] = [test_suite_name]
                            else:
                                self.pat2inst_dict[pattern_name].append(test_suite_name)
                        except Exception as e:
                            period_val_list, clk_val_list = [""], [""]
                            self.__put_data_log("Warning: cannot read pattern file: " + pattern_name)
                            print("Warning: cannot read pattern file: " + pattern_name)
                        self.work_sheet.write(flow_table_index + 1, pattern_index, pattern_name)
                        self.work_sheet.write(flow_table_index + 1, pattern_index + 1, ",".join(period_val_list)) #xxxx
                        self.work_sheet.write(flow_table_index + 1, pattern_index + 2, ",".join(clk_val_list))
                    else:
                        pattern_list = pattern_name.split(",")
                        for pattern_index, pattern_name in enumerate(pattern_list):
                            pattern_index_new = self.print_inst_info_col_cnt + dps_count + 3 * pattern_index
                            # get period & clk
                            try:
                                period_val_list, clk_val_list = self.__extract_per_clk(pattern_name, timing_name, category_name,
                                                                             selector_name)
                                # store pat2inst map
                                if pattern_name not in self.pat2inst_dict.keys():
                                    self.pat2inst_dict[pattern_name] = [test_suite_name]
                                else:
                                    self.pat2inst_dict[pattern_name].append(test_suite_name)
                            except Exception as e:
                                period_val_list, clk_val_list = [""], [""]
                                self.__put_data_log("Warning: cannot read pattern file: " + pattern_name)
                                print("Warning: cannot read pattern file: " + pattern_name)
                            self.work_sheet.write(0, pattern_index_new, 'PatternName_' + str(pattern_index))
                            self.work_sheet.write(flow_table_index + 1, pattern_index_new, pattern_name)
                            self.work_sheet.set_column(pattern_index_new, pattern_index_new, 40)

                            self.work_sheet.write(0, pattern_index_new + 1, 'Period_' + str(pattern_index))
                            if self.cycle_mode == "Frequency":
                                self.work_sheet.write(0, pattern_index_new + 1, 'Freq_' + str(pattern_index))
                            self.work_sheet.write(flow_table_index + 1, pattern_index_new + 1, ",".join(period_val_list)) #xxxx

                            self.work_sheet.write(0, pattern_index_new + 2, 'Clock_' + str(pattern_index))
                            self.work_sheet.write(flow_table_index + 1, pattern_index_new + 2, ",".join(clk_val_list))  # xxxx
                else:
                    pass
                if flow_table_index != write_row_start:
                    self.work_sheet.set_row(flow_table_index + 1, None, None, {'level': 1, 'hidden': True})
                flow_table_index += 1
        else:
            self.__put_data_log("Info: cannot found " + test_suite_name + " in Test Instance, please check.")
            print("Info: cannot found " + test_suite_name + " in Test Instance, please check.")

    # def __period_process(self, flow_table_directory, flow_table_index, flow_table_info):
    #     test_suite_name = flow_table_info['Parameter']
    #     timing_name = self.test_instance_dict[test_suite_name]['TimeSet']
    #     category_name = self.test_instance_dict[test_suite_name]['AC Category']
    #     selector_name = self.test_instance_dict[test_suite_name]['AC Selector']
    #     if timing_name != '':
    #         pt = ParseTIM()
    #         pt.read_timing(os.path.join(flow_table_directory, timing_name.split(',')[0] + '.txt'), self.platform)
    #         self.tsb_dict[timing_name] = pt.get_timing_info()
    #         self.clock_dic[timing_name] = pt.get_clk_info()
    #
    #         timing_period = self.tsb_dict[timing_name][tset_name]
    #         mcg_clk_dic = self.clock_dic[timing_name][tset_name]
    #         try:
    #             period_value = self.__spec_calculation(timing_period, self.ac_spec_dict, category_name, selector_name)
    #             self.work_sheet.write(flow_table_index + 1, 5, eval(format_str(period_value)))
    #         except Exception as e:
    #             self.work_sheet.write(flow_table_index + 1, 5, "Error: cannot parse AC variables: " + timing_period + "=" + period_value)
    #             # self.__put_data_log("Error: cannot parse AC variables: " + timing_period)
    #             # print("Error: cannot parse AC variables: " + timing_period)
    #         if mcg_clk_dic.__len__() > 0:
    #             tmpStr = ''
    #             for k,v in mcg_clk_dic.items():
    #                 mcg_clk_dic[k]=self.__spec_calculation(v, self.ac_spec_dict, category_name, selector_name)
    #                 tmpStr = tmpStr + k +":"+mcg_clk_dic[k]+";"
    #             self.work_sheet.write(flow_table_index + 1, 6, tmpStr)
    #     else:
    #         pass

    def __power_process_and_get_count(self, flow_table_directory, flow_table_info, flow_table_index):
        dps_count = 0
        test_suite_name = flow_table_info['Parameter']
        if test_suite_name in self.test_instance_dict.keys():
            for single_inst in self.test_instance_dict[test_suite_name]:
                dps_index_start = self.print_inst_info_col_cnt
                dps_count = 0
                if single_inst['DC Category'] != '':
                    level_sheet_name = single_inst['PinLevel']
                    category_name = single_inst['DC Category']
                    selector_name = single_inst['DC Selector']
                    ppl = ParsePinLevel()
                    ppl.read_pin_level(os.path.join(flow_table_directory, level_sheet_name + '.txt'))
                    pin_level_origin_dict = ppl.get_pin_level_info()
                    dps_count = len(pin_level_origin_dict)
                    pin_level_dict = collections.OrderedDict()
                    power_pin_alias_dict = collections.OrderedDict()
                    if self.power_order_path != '':
                        read_book = xlrd.open_workbook(self.power_order_path)
                        read_sheet = read_book.sheet_by_index(0)
                        rows = read_sheet.nrows
                        for row in range(rows):
                            try:
                                power_pin_name = read_sheet.cell(row + 1, 0).value
                                alias = read_sheet.cell(row + 1, 1).value
                                power_pin_alias_dict[power_pin_name] = alias if alias != '' else power_pin_name
                            except IndexError:
                                break
                            if power_pin_name in pin_level_origin_dict.keys():
                                pin_level_dict[power_pin_name] = pin_level_origin_dict[power_pin_name]
                            else:
                                self.__put_data_log('Cannot find power pin name in pin level file!')
                                self.__put_data_log('Power pin name is: ' + power_pin_name)
                    else:
                        pin_level_dict = pin_level_origin_dict
                        for power_pin_name in pin_level_origin_dict.keys():
                            power_pin_alias_dict[power_pin_name] = power_pin_name

                    for pin_level_name, pin_level_info in pin_level_dict.items():
                        cur_power_pin = power_pin_alias_dict[pin_level_name]
                        if cur_power_pin in self.power_list:
                            # get index of power pin
                            dps_index = dps_index_start + self.power_list.index(cur_power_pin)
                        else:
                            self.power_list.append(cur_power_pin)
                            dps_index = dps_index_start + len(self.power_list) - 1
                            self.work_sheet.write(0, dps_index, cur_power_pin)
                            self.work_sheet.set_column(dps_index, dps_index, 15)
                        power_value = self.__spec_calculation(pin_level_info, self.dc_spec_dict, category_name, selector_name)
                        power_value = round(float(eval(format_str(power_value))), 5)
                        if power_value == 0:
                            self.work_sheet.write(flow_table_index + 1, dps_index, str(power_value), self.format_orange)
                        else:
                            self.work_sheet.write(flow_table_index + 1, dps_index, str(power_value))

                else:
                    pass
                flow_table_index += 1
            dps_count = len(self.power_list)
        else:
            self.__put_data_log("Info: cannot found " + test_suite_name + " in Test Instance, please check.")
            print("Info: cannot found " + test_suite_name + " in Test Instance, please check.")

        return dps_count

    def save_max_col(self, col_cnt:int):
        if self.MAX_DSP_CNT < col_cnt:
            self.MAX_DSP_CNT = col_cnt

    def update_progressbar(self, val):
        self.progressbarOne(val)

    def __run_each_flow(self, flow_path):
        self.update_progressbar(1)
        flow_table_directory = '/'.join(flow_path.split('/')[:-1])
        flow_table = flow_path.split('/')[-1]
        pre_flow_name = flow_table.split('.')[0]
        self.__put_data_log('Parse Flow Table: ' + pre_flow_name)
        if flow_path == '':
            self.__put_data_log('Flow Table Path Cannot be Empty, Please Check!')
            return
        else:
            flow_path = flow_path.replace(' ', '%20')
            pft = ParseFlowTable()
            pft.read_flow_table(flow_path, self.platform)
            flow_table_info_list = pft.get_test_suite_info()

            dc_spec_name_temp = self.job_list_dict[pre_flow_name]['DC Spec']
            dc_spec_name = os.path.join(flow_table_directory, dc_spec_name_temp + '.txt')
            dc_spec_name_replace_space = os.path.join(flow_table_directory,
                                                      dc_spec_name_temp.replace(' ', '%20') + '.txt')
            dc_spec_name = dc_spec_name if os.path.exists(dc_spec_name) else dc_spec_name_replace_space

            ac_spec_name_temp = self.job_list_dict[pre_flow_name]['AC Spec']
            ac_spec_name = os.path.join(flow_table_directory, ac_spec_name_temp + '.txt')
            ac_spec_name_replace_space = os.path.join(flow_table_directory,
                                                      ac_spec_name_temp.replace(' ', '%20') + '.txt')
            ac_spec_name = ac_spec_name if os.path.exists(ac_spec_name) else ac_spec_name_replace_space

            # add global spec support
            glob_spec_name_temp = self.job_list_dict[pre_flow_name]['Global Spec']
            glob_spec_name = os.path.join(flow_table_directory, glob_spec_name_temp + '.txt')
            glob_spec_name_replace_space = os.path.join(flow_table_directory,
                                                      glob_spec_name_temp.replace(' ', '%20') + '.txt')
            glob_spec_name = glob_spec_name if os.path.exists(glob_spec_name) else glob_spec_name_replace_space

            pattern_set_name_list = self.job_list_dict[pre_flow_name]['PatternSet']
            pattern_set_name_list = [os.path.join(flow_table_directory, pattern_set_name.replace(' ', '%20') + '.txt') for pattern_set_name in pattern_set_name_list if pattern_set_name_list]

            # pattern_set_name = os.path.join(flow_table_directory, pattern_set_name_temp + '.txt')
            # pattern_set_name_replace_space = os.path.join(flow_table_directory,
            #                                               pattern_set_name_temp.replace(' ', '%20') + '.txt')
            # pattern_set_name = pattern_set_name if os.path.exists(pattern_set_name) else pattern_set_name_replace_space

            test_instance_list = self.job_list_dict[pre_flow_name]['TestInstanceList']
            test_instance_list = [os.path.join(flow_table_directory, test_instance_name.replace(' ', '%20') + '.txt') for test_instance_name
                                  in
                                  test_instance_list if test_instance_list]
            self.update_progressbar(2)

            # Process pattern set sheet(s)
            pps = ParsePatternSet()
            if pattern_set_name_list:
                for pattern_set_name in pattern_set_name_list:
                    if self.last_flow_info.pattern_set_name != pattern_set_name: # and LastFlowInfo.pattern_set_name is not None:
                        # pps = ParsePatternSet()
                        try:
                            pps.read_pattern_set(pattern_set_name, self.pattern_path, self.platform)
                            # self.pattern_set_dict = pps.get_pattern_set_info()
                            # self.pattern_cycle_dict = pps.get_pattern_cycle_info()
                            self.last_flow_info.pattern_set_name = pattern_set_name
                        except Exception as e:
                            self.__put_data_log("Warning: cannot read PatternSet, please check it!")
                    else:
                        pass
            self.pattern_set_dict = pps.get_pattern_set_info()
            self.pattern_cycle_dict = pps.get_pattern_cycle_info()
            self.update_progressbar(3)

            pti = ParseTestInstance()
            if test_instance_list:
                for test_instance_name in test_instance_list:
                    try:
                        pti.read_test_instance(test_instance_name, self.pattern_set_dict, self.platform)
                    except Exception as e:
                        self.__put_data_log("Error: cannot read " + test_instance_name + ", please check it!")
                        print(str(e))
            else:
                pass
            self.test_instance_dict = pti.get_instance_info()
            self.update_progressbar(4)
            # if LastFlowInfo.pattern_set_name != pattern_set_name:
            #     pps = ParsePatternSet()
            #     pps.read_pattern_set(pattern_set_name, self.pattern_path)
            #     self.pattern_set_dict = pps.get_pattern_set_info()
            #     self.pattern_cycle_dict = pps.get_pattern_cycle_info()
            #     LastFlowInfo.pattern_set_name = pattern_set_name
            # else:
            #     pass
            if self.last_flow_info.dc_spec_name != dc_spec_name:
                pds = ParseDCSpec()
                pds.read_dc_spec(dc_spec_name, self.platform)
                self.dc_spec_dict = pds.get_dc_info()
                self.last_flow_info.dc_spec_name = dc_spec_name
            else:
                pass
            self.update_progressbar(5)

            if self.last_flow_info.glob_spec_name != glob_spec_name:
                pds = ParseGlobalSpec()
                try:
                    pds.read_spec(glob_spec_name, self.platform)
                    self.glob_spec_dict = pds.get_info()
                    self.last_flow_info.glob_spec_name = glob_spec_name
                except Exception as e:
                    self.__put_data_log("Warning: cannot read Global Specs, please check it!")
            else:
                pass
            self.update_progressbar(6)

            if self.last_flow_info.ac_spec_name is not None:
                if self.last_flow_info.ac_spec_name != ac_spec_name:
                    pas = ParseACSpec()
                    pas.read_ac_spec(ac_spec_name, self.platform)
                    self.ac_spec_dict = pas.get_ac_info()
                    ac_spec_version = pas.get_spec_version()
                    self.spec_version = ac_spec_version
                    self.last_flow_info.ac_spec_name = ac_spec_name
            else:
                pass
            self.update_progressbar(7)

            self.__init()
            self.sort_bin_dscrp = []
            for flow_table_index, flow_table_info in enumerate(flow_table_info_list):
                test_suite_name = flow_table_info['Parameter']
                test_sort_bin = flow_table_info["SortBin"]
                if test_sort_bin != "":
                    self.sort_bin_dscrp.append([test_sort_bin, test_suite_name])
                flow_table_info_list[flow_table_index]["write_row_start"] = self.write_row_index
                if test_suite_name in self.test_instance_dict.keys():
                    self.write_row_index += len(self.test_instance_dict[test_suite_name])
                self.update_progressbar(8 + 10 * flow_table_index/len(flow_table_info_list))

            self.power_list = []
            for flow_table_index, flow_table_info in enumerate(flow_table_info_list):
                write_row = flow_table_info_list[flow_table_index]["write_row_start"]
                try:
                    self.__test_table_process(write_row, flow_table_info)
                    dps_count = self.__power_process_and_get_count(flow_table_directory, flow_table_info, write_row)
                    self.save_max_col(dps_count)
                except Exception as e:
                    self.__put_data_log("Error found in power process:")
                    self.__put_data_log(str(e))
                    self.__put_data_log(str(flow_table_index) + " - " + flow_table_info.__str__())
                    print(flow_table_index,flow_table_info)
                self.write_row_index += 1
                self.update_progressbar(19 + 10 * flow_table_index/len(flow_table_info_list))

            # Without Pandas, first write instance name/power, then write pat to align column
            for flow_table_index, flow_table_info in enumerate(flow_table_info_list):
                write_row = flow_table_info_list[flow_table_index]["write_row_start"]
                try:
                    # if flow_table_info["Parameter"] == "DNA_READ_PCM_TEST":
                    #     print("OK")
                    self.__pattern_period_clk_process(self.MAX_DSP_CNT, write_row, flow_table_info, flow_table_directory)
                except Exception as e:
                    self.__put_data_log("Error found in pattern/timing process:")
                    self.__put_data_log(str(e))
                    self.__put_data_log(str(flow_table_index) + " - " + flow_table_info.__str__())
                    print(flow_table_index,flow_table_info)
                self.update_progressbar(30 + 70 * (flow_table_index + 1) / len(flow_table_info_list))