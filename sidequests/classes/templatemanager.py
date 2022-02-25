from shutil import copy2
from Utils_Python.Utils_Files import replace_value, check_overwrite

class TemplateManager:

    def __init__(self, input_template):
        self.input_template = input_template

    def duplicate_template(self, output_template, overwrite=False):
        """Copy `self.input_template` to `output_template`."""
        check_overwrite(output_template, overwrite=overwrite)
        print(f"Making copy of {self.input_template}:\n{output_template}")
        copy2(self.input_template, output_template)

    def replace_vals(self, template, **kwargs):
        """Replace all keys in `kwargs` with their values inside `template`.

        Args:
            template (str): Path to template file.
        
        Example:
            Suppose you have the values:
                REPLACE_ME and SOME_NUM inside of `template`.
            Also suppose that,
                kwargs = {
                    REPLACE_ME='this_val',
                    SOME_NUM=14,
                }
            Then inside `template`, REPLACE_ME will be replaced by 'this_val'
            and SOME_NUM will be replaced by 14.

        """
        for old, new in kwargs.items():
            _ = replace_value(old=old, new=new, script=template)
