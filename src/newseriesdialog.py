'''
Copyright 2011,2014 Gianluca Ferri 

This file is part of plotimg_picker.

plotimg_picker is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Nome-Programma is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Nome-Programma.  If not, see <http://www.gnu.org/licenses/>.
'''



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
        