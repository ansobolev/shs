from collections import OrderedDict
import wx
from wx.wizard import Wizard, WizardPageSimple
from batch_pages import SelectPage, FillInPage, DirHierarchyPage, DirNamePage


class BatchWizard(Wizard):

    def __init__(self, *args, **kwds):
        options = kwds.pop('options', None)
        self.values = {}
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

    def prepare_calc_dirs(self):
        calc_dir = None
        dlg = wx.DirDialog(self, message="Select root directory for calculations")
        if dlg.ShowModal() == wx.ID_OK:
            calc_dir = dlg.GetPath()
        dlg.Destroy()
        if calc_dir is None:
            return


    def run(self):
        if self.RunWizard(self.select_page):
            self.prepare_calc_dirs()


if __name__ == '__main__':
    "A simple test"
    app = wx.App()
    dlg = BatchWizard(None, -1)
    app.SetTopWindow(dlg)
    dlg.run()
    app.MainLoop()
    dlg.Destroy()