from parse_spec import ParseSpec


class ParseACSpec(ParseSpec):

    def read_ac_spec(self, ac_spec_path):
        super().read_spec(ac_spec_path)

    def get_ac_info(self):
        return super().get_info()

    def __init__(self):
        super().__init__()


