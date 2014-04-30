from collections import OrderedDict
import wx
from wx.wizard import Wizard, WizardPageSimple
from batch_pages import SelectPage, FillInPage, DirHierarchyPage

class BatchWizard(Wizard):

    def __init__(self, *args, **kwds):
        options = kwds.pop('options', None)
        self.options = self.make_options_dict(options)
        
        Wizard.__init__(self, *args, **kwds)
        self.select_page = SelectPage(self)
        self.fillin_page = FillInPage(self)
        self.dh_page = DirHierarchyPage(self)
        WizardPageSimple.Chain(self.select_page, self.fillin_page)
        WizardPageSimple.Chain(self.fillin_page, self.dh_page)
        self.__set_properties(options)
        self.__do_layout()

    def make_options_dict(self, options):
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
        self.fillin_page.add_FDF_option(option)
        self.dh_page.add_FDF_option(option)


    def remove_FDF_option(self, option):
        self.fillin_page.remove_FDF_option(option)
        self.dh_page.remove_FDF_option(option)

    def get_option_class(self, option):
        return self.options[option].__class__ 

    def __set_properties(self, options):
        self.select_page.build_tree(options)
        self.SetPageSize((700, 400))

    def __do_layout(self):
        pass


    def run(self):
        self.RunWizard(self.select_page)

if __name__ == '__main__':
    'A simple test'
    app = wx.App()
    dlg = BatchWizard(None, -1)
    app.SetTopWindow(dlg)
    dlg.run()
    app.MainLoop()
    dlg.Destroy()