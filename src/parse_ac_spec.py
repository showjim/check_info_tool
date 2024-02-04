from src.parse_spec import ParseSpec


class ParseACSpec(ParseSpec):

    def read_ac_spec(self, ac_spec_path, platform):
        super().read_spec(ac_spec_path, platform)

    def get_ac_info(self):
        return super().get_info()

    def __init__(self):
        super().__init__()


