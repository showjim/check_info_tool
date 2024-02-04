import zipfile


def unzip(file_name, path):
    unzip_format = zipfile.is_zipfile(file_name)
    if unzip_format:
        zip_file = zipfile.ZipFile(file_name)
        for names in zip_file.namelist():
            zip_file.extract(names, path + '/')
        zip_file.close()
    else:
        print('Need Zip Format, Please Check!!!')


def format_str(target_str):
    if True:
        target_str = target_str.replace('=', '')
        target_str = target_str.replace('*MV', '*0.001')
        target_str = target_str.replace('*MA', '*0.001')
        target_str = target_str.replace('*UV', '*0.000001')
        target_str = target_str.replace('*UA', '*0.000001')
        target_str = target_str.replace('*V', '*1')
        target_str = target_str.replace('*A', '*1')
        target_str = target_str.replace('*PS', '*0.000000000001')
        target_str = target_str.replace('*NS', '*0.000000001')
        target_str = target_str.replace('*US', '*0.000001')
        target_str = target_str.replace('*MS', '*0.001')
        target_str = target_str.replace('*GHZ', '*1000000000')
        target_str = target_str.replace('*MHZ', '*1000000')
        target_str = target_str.replace('*KHZ', '*1000')
    else:
        target_str = target_str.replace('=', '')
        target_str = target_str.replace('*MV', '*0.001')
        target_str = target_str.replace('*MA', '*0.001')
        target_str = target_str.replace('*UV', '*0.000001')
        target_str = target_str.replace('*UA', '*0.000001')
        target_str = target_str.replace('*V', '*1')
        target_str = target_str.replace('*A', '*1')
        target_str = target_str.replace('*PS', '*0.001')
        target_str = target_str.replace('*NS', '*1')
        target_str = target_str.replace('*US', '*1000')
        target_str = target_str.replace('*MS', '*1000000')
        target_str = target_str.replace('*GHZ', '*1')
        target_str = target_str.replace('*MHZ', '*0.001')
        target_str = target_str.replace('*KHZ', '*0.000001')

    return target_str
