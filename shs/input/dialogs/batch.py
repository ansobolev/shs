import os
from collections import OrderedDict
import wx
from wx.wizard import Wizard, WizardPageSimple

from shs.input.dialogs.batch_pages import SelectPage, FillInPage, DirHierarchyPage, DirNamePage


class BatchWizard(Wizard):

    def __init__(self, *args, **kwds):
        options = kwds.pop('options', {})
        self.extra = kwds.pop('extra', '')
        self.values = {}
        self.fdf_options = options
        self.options = self.make_options_dict(options)
        
        Wizard.__init__(self, *args, **kwds)
        self.select_page = SelectPage(self)
        self.fill_in_page = FillInPage(self)
        self.dh_page = DirHierarchyPage(self)
        self.name_page = DirNamePage(self)
        WizardPageSimple.Chain(self.select_page, self.fill_in_page)
        WizardPageSimple.Chain(self.fill_in_page, self.dh_page)
        WizardPageSimple.Chain(self.dh_page, self.name_page)
        self.__set_properties(options)
        self.__do_layout()

    @staticmethod
    def make_options_dict(options):
        # flattening options 
        result = OrderedDict()
        for panels, option_dict in options.iteritems():
            for option, instance in option_dict.iteritems():
                if type(instance.fdf_text) == list:
                    for t in instance.fdf_text:
                        if t.lower() == option:
                            result[t] = instance
                else:
                    result[instance.fdf_text] = instance
        return result

    def add_FDF_option(self, option):
        self.values[option] = {"values": [],
                               "level": 1}
        self.fill_in_page.add_FDF_option(option)
        self.dh_page.add_FDF_option(option)
        self.name_page.add_to_level(option, 1)

    def remove_FDF_option(self, option):
        v = self.values.pop(option)
        i_level = v["level"]
        self.fill_in_page.remove_FDF_option(option)
        self.dh_page.remove_FDF_option(option)
        self.name_page.remove_from_level(option, i_level)

    def add_value(self, option, value):
        self.values[option]["values"].append(value)

    def remove_value(self, option):
        self.values[option]["values"].pop()

    def alter_level(self, option, level):
        old_level = self.values[option]["level"]
        self.name_page.move_between_levels(option, old_level, level)
        self.values[option]["level"] = level

    def get_option_class(self, option):
        return self.options[option].__class__ 

    def __set_properties(self, options):
        self.select_page.build_tree(options)
        self.SetPageSize((700, 400))

    def __do_layout(self):
        pass

    def get_calc_dir(self):
        calc_dir = None
        dlg = wx.DirDialog(self, message="Select root directory for calculations", style=wx.DD_NEW_DIR_BUTTON)
        if dlg.ShowModal() == wx.ID_OK:
            calc_dir = dlg.GetPath()
        dlg.Destroy()
        return calc_dir

    def check_changes(self):
        changes = []
        n_levels = max([option['level'] for option in self.values.values()])
        for i_level in range(1, n_levels+1):
            options_level = {option: values['values'] for (option, values) in self.values.iteritems()
                             if self.values[option]["level"] == i_level}
            if any([len(v) == 0 for v in options_level.values()]):
                wx.MessageBox("No values given for some of chosen FDF options!", style=wx.ICON_WARNING)
                return None
            changes.append(options_level)
        return changes

    def dir_names(self, changes, i_level):
        changes_level = changes[0]
        dir_title = self.name_page.dir_title(i_level)
        if dir_title == "Ordinal numbers":
            for i in range(1, len(changes_level.values()[0])+1):
                yield str(i)
        else:
            for value in changes_level[dir_title]:
                yield str(value.GetValue())

    def export_FDF(self, options, calc_dir, changes, i_level=1):
        """ Main recursive function for exporting FDFs
        :param options:
        :param calc_dir: A root calculation directory (string)
        :param changes: A list with value changes
        :param i_level: Level number (default is 1)
        :return: Error code (0 is OK)
        """
        if len(changes) == 0:
            # we are in the leaf
            os.makedirs(calc_dir)
            with open(os.path.join(calc_dir, 'CALC.fdf'), 'w') as f:
                for k, v in options.iteritems():
                    if v.IsEnabled():
                        f.write("%s\n" % (v.FDF_string(k),))
                f.write(self.extra)
        else:
            changes_level = changes[0]
            fdf_lines = changes_level.keys()
            fdf_values = [changes_level[key] for key in fdf_lines]
            fdf_values = [dict(zip(fdf_lines, v)) for v in zip(*fdf_values)]
            for (dir_name, fdf_value) in zip(self.dir_names(changes, i_level), fdf_values):
                options.update(fdf_value)
                self.export_FDF(options, os.path.join(calc_dir, dir_name), changes[1:], i_level+1)

    def run(self):
        if self.RunWizard(self.select_page):
            calc_dir = self.get_calc_dir()
            if calc_dir is None:
                return None
            changes = self.check_changes()
            self.export_FDF(self.options, calc_dir, changes)

if __name__ == '__main__':
    "A simple test"
    app = wx.App()
    dlg = BatchWizard(None, -1)
    app.SetTopWindow(dlg)
    dlg.run()
    app.MainLoop()
    dlg.Destroy()
