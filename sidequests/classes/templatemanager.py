from shutil import copy2

class TemplateManager:

    def __init__(self, input_template):
        self.in_temp = input_template

    def duplicate_template(self, output_template):
        """Copy `self.in_temp` to `output_template`."""
        print(f"Making copy of {self.in_temp}:\n{output_template}")
        copy2(self.in_temp, output_template)
