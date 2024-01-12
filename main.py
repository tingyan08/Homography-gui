from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import os
import glob
import random

# colors for the bboxes
COLORS = ['red', 'blue', 'pink', 'cyan', 'green', 'black']
# image sizes for the examples
SIZE = 256, 256

class HomographyTool():
    def __init__(self, master):
        # set up the main frame
        self.parent = master
        self.parent.title("HomographyTool")
        self.frame = Frame(self.parent)
        self.frame.columnconfigure(0, weight=47)
        self.frame.columnconfigure(1, weight=45)
        self.frame.columnconfigure(2, weight=4)
        self.frame.columnconfigure(3, weight=4)
        

        self.frame.rowconfigure(2, weight=4)
        
        
        self.frame.pack(fill=BOTH, expand=1)
        self.parent.resizable(width = FALSE, height = FALSE)

        # initialize global state
        self.imageDir = ''
        self.imageList= []
        self.egDir = ''
        self.egList = []
        self.outDir = ''
        self.cur = 0
        self.total = 0
        self.category = 0
        self.imagename = ''
        self.labelfilename = ''
        self.tkimg = None
        self.currentLabelclass = ''
        self.cla_can_temp = []

        # initialize mouse state
        self.POINTS = []


        # reference to polygon
        self.polygonID = None
        self.hl = None
        self.vl = None

        # ----------------- GUI stuff ---------------------
        # dir entry & load
        # input image dir entry
        self.svSourcePath = StringVar()
        self.entrySrc = Entry(self.frame, textvariable=self.svSourcePath)
        self.entrySrc.grid(row=0, column=0, columnspan=2, padx=2, sticky=W+E)
        self.svSourcePath.set(os.path.join(os.getcwd(),"Images"))
        
        # input image dir button
        self.srcDirBtn = Button(self.frame, text="Image input folder", command=self.selectSrcDir)
        self.srcDirBtn.grid(row=0, column=2, padx=2, sticky=W+E)
        
        # load button
        self.ldBtn = Button(self.frame, text="Load Dir", command=self.loadDir)
        self.ldBtn.grid(row=0, column=3, rowspan=2, padx=2, sticky=W+E+N+S)
        
        # label file save dir entry
        self.svDestinationPath = StringVar()
        self.entryDes = Entry(self.frame, textvariable=self.svDestinationPath)
        self.entryDes.grid(row=1, column=0, columnspan=2, padx=2, sticky=W+E)
        self.svDestinationPath.set(os.path.join(os.getcwd(),"Labels"))
        
        # label file save dir button
        self.desDirBtn = Button(self.frame, text="Output folder", command=self.selectDesDir)
        self.desDirBtn.grid(row=1, column=2, padx=2, sticky=W+E)


        # main panel for labeling
        self.mainPanel = Canvas(self.frame, cursor='tcross')
        self.mainPanel.bind("<Button-1>", self.mouseClick)
        self.mainPanel.bind("<Motion>", self.mouseMove)
        self.parent.bind("<Escape>", self.cancelPolygon)  # press <Espace> to cancel current bbox
        self.parent.bind("s", self.cancelPolygon)
        self.parent.bind("a", self.prevImage) # press 'a' to go backforward
        self.parent.bind("d", self.nextImage) # press 'd' to go forward
        self.mainPanel.grid(row = 2, column = 0, rowspan = 2, columnspan=2, sticky = W+N+E+S)
        
        # example pannel for illustration
        self.egPanel = Frame(self.frame)
        self.egPanel.grid(row = 2, column = 1, sticky = W+N+E+S)
        self.tmpLabel2 = Label(self.egPanel, text = "Results:")
        self.tmpLabel2.pack(side = TOP, pady = 5)
        self.result = Label(self.egPanel)
        self.result.pack(side = TOP)
        
        # Target Size
        self.targetPanel = Frame(self.frame)
        self.targetPanel.grid(row = 2, column = 2, columnspan = 2, sticky = W+N+E+S)
        self.targetPanel.columnconfigure(0, weight=1)
        self.targetPanel.columnconfigure(1, weight=1)
        self.targetPanel.rowconfigure(15, weight=1)
        self.lbrp = Label(self.targetPanel, text = 'Reference Points', bg='yellow')
        self.lbrp.grid(row = 0, column = 0, columnspan = 2, pady=10, sticky = W+E)
        self.lb1p1 = Label(self.targetPanel, text = 'Point 1 (Left top):')
        self.lb1p1.grid(row = 1, column = 0, columnspan = 2, sticky = W+E, pady=5)
        self.point1x = DoubleVar()
        self.entryP1x = Entry(self.targetPanel, textvariable=self.point1x).grid(row = 2, column = 0, sticky = W+E)
        self.point1y = DoubleVar()
        self.entryP1y = Entry(self.targetPanel, textvariable=self.point1y).grid(row = 2, column = 1, sticky = W+E)
        
        self.lb1p2 = Label(self.targetPanel, text = 'Point 2 (Left bottom):')
        self.lb1p2.grid(row = 3, column = 0, columnspan = 2, sticky = W+E, pady=5)
        self.point2x = DoubleVar()
        self.entryP2x = Entry(self.targetPanel, textvariable=self.point2x).grid(row = 4, column = 0, sticky = W+E)
        self.point2y = DoubleVar()
        self.entryP2y = Entry(self.targetPanel, textvariable=self.point2y).grid(row = 4, column = 1, sticky = W+E)
        
        self.lb1p3 = Label(self.targetPanel, text = 'Point 3 (Right bottom):')
        self.lb1p3.grid(row = 5, column = 0, columnspan = 2, sticky = W+E, pady=5)
        self.point3x = DoubleVar()
        self.entryP3x = Entry(self.targetPanel, textvariable=self.point3x).grid(row = 6, column = 0, sticky = W+E)
        self.point3y = DoubleVar()
        self.entryP3y = Entry(self.targetPanel, textvariable=self.point3y).grid(row = 6, column = 1, sticky = W+E)
        
        self.lb1p4 = Label(self.targetPanel, text = 'Point 4 (Right top):')
        self.lb1p4.grid(row = 7, column = 0, columnspan = 2, sticky = W+E, pady=5)
        self.point4x = DoubleVar()
        self.entryP4x = Entry(self.targetPanel, textvariable=self.point4x).grid(row = 8, column = 0, sticky = W+E)
        self.point4y = DoubleVar()
        self.entryP4y = Entry(self.targetPanel, textvariable=self.point4y).grid(row = 8, column = 1, sticky = W+E)
        
        # set default values
        self.point1x.set(0)
        self.point1y.set(0)
        self.point2x.set(0)
        self.point2y.set(800)
        self.point3x.set(750)
        self.point3y.set(800)
        self.point4x.set(800)
        self.point4y.set(0)
        
        # Drift Ratio and Cycles
        Label(self.targetPanel, text = 'Cycles', bg='yellow').grid(row = 9, column = 0, columnspan = 2, pady=10, sticky = W+E)
        self.drift = DoubleVar()
        Label(self.targetPanel, text = 'Drift Ratio (%)').grid(row = 10, column = 0, columnspan = 2, pady=5, sticky = W+E)
        Entry(self.targetPanel, textvariable=self.drift).grid(row = 11, column = 0, columnspan = 2, sticky = W+E)
        self.cycle = DoubleVar()
        Label(self.targetPanel, text = 'Cycle').grid(row = 12, column = 0, columnspan = 2, pady=5, sticky = W+E)
        Entry(self.targetPanel, textvariable=self.cycle).grid(row = 13, column = 0, columnspan = 2, sticky = W+E)

        # showing bbox info 
        self.lb1 = Label(self.targetPanel, text = 'Source Points', bg='yellow')
        self.lb1.grid(row = 14, column = 0, columnspan = 2, pady=10, sticky = W+E)
        self.listbox = Listbox(self.targetPanel)
        self.listbox.grid(row = 15, column = 0, columnspan = 2, pady=5, sticky = W+N+E+S)
        
        # delete bbox
        self.btnDel = Button(self.frame, text = 'Delete', command = self.clearPoints)
        self.btnDel.grid(row = 3, column = 2, columnspan=2, pady=5, sticky =  W+N+E+S)

        # control panel for image navigation
        self.ctrPanel = Frame(self.frame)
        self.ctrPanel.grid(row = 4, column = 0, columnspan = 4, sticky = W+E)
        self.prevBtn = Button(self.ctrPanel, text='<< Prev', width = 10, command = self.prevImage)
        self.prevBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.nextBtn = Button(self.ctrPanel, text='Next >>', width = 10, command = self.nextImage)
        self.nextBtn.pack(side = LEFT, padx = 5, pady = 3)
        self.progLabel = Label(self.ctrPanel, text = "Progress:     /    ")
        self.progLabel.pack(side = LEFT, padx = 5)
        self.tmpLabel = Label(self.ctrPanel, text = "Go to Image No.")
        self.tmpLabel.pack(side = LEFT, padx = 5)
        self.idxEntry = Entry(self.ctrPanel, width = 5)
        self.idxEntry.pack(side = LEFT)
        self.goBtn = Button(self.ctrPanel, text = 'Go', command = self.gotoImage)
        self.goBtn.pack(side = LEFT)



        # display mouse position
        self.disp = Label(self.ctrPanel, text='')
        self.disp.pack(side = RIGHT)


    def selectSrcDir(self):
        path = filedialog.askdirectory(title="Select image source folder", initialdir=self.svSourcePath.get())
        self.svSourcePath.set(path)
        return

    def selectDesDir(self):
        path = filedialog.askdirectory(title="Select label output folder", initialdir=self.svDestinationPath.get())
        self.svDestinationPath.set(path)
        return

    def loadDir(self):
        self.parent.focus()
        # get image list
        #self.imageDir = os.path.join(r'./Images', '%03d' %(self.category))
        self.imageDir = self.svSourcePath.get()
        if not os.path.isdir(self.imageDir):
            messagebox.showerror("Error!", message = "The specified dir doesn't exist!")
            return

        extlist = ["*.JPEG", "*.jpeg", "*JPG", "*.jpg", "*.PNG", "*.png", "*.BMP", "*.bmp"]
        for e in extlist:
            filelist = glob.glob(os.path.join(self.imageDir, e))
            self.imageList.extend(filelist)
        #self.imageList = glob.glob(os.path.join(self.imageDir, '*.JPEG'))
        if len(self.imageList) == 0:
            print('No .JPEG images found in the specified dir!')
            return

        # default to the 1st image in the collection
        self.cur = 1
        self.total = len(self.imageList)

        # set up output dir
        #self.outDir = os.path.join(r'./Labels', '%03d' %(self.category))
        self.outDir = self.svDestinationPath.get()
        if not os.path.exists(self.outDir):
            os.mkdir(self.outDir)
            
        self.loadImage()
        print('%d images loaded from %s' %(self.total, self.imageDir))

    def loadImage(self):
        # load image
        imagepath = self.imageList[self.cur - 1]
        self.img = Image.open(imagepath)
        size = self.img.size
        if size[0] > size[1]:
            self.img = self.img.transpose(Image.ROTATE_270)
        size = self.img.size
        self.factor = max(size[0]/1000, size[1]/1000., 1.)
        self.img = self.img.resize((int(size[0]/self.factor), int(size[1]/self.factor)))
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.mainPanel.config(width = max(self.tkimg.width(), 400), height = max(self.tkimg.height(), 400))
        self.mainPanel.create_image(0, 0, image = self.tkimg, anchor=NW)
        self.progLabel.config(text = "%04d/%04d" %(self.cur, self.total))

        # load labels
        self.clearPoints()
        #self.imagename = os.path.split(imagepath)[-1].split('.')[0]
        fullfilename = os.path.basename(imagepath)
        self.imagename, _ = os.path.splitext(fullfilename)
        labelname = self.imagename + '.txt'
        self.labelfilename = os.path.join(self.outDir, labelname)
        bbox_cnt = 0
        if os.path.exists(self.labelfilename):
            with open(self.labelfilename) as f:
                for (i, line) in enumerate(f):
                    if i == 0:
                        bbox_cnt = int(line.strip())
                        continue
                    #tmp = [int(t.strip()) for t in line.split()]
                    tmp = line.split()
                    tmp[0] = int(int(tmp[0])/self.factor)
                    tmp[1] = int(int(tmp[1])/self.factor)
                    tmp[2] = int(int(tmp[2])/self.factor)
                    tmp[3] = int(int(tmp[3])/self.factor)
                    self.bboxList.append(tuple(tmp))
                    color_index = (len(self.bboxList)-1) % len(COLORS)
                    tmpId = self.mainPanel.create_rectangle(tmp[0], tmp[1], \
                                                            tmp[2], tmp[3], \
                                                            width = 2, \
                                                            outline = COLORS[color_index])
                                                            #outline = COLORS[(len(self.bboxList)-1) % len(COLORS)])
                    self.bboxIdList.append(tmpId)
                    self.listbox.insert(END, '(%d, %d) -> (%d, %d)' %(tmp[0], tmp[1], tmp[2], tmp[3]))
                    self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[color_index])
                    #self.listbox.itemconfig(len(self.bboxIdList) - 1, fg = COLORS[(len(self.bboxIdList) - 1) % len(COLORS)])

    def saveImage(self):
        if self.labelfilename == '':
            return
        with open(self.labelfilename, 'w') as f:
            f.write('%d\n' %len(self.bboxList))
            for points in self.POINTS:
                f.write("{} {}\n".format(int(int(points[0])*self.factor), int(int(points[1])*self.factor)))
                #f.write(' '.join(map(str, bbox)) + '\n')
        print('Image No. %d saved' %(self.cur))


    def mouseClick(self, event):
        if len(self.POINTS) < 4:
            self.POINTS.append((event.x, event.y))
            self.listbox.insert(len(self.POINTS), 'Point %d: (%d, %d)' %(len(self.POINTS), self.POINTS[len(self.POINTS)-1][0], self.POINTS[len(self.POINTS)-1][1]))
        else:
            self.listbox.delete(0, len(self.POINTS))
            self.POINTS = []
            self.POINTS.append((event.x, event.y))
            self.listbox.insert(len(self.POINTS), 'Point %d: (%d, %d)' %(len(self.POINTS), self.POINTS[len(self.POINTS)-1][0], self.POINTS[len(self.POINTS)-1][1]))
            

    def mouseMove(self, event):
        self.disp.config(text = 'x: %d, y: %d' %(event.x, event.y))
        if self.tkimg:
            if self.hl:
                self.mainPanel.delete(self.hl)
            self.hl = self.mainPanel.create_line(0, event.y, self.tkimg.width(), event.y, width = 2)
            if self.vl:
                self.mainPanel.delete(self.vl)
            self.vl = self.mainPanel.create_line(event.x, 0, event.x, self.tkimg.height(), width = 2)
        if 4 > len(self.POINTS) >= 1:
            if self.polygonID:
                self.mainPanel.delete(self.polygonID)
            self.polygonID = self.mainPanel.create_polygon(self.POINTS + [(event.x, event.y)], outline='red', width=2, fill='red', stipple='gray50')

    def cancelPolygon(self, event):
        if len(self.POINTS) >= 1:
            if self.polygonID:
                self.mainPanel.delete(self.polygonID)
                self.polygonID = None
                self.clearPoints()

    def clearPoints(self):
        if self.polygonID:
            self.mainPanel.delete(self.polygonID)
        self.listbox.delete(0, len(self.POINTS))
        self.POINTS = []

    def prevImage(self, event = None):
        self.saveImage()
        if self.cur > 1:
            self.cur -= 1
            self.loadImage()

    def nextImage(self, event = None):
        self.saveImage()
        if self.cur < self.total:
            self.cur += 1
            self.loadImage()

    def gotoImage(self):
        idx = int(self.idxEntry.get())
        if 1 <= idx and idx <= self.total:
            self.saveImage()
            self.cur = idx
            self.loadImage()


if __name__ == '__main__':
    root = Tk()
    tool = HomographyTool(root)

    root.iconbitmap('lab-logo.ico')
    root.resizable(width = True, height = True)
    root.state('zoomed')
    root.mainloop()
