from parse_spec import ParseSpec


class ParseDCSpec(ParseSpec):

    def read_dc_spec(self, dc_spec_path, platform):
        super().read_spec(dc_spec_path, platform)

    def get_dc_info(self):
        return super().get_info()

    def __init__(self):
        super().__init__()

