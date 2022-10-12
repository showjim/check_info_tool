from parse_flow_table import ParseFlowTable
from parse_dc_spec import ParseDCSpec
from parse_ac_spec import ParseACSpec
from parse_level import ParsePinLevel
from parse_timing import ParseTIM
from parse_job_list import ParseJobList
from parse_pattern_set import ParsePatternSet
from parse_test_instance import ParseTestInstance
from common import unzip, format_str
import collections
import tkinter as tk
import os
import re
import datetime
import xlwt
import xlrd
import traceback


class LastFlowInfo:
    dc_spec_name = None
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

    def read_device(self, device_path, power_order_path, pattern_path, text):
        self.text = text
        if power_order_path != '':
            self.__put_data_log("Import Power Order File: " + power_order_path)
        self.power_order_path = power_order_path
        if self.pattern_path != '':
            self.__put_data_log("Import Pattern Path: " + pattern_path)
        self.pattern_path = pattern_path
        if os.path.isdir(device_path):
            self.device_directory = device_path
        else:
            unzip(device_path, self.device_directory)
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

    def run(self, flow_table_set):
        try:
            time = datetime.datetime.now()
            current_time = str(time.month) + str(time.day) + str(time.hour) + str(time.minute) + str(time.second)
            work_book = xlwt.Workbook()
            for flow_name in flow_table_set:
                self.work_sheet = work_book.add_sheet(flow_name, cell_overwrite_ok=True)
                flow_path = self.device_directory + '/' + flow_name + '.txt'
                self.__run_each_flow(flow_path)
            output_name = 'CheckInfo_' + current_time + '.xls'
            work_book.save(output_name)
            self.__put_data_log('Output file path is: ' + output_name)
            self.__put_data_log('Execution successful!!!')
            self.__put_data_log('===============================END===============================')
        except Exception as e:
            self.__put_data_log('An exception occurred!Please check!!!')
            self.__put_data_log(str(e))
            traceback.print_exc()

    def __put_data_log(self, data_log):
        self.text.insert(tk.END, data_log + '\n')
        self.text.see(tk.END)
        self.text.update()

    def __init(self):
        self.work_sheet.write(0, 0, label='Opcode')
        self.work_sheet.write(0, 1, label='Parameter')
        self.work_sheet.write(0, 2, label='TestNumber')
        self.work_sheet.write(0, 3, label='HardBinNumber')
        self.work_sheet.write(0, 4, label='SoftBinNumber')
        self.work_sheet.write(0, 5, label='Period(ns)')
        self.work_sheet.write(0, 6, label='MCG CLK(ns)')
        self.work_sheet.col(1).width = 256 * 20
        self.work_sheet.col(2).width = 256 * 15
        self.work_sheet.col(3).width = 256 * 15
        self.work_sheet.col(4).width = 256 * 15
        self.work_sheet.col(5).width = 256 * 12
        self.work_sheet.col(6).width = 256 * 12

    def __test_table_process(self, flow_table_index, flow_table_info):
        self.work_sheet.write(flow_table_index + 1, 0, label=flow_table_info['Opcode'])
        self.work_sheet.write(flow_table_index + 1, 1, label=flow_table_info['Parameter'])
        self.work_sheet.write(flow_table_index + 1, 2, label=flow_table_info['TestNumber'])
        self.work_sheet.write(flow_table_index + 1, 3, label=flow_table_info['HardBin'])
        self.work_sheet.write(flow_table_index + 1, 4, label=flow_table_info['SoftBin'])

    def __spec_calculation(self, target, spec_dict, category_name, selector_name):
        target = target.replace('=', '')
        target_list = re.split(r'[\+\-\*\/\(\)]', target)
        sample_list = re.findall(r'[\+\-\*\/\(\)]', target)
        sample_len = len(sample_list)
        for target_index, target_value in enumerate(target_list):
            if '_' in target_value:
                target_value_strip = target_value.replace('_', '', 1).replace(' ','')
                if self.spec_version == '3.0':
                    try:
                        spec_type = spec_dict[target_value_strip.upper()]['SELECTORS ' + selector_name.upper()]
                    except:
                        os.system('pause')
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

    def __pattern_process(self, dps_count, flow_table_index, flow_table_info):
        test_suite_name = flow_table_info['Parameter']
        pattern_name = self.test_instance_dict[test_suite_name]['Pattern']
        if pattern_name != '':
            pattern_index = 6 + dps_count
            self.work_sheet.write(0, pattern_index, label='PatternName')
            self.work_sheet.write(0, pattern_index + 1, label='CycleCount')
            self.work_sheet.col(pattern_index).width = 256 * 40
            self.work_sheet.write(flow_table_index + 1, pattern_index, label=pattern_name)
            pattern_index = pattern_index + 1
            if ',' not in pattern_name:
                try:
                    cycle_count =0# self.pattern_cycle_dict[pattern_name]
                except:
                    os.system('pause')
                self.work_sheet.write(flow_table_index + 1, pattern_index, label=str(cycle_count))
                pattern_index = pattern_index + 1
                main_pattern_list = self.pattern_set_dict[pattern_name]
                for main_pattern_index, main_pattern_name in enumerate(main_pattern_list):
                    self.work_sheet.write(flow_table_index + 1, pattern_index + main_pattern_index,
                                          label=main_pattern_name)
                    self.work_sheet.write(0, pattern_index + main_pattern_index,
                                          label='MainPattern_' + str(main_pattern_index + 1))
                    self.work_sheet.col(pattern_index + main_pattern_index).width = 256 * 40
            else:
                self.__put_data_log('Cannot Support Multi Burst Pattern Parse!')
                self.__put_data_log(' Multi Burst Pattern is: ' + pattern_name)

    def __period_process(self, flow_table_directory, flow_table_index, flow_table_info):
        test_suite_name = flow_table_info['Parameter']
        timing_name = self.test_instance_dict[test_suite_name]['TimeSet']
        category_name = self.test_instance_dict[test_suite_name]['AC Category']
        selector_name = self.test_instance_dict[test_suite_name]['AC Selector']
        if timing_name != '':
            pt = ParseTIM()
            pt.read_timing(os.path.join(flow_table_directory, timing_name.split(',')[0] + '.txt'))
            timing_period = pt.get_timing_info()
            mcg_clk_dic = pt.get_clk_info()
            period_value = self.__spec_calculation(timing_period, self.ac_spec_dict, category_name, selector_name)
            self.work_sheet.write(flow_table_index + 1, 5, label=eval(format_str(period_value)))
            if mcg_clk_dic.__len__() >0:
                tmpStr = ''
                for k,v in mcg_clk_dic.items():
                    mcg_clk_dic[k]=self.__spec_calculation(v, self.ac_spec_dict, category_name, selector_name)
                    tmpStr = tmpStr + k +":"+mcg_clk_dic[k]+";"
                self.work_sheet.write(flow_table_index + 1, 6, label=tmpStr)
        else:
            pass

    def __power_process_and_get_count(self, flow_table_directory, flow_table_info, flow_table_index):
        dps_index = 7#6
        dps_count = 0
        test_suite_name = flow_table_info['Parameter']
        if self.test_instance_dict[test_suite_name]['DC Category'] != '':
            level_sheet_name = self.test_instance_dict[test_suite_name]['PinLevel']
            category_name = self.test_instance_dict[test_suite_name]['DC Category']
            selector_name = self.test_instance_dict[test_suite_name]['DC Selector']
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
                self.work_sheet.write(0, dps_index, label=power_pin_alias_dict[pin_level_name])
                self.work_sheet.col(dps_index).width = 256 * 15
                power_value = self.__spec_calculation(pin_level_info, self.dc_spec_dict, category_name, selector_name)
                power_value = round(float(eval(format_str(power_value))), 5)
                self.work_sheet.write(flow_table_index + 1, dps_index, label=str(power_value))
                dps_index = dps_index + 1
        else:
            pass

        return dps_count

    def __run_each_flow(self, flow_path):
        flow_table_directory = '/'.join(flow_path.split('/')[:-1])
        flow_table = flow_path.split('/')[-1]
        pre_flow_name = flow_table.split('.')[0]
        self.__put_data_log('Parse Flow Table: ' + pre_flow_name)
        if flow_path == '':
            self.__put_data_log('Flow Table Path Cannot be Empty, Please Check!')
            return
        else:
            pft = ParseFlowTable()
            pft.read_flow_table(flow_path)
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

            pattern_set_name_temp = self.job_list_dict[pre_flow_name]['PatternSet']
            pattern_set_name = os.path.join(flow_table_directory, pattern_set_name_temp + '.txt')
            pattern_set_name_replace_space = os.path.join(flow_table_directory,
                                                          pattern_set_name_temp.replace(' ', '%20') + '.txt')
            pattern_set_name = pattern_set_name if os.path.exists(pattern_set_name) else pattern_set_name_replace_space
            test_instance_list = self.job_list_dict[pre_flow_name]['TestInstanceList']
            test_instance_list = [os.path.join(flow_table_directory, test_instance_name + '.txt') for test_instance_name
                                  in
                                  test_instance_list if test_instance_list]
            pti = ParseTestInstance()
            if test_instance_list:
                for test_instance_name in test_instance_list:
                    pti.read_test_instance(test_instance_name)
            else:
                pass
            self.test_instance_dict = pti.get_instance_info()
            if LastFlowInfo.pattern_set_name != pattern_set_name:
                pps = ParsePatternSet()
                pps.read_pattern_set(pattern_set_name, self.pattern_path)
                self.pattern_set_dict = pps.get_pattern_set_info()
                self.pattern_cycle_dict = pps.get_pattern_cycle_info()
                LastFlowInfo.pattern_set_name = pattern_set_name
            else:
                pass
            if LastFlowInfo.dc_spec_name != dc_spec_name:
                pds = ParseDCSpec()
                pds.read_dc_spec(dc_spec_name)
                self.dc_spec_dict = pds.get_dc_info()
                LastFlowInfo.dc_spec_name = dc_spec_name
            else:
                pass
            if LastFlowInfo.ac_spec_name != ac_spec_name:
                pas = ParseACSpec()
                pas.read_ac_spec(ac_spec_name)
                self.ac_spec_dict = pas.get_ac_info()
                ac_spec_version = pas.get_spec_version()
                self.spec_version = ac_spec_version
                LastFlowInfo.ac_spec_name = ac_spec_name
            else:
                pass
            self.__init()
            for flow_table_index, flow_table_info in enumerate(flow_table_info_list):
                try:
                    self.__test_table_process(flow_table_index, flow_table_info)
                    self.__period_process(flow_table_directory, flow_table_index, flow_table_info)
                    dps_count = self.__power_process_and_get_count(flow_table_directory, flow_table_info, flow_table_index)
                    self.__pattern_process(dps_count, flow_table_index, flow_table_info)
                except Exception as e:
                    print(flow_table_index,flow_table_info)
