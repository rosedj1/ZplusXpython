from shutil import copy2

class TemplateManager:

    def __init__(self, input_template):
        self.input_template = input_template

    def duplicate_template(self, output_template):
        """Copy `self.input_template` to `output_template`."""
        print(f"Making copy of {self.input_template}:\n{output_template}")
        copy2(self.input_template, output_template)