'''
Created on 15/feb/2011

@author: subbuglio
'''
import tkSimpleDialog
import Tkinter


class NewSeriesDialog(tkSimpleDialog.Dialog):
    
    def __init__(self, master, keys, title = None):
        self.keys = keys
        tkSimpleDialog.Dialog.__init__(self, master, title)
        
    def body(self, master):
        Tkinter.Label(master, text="New series name:").pack()

        self.e1 = Tkinter.Entry(master)
        self.e1.pack()
        return self.e1 # initial focus

    def apply(self):
        self.result = self.e1.get().strip()
        
    def validate(self):
        val = self.e1.get().strip()
        if not val or val in self.keys:
            return 0
        else:
            return 1
        