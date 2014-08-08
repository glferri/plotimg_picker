#!/usr/bin/env python
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


Load image, 
@author: Gianluca Ferri

Something from:
Noah Spurrier 2007

'''


#TODO: add y error
#TODO: show recorded data
#TODO: handle window resize (at least make it unresizable)
#TODO: use states

import Tkinter
from PIL import Image, ImageTk
import newseriesdialog
import tkFileDialog
import tkMessageBox
import os
import picture_data_picker
from os.path import expanduser

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


STARTING_VAL = -1
IMSCALE = 0.7
imgrows = 70
#todo:make these relative to system
maxheight = 600
maxwidth = 900

class ImagePicker(object):
    
    def __init__(self,fname = None):
        self.f = fname
        
        homedir = expanduser("~")
        self.settingsfname = os.path.join(homedir, ".picker_settings.cfg")
        #todo use ConfigParser
        if os.path.exists(self.settingsfname):
            try:
                setfile = open(self.settingsfname,'r')
                searchdir = setfile.readline().strip()
                if os.path.exists(searchdir):
                    self.searchdir = searchdir
                else:
                    self.searchdir  = homedir
                writedir = setfile.readline().strip()
                if os.path.exists(searchdir):
                    self.writedir = writedir
                else:
                    self.writedir   = homedir
            except:
                pass
            setfile.close()
             
        else:
            self.searchdir  = homedir
            self.writedir   = homedir
            
        self.next_is_error = 0
        
        self.x0 = STARTING_VAL
        self.x1 = STARTING_VAL
        self.xdelta = 7.
        self.x0val = 1.
        
        self.y0 = STARTING_VAL
        self.y1 = STARTING_VAL
        self.ydelta = 5.
        self.y0val = 0.

        self.series = {}  
        self.series_stack = []      
        
        self.root = Tkinter.Tk()
        self.root.bind("<Button>", self.h_click)
        #root.geometry('+%d+%d' % (100,100))
        self.root.protocol("WM_DELETE_WINDOW", self.h_before_quit)
        
        self.label_image = Tkinter.Label(self.root)
        self.label_image.grid(rowspan=imgrows,column=0)
        if self.f:
            self.openImage()
               
        self.button_done = Tkinter.Button(self.root, text="DONE", command=self.h_button_done,
                                          state=Tkinter.DISABLED)
        self.button_done.grid(column=1, row=0)
        #self.button_done.pack()
              
        self.button_undo = Tkinter.Button(self.root, text="Undo", command=self.h_button_undo)
        self.button_undo.grid(column=1, row=1)
        #self.button_undo.pack()
        
        self.button_new_series = Tkinter.Button(self.root, text="Add Series",
                                                command=self.addSeries, state=Tkinter.DISABLED)
        self.button_new_series.grid(column=1, row=2)
        #self.button_undo.pack()      
        
        self.button_reset = Tkinter.Button(self.root, text="Reset", command=self.h_reset)
        self.button_reset.grid(column=1, row=3)
        #self.button_undo.pack()   
        
        
        self.xdelta_label = Tkinter.Label(self.root, text='xdelta')
        self.xdelta_label.grid(column=1, row=4)
                     
        self.xdelta_entry = Tkinter.Entry(self.root)
        self.xdelta_entry.grid(column=1, row=5)
        self.xdelta_entry.insert(0, self.xdelta)
        
        
        self.x0val_label = Tkinter.Label(self.root, text='x0 value')
        self.x0val_label.grid(column=1, row=6)
              
      
        self.x0val_entry = Tkinter.Entry(self.root)
        self.x0val_entry.grid(column=1, row=7)
        self.x0val_entry.insert(0, self.x0val)
        
        self.ydelta_label = Tkinter.Label(self.root, text='ydelta')
        self.ydelta_label.grid(column=1, row=8)
               
        self.ydelta_entry = Tkinter.Entry(self.root)
        self.ydelta_entry.grid(column=1, row=9)
        self.ydelta_entry.insert(0, self.ydelta)
        
        self.y0val_label = Tkinter.Label(self.root, text='y0 value')
        self.y0val_label.grid(column=1, row=10)
                
        self.y0val_entry = Tkinter.Entry(self.root)
        self.y0val_entry.grid(column=1, row=11)
        self.y0val_entry.insert(0, self.y0val)
        
        ############## ERROR HANDLING ###############
        self.with_error = Tkinter.IntVar()
        self.with_error.set(0)
        self.with_error_checkbutton = Tkinter.Checkbutton(self.root, text="Enter error", variable=self.with_error)
        self.with_error_checkbutton.grid(column=1, row = 12)
        #############################################
        
        
        self.status_text = Tkinter.StringVar()
        self.status_text.set("Select x0")
        self.label_state = Tkinter.Label(self.root, textvariable=self.status_text,
                                         bd=1, relief=Tkinter.SUNKEN, anchor=Tkinter.W)
        #self.label_state.pack()
        self.label_state.grid(column=0, row=imgrows+1)
        
        self.x0_text = Tkinter.StringVar()
        self.x0_text.set("x0:       ")
        self.label_x0 = Tkinter.Label(self.root, textvariable=self.x0_text)
        self.label_x0.grid(column=2, row=0)
        
        self.x1_text = Tkinter.StringVar()
        self.x1_text.set("x1:       ")
        self.label_x1 = Tkinter.Label(self.root, textvariable=self.x1_text)
        self.label_x1.grid(column=2, row=1)
        
        self.y0_text = Tkinter.StringVar()
        self.y0_text.set("y0:       ")
        self.label_y0 = Tkinter.Label(self.root, textvariable=self.y0_text)
        self.label_y0.grid(column=2,row=2)
        
        self.y1_text = Tkinter.StringVar()
        self.y1_text.set("y1:       ")
        self.label_y1 = Tkinter.Label(self.root, textvariable=self.y1_text)
        self.label_y1.grid(column=2,row=3)
        

        ###########################
        #      MENU
        ###########################
        
        menubar = Tkinter.Menu(self.root)

        # create a pulldown menu, and add it to the menu bar
        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Open", command=self.h_open_file)
        #filemenu.add_command(label="Save", command=hello)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.h_before_quit)
        
        menubar.add_cascade(label="File", menu=filemenu)
        
        # create more pulldown menus
#        editmenu = Menu(menubar, tearoff=0)
#        editmenu.add_command(label="Cut", command=hello)
#        editmenu.add_command(label="Copy", command=hello)
#        editmenu.add_command(label="Paste", command=hello)
#        menubar.add_cascade(label="Edit", menu=editmenu)
        
#        helpmenu = Menu(menubar, tearoff=0)
#        helpmenu.add_command(label="About", command=hello)
#        menubar.add_cascade(label="Help", menu=helpmenu)
        
        # display the menu
        self.root.config(menu=menubar)
        if self.f:
            self.root.title(self.f)
        self.root.update()

    def h_click(self,event):
        if not event.widget == self.label_image:
            return
        
        if self.x0 <0:
            self.x0 = event.x
            self.status_text.set("select x1")
            self.x0_text.set("x0: %d" % self.x0)
            
        elif self.x1 < 0:
            self.x1 = event.x
            self.status_text.set("select y0")
            self.x1_text.set("x1: %d" % self.x1)
            
        elif self.y0 < 0:
            self.y0 = event.y
            self.status_text.set("select y1")
            self.y0_text.set("y0: %d" % self.y0)
            
        elif self.y1 < 0:
            self.y1 = event.y
            self.status_text.set("add point")
            self.y1_text.set("y1: %d" % self.y1)
            self.addSeries()
                       
        else:
            if not self.next_is_error:
                self.series[self.series_stack[-1]].append((event.x, event.y))
                
            if self.with_error.get():
                if self.next_is_error:  
                    temptriplet = list(self.series[self.series_stack[-1]].pop())
                    temptriplet.append(event.y)
                    self.series[self.series_stack[-1]].append(tuple(temptriplet))
                    self.status_text.set("add point")
                else:
                    self.status_text.set("pick lower end of error bar for last inserted point")
                self.next_is_error = not self.next_is_error;
                
            
            
            
            self.button_new_series.configure(state=Tkinter.NORMAL)
            self.button_new_series.update_idletasks()
            self.button_done.configure(state=Tkinter.NORMAL)
            self.button_done.update_idletasks()
        
        print self.series

    def h_button_done(self):
        self.xdelta = float(self.xdelta_entry.get())
        self.x0val  = float(self.x0val_entry.get())
        self.ydelta = float(self.ydelta_entry.get())
        self.y0val  = float(self.y0val_entry.get())
        print self.xdelta, self.x0val, self.ydelta, self.y0val
        
        pictransformer = picture_data_picker.PictureDataPicker(
                        self.x0, self.x1, self.xdelta,
                        self.y0, self.y1, self.ydelta,
                        self.x0val, self.y0val)    
        #transform to plot coordinates
        self.transformed = {}
        for k,v in self.series.iteritems():
            if len(v[0]) == 2:
                print 'before transformation'
                print [(x,y) for x,y in v]
                print 'after transformation'
                self.transformed[k]=[pictransformer.getXY(x,y) for x,y in v]
                print self.transformed[k]
            else:
                print 'before transformation'
                print [(x,y,yerr) for x,y,yerr in v]
                print 'after transformation'
                self.transformed[k]=[pictransformer.getXYErr(x,y,yerr) for x,y,yerr in v]
                print self.transformed[k]
            
        self.plotseries()
        
        #TODO: choose filename with dialog
        self.saveseries()
        #clear series data
        self.series_stack = []
        self.series = {}
        print "DONE"
                
                

    def plotseries(self):
        
        plotroot = Tkinter.Toplevel()
        iformat = 0
        colors = ['r','g','b','m']
        markers = ['s','o','^','+']
        
        f = Figure()#Figure(figsize=(5,4), dpi=100)
        a = f.add_subplot(111)
        #a.set_autoscale_on(True)
        seriesplots = []
        seriesnames = []
        for k,v in self.transformed.iteritems():
            if len(v[0]) == 2:
                plot = a.scatter([x for (x,y) in v], [y for (x,y) in v],
                               c = colors[iformat%len(colors)],
                               marker = markers[iformat%len(markers)],
                               label = k)
            else:
                a.errorbar([x for (x,y,yerr) in v], [y for (x,y,yerr) in v],
                                  [yerr for (x,y,yerr) in v], fmt = None, c='k',
                                  marker = None)
                plot = a.scatter([x for (x,y,yerr) in v], [y for (x,y,yerr) in v],
                               c = colors[iformat%len(colors)],
                               marker = markers[iformat%len(markers)],
                               label = k)
                
            a.hold(True)
            iformat += 1
            seriesplots.append(plot)
            seriesnames.append(k)
        a.legend(seriesplots,seriesnames)
        #a.set_xlabel(r"$\sigma S$")
        a.grid()
        a.hold(False)        
        
        canvas = FigureCanvasTkAgg(f,master=plotroot)
        canvas.show()
        canvas.get_tk_widget().pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

        toolbar = NavigationToolbar2TkAgg( canvas, plotroot )
        toolbar.update()
        canvas._tkcanvas.pack(side=Tkinter.TOP, fill=Tkinter.BOTH, expand=1)

        
            
        #TODO: save series data
            
    def saveseries(self):
        wfname = tkFileDialog.asksaveasfilename(initialdir=self.writedir)
        if wfname:
            self.writedir = os.path.dirname(wfname)
            f = open(wfname,"w")
            format = ""
            for k,v in self.transformed.iteritems():
                f.write(k + "\n")
                #write x
                if len(v[0]) == 2:
                    f.write(str([x for (x,y) in v]) + "\n")
                    f.write(str([y for (x,y) in v]) + "\n")
                else:
                    f.write(str([x for (x,y,yerr) in v]) + "\n")
                    f.write(str([y for (x,y,yerr) in v]) + "\n")
                    f.write(str([yerr for (x,y,yerr) in v]) + "\n")
                    
            
            

    def h_button_undo(self):
        if len(self.series_stack) > 0 and len(self.series[self.series_stack[-1]]) > 0:
            #we just remove last inserted, no matter if error or point was the last addition
            self.next_is_error = 0
            self.status_text.set("add point")
            
            #remove point
            self.series[self.series_stack[-1]].pop()
            if len(self.series[self.series_stack[-1]]) == 0:
                self.series.pop(self.series_stack.pop())            
                if len(self.series) == 0:
                    self.button_new_series.configure(state=Tkinter.DISABLED)
                    self.button_new_series.update_idletasks()
                    self.button_done.configure(state=Tkinter.DISABLED)
                    self.button_done.update_idletasks()
        elif self.y1 > STARTING_VAL:
            self.y1 = STARTING_VAL
            self.status_text.set("select y1")
            self.y1_text.set("y1:       ")
        elif self.y0 > STARTING_VAL:
            self.y0 = STARTING_VAL
            self.status_text.set("select y0")
            self.y0_text.set("y0:       ")
        elif self.x1 > STARTING_VAL:
            self.x1 = STARTING_VAL
            self.status_text.set("select x1")
            self.x1_text.set("x1:       ")
        elif self.x0 > STARTING_VAL:
            self.x0 = STARTING_VAL
            self.status_text.set("select x0")
            self.x0_text.set("x0:       ")
        else:
            pass
        
        print self.series
    
    def h_open_file(self):
        self.f = tkFileDialog.askopenfilename(initialdir=self.searchdir)
        self.searchdir = os.path.dirname(self.f)
        self.openImage()
        self.h_reset()
        
    def h_reset(self):
        self.x0 = STARTING_VAL
        self.x0_text.set("x0:       ")
        self.x1 = STARTING_VAL
        self.x1_text.set("x1:       ")
        self.y0 = STARTING_VAL
        self.y0_text.set("y0:       ")
        self.y1 = STARTING_VAL
        self.y1_text.set("y1:       ")
        
        self.status_text.set("select x0")
        
        self.button_new_series.configure(state=Tkinter.DISABLED)
        self.button_new_series.update_idletasks()
        self.button_done.configure(state=Tkinter.DISABLED)
        self.button_done.update_idletasks()
        
        self.series_stack = []
        self.series = {}
        self.measuredsets = {}
    
    def h_before_quit(self):
        if tkMessageBox.askokcancel("Quit?", "Are you sure you want to quit?"):
            setfile = open(self.settingsfname,'w')
            setfile.write(self.searchdir + "\n")
            setfile.write(self.writedir + "\n")
            self.root.quit()    
    
    def addSeries(self):
        dialog = newseriesdialog.NewSeriesDialog(self.root, self.series.keys())
        if (dialog.result):
            self.series_stack.append(dialog.result)
            self.series[dialog.result] = []
            
    def openImage(self):
        image1 = Image.open(self.f)
        
        xratio = float(maxwidth)/image1.size[0]
        yratio = float(maxheight)/image1.size[1]
        
        imscale = min(xratio,yratio)
        image1 = image1.resize(
                (int(imscale*image1.size[0]),int(imscale*image1.size[1])),
                Image.ANTIALIAS)
        #root.geometry('%dx%d' % (image1.size[0],image1.size[1]))
        self.tkpi = ImageTk.PhotoImage(image1)
        self.label_image.configure(image=self.tkpi)
        #label_image.place(x=0,y=0,width=image1.size[0],height=image1.size[1])
        #self.label_image.pack()
        self.label_image.update_idletasks()
        self.root.title(self.f)
        
        
def main():
    ip = ImagePicker()
    Tkinter.mainloop() # wait until user clicks the window
    
if __name__ == '__main__':
    main()
