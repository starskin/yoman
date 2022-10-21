# IMPORT PACKAGES
import tkinter as tk
import datetime
from sys import platform
import os
import xml.etree.ElementTree as ET


# CONSTANTS
_VERSION = 0.1
_BBG = 'black'
_BG = '#454545'
_FG = '#696969'
_FONT_SMALL = ('Bahnschrift',9)
_FONT = ('Bahnschrift',11)
_FONT_BIG = ('Bahnschrift',13)
_FONT_COLOR = 'white'
journalDirPath = 'journals'


# CLASSES AND FUNCTIONS
class MainWindow(tk.Tk):
    def __init__(self,dirPath=''):
        super().__init__()
        self.title('Yoman')
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.topFrame = TopFrame(master=self,dirPath=dirPath)
        self.grid()
        self.protocol("WM_DELETE_WINDOW",self.onClosing)

    def onClosing(self): # function for window closing
        if self.topFrame.entryFrame.entryText.textIsModified == True: # check if there are unsaved entry changes
            popup = SavePopup(self)
            choice = popup.show()
            if choice == True:
                self.topFrame.entryFrame.saveEntry()
        self.destroy()

class TopFrame(tk.Frame):
    def __init__(self,master=None,dirPath=''):
        self.master = master
        self.dirPath = dirPath
        super().__init__(master=self.master,bg=_BBG)
        self.columnconfigure(1,weight=1)
        self.rowconfigure(0,weight=1)

        self.currentDate = datetime.date.today()
        self.currentYearVar = tk.IntVar()
        self.currentYearVar.set(self.currentDate.year)
        self.currentDateStringVar = tk.StringVar()
        self.currentDateStringVar.set(self.currentDate.strftime("%A, %B %d, %Y").replace(' 0',' '))

        self.drawFrames()
        self.updateEntryList()
        self.grid(sticky='nsew')

    def drawFrames(self):
        # List frame
        self.listFrame = ListFrame(master=self)
        self.listFrame.grid(row=0,column=0,padx=3,pady=3,sticky='nsew')

        # Entry frame
        self.entryFrame = EntryFrame(master=self)
        self.entryFrame.grid(row=0,column=1,padx=3,pady=3,sticky='nsew')

    def updateEntryList(self):
        year = self.currentYearVar.get()
        self.listFrame.clearEntryList()
        if (checkJournalDir(self.dirPath) == True) and (checkJournalFile(self.dirPath,year) == True):
            journal = parseJournalFile(journalDirPath,year)
            for month in reversed(journal):
                for day in reversed(journal[month]):
                    entryDate = datetime.date(year,int(month),int(day))
                    self.listFrame.addEntryListing(entryDate)

    def changeSelectedEntry(self,entryDate):
        if self.entryFrame.entryText.textIsModified == True: # check if there are unsaved entry changes
            popup = SavePopup(self)
            choice = popup.show()
            if choice == True: # if user wants to save entry changes
                self.entryFrame.saveEntry()
            self.entryFrame.entryText.textIsModified = False
            self.entryFrame.saveButton.grid_remove()
        self.currentDate = entryDate
        self.entryFrame.entryText.overrideModified = True
        self.entryFrame.entryText.delete("1.0",tk.END)
        entryText = parseJournalFile(self.dirPath,entryDate.year,entryDate.month,entryDate.day)
        self.entryFrame.entryText.insert("1.0",entryText)
        self.entryFrame.entryText.startingText = entryText
        self.currentDateStringVar.set(self.currentDate.strftime("%A, %B %d, %Y").replace(' 0',' '))

class ListFrame(tk.Frame):
    def __init__(self,master=None):
        self.master = master
        super().__init__(master=self.master,bg=_BG)

        self.yearSelectorFrame = tk.Frame(master=self,bg=_BG)
        self.yearSelectorFrame.grid(row=0,sticky='ew')

        self.yearLabel = tk.Label(master=self.yearSelectorFrame,bg=_BG,font=_FONT,fg=_FONT_COLOR,textvariable=self.master.currentYearVar,width=5)
        self.yearLabel.grid(row=0,column=1,padx=5,sticky='ew')

        self.prevYearButton = tk.Button(master=self.yearSelectorFrame,text='<',bg=_BG,font=_FONT,fg=_FONT_COLOR,pady=0,relief=tk.FLAT,overrelief=tk.GROOVE,command=self.prevYear)
        self.prevYearButton.grid(row=0,padx=5,column=0)

        self.nextYearButton = tk.Button(master=self.yearSelectorFrame,text='>',bg=_BG,font=_FONT,fg=_FONT_COLOR,pady=0,relief=tk.FLAT,overrelief=tk.GROOVE,command=self.nextYear)
        self.nextYearButton.grid(row=0,padx=5,column=2)

        self.entryListFrame = tk.Frame(master=self,bg=_BG)
        self.entryListFrame.grid(row=1,sticky='nsew')
        self.entryListFrame.columnconfigure(0,weight=1)

    def addEntryListing(self,entryDate):
        button = EntryListButton(master=self.entryListFrame,date=entryDate)
        button.grid(column=0,sticky='ew',padx=5,pady=3)

    def clearEntryList(self):
        entryObjectList = self.entryListFrame.winfo_children()
        for entryWidget in entryObjectList:
            entryWidget.destroy()

    def prevYear(self):
        yearInt = self.master.currentYearVar.get() - 1
        self.master.currentYearVar.set(yearInt)
        self.master.updateEntryList()

    def nextYear(self):
        yearInt = self.master.currentYearVar.get() + 1
        self.master.currentYearVar.set(yearInt)
        self.master.updateEntryList()

class EntryListButton(tk.Button):
    def __init__(self,master=None,date=None):
        self.date = date
        super().__init__(master=master,
                        text=date.strftime("%B %d").replace(' 0',' '),
                        relief=tk.FLAT,
                        anchor=tk.W,
                        bg=_FG,
                        fg=_FONT_COLOR,
                        font=_FONT,
                        command=lambda:self.master.master.master.changeSelectedEntry(date))

class EntryFrame(tk.Frame):
    def __init__(self,master=None):
        self.master = master
        super().__init__(master=self.master,bg=_BG)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(2,weight=1)

        self.entryBanner = tk.Frame(master=self,bg=_BG)
        self.entryBanner.grid(row=0,padx=10,pady=3,sticky='ew')
        self.entryBanner.columnconfigure(0,weight=1)

        self.entryDate = tk.Label(master=self.entryBanner,anchor=tk.W,bg=_BG,fg=_FONT_COLOR,font=_FONT_BIG,textvariable=self.master.currentDateStringVar)
        self.entryDate.grid(row=0,column=0,sticky='ew')

        self.saveButton = tk.Button(master=self.entryBanner,relief=tk.FLAT,bg=_FG,fg=_FONT_COLOR,font=_FONT_SMALL,overrelief=tk.GROOVE,pady=0,text="Save Entry",command=self.saveEntry)

        self.entrySeparator = tk.Frame(master=self,height=1,bg=_FG)
        self.entrySeparator.grid(row=1,padx=10,sticky='ew')

        # Entry text frame
        self.entryTextFrame = tk.Frame(master=self)
        self.entryTextFrame.columnconfigure(0,weight=1)
        self.entryTextFrame.rowconfigure(0,weight=1)
        self.entryTextFrame.grid(row=2,padx=10,pady=3,sticky='nsew')

        self.scrollbar = AutoHideScrollBar(master=self.entryTextFrame)
        self.scrollbar.grid(column=1,sticky='ns')

        self.entryText = EntryTextBox(master=self.entryTextFrame,scroll=self.scrollbar)
        self.scrollbar.config(command=self.entryText.yview) # scrollbar changes text view
        currentDate = self.master.currentDate
        existingEntryText = parseJournalFile(self.master.dirPath,currentDate.year,currentDate.month,currentDate.day)
        if existingEntryText != False:
            self.entryText.overrideModified = True
            self.entryText.insert("1.0",existingEntryText)
        self.entryText.grid(row=0,column=0,sticky='nsew')
        self.entryText.focus_set() # set entry text box as active on start

    def saveEntry(self):
        date = self.master.currentDate
        entryText = self.entryText.get("1.0","end-1c") # "end-1c" does not include final newline character
        if len(entryText) != 0: # ensures empty entries are not saved; might be unnecessary
            saveJournalEntry(self.master.dirPath,date.year,date.month,date.day,entryText)
            self.master.updateEntryList()
            self.saveButton.grid_remove()
            self.entryText.startingText = entryText

class EntryTextBox(tk.Text):
    def __init__(self,master=None,scroll=None):
        super().__init__(master=master,
                        bg=_BG,
                        fg=_FONT_COLOR,
                        font=_FONT,
                        wrap=tk.WORD,
                        relief=tk.FLAT,
                        insertbackground=_FONT_COLOR,
                        insertontime=750,
                        insertofftime=500,
                        insertwidth=1,
                        spacing2=1,
                        selectbackground=_FG,
                        exportselection=0)
        if not scroll == None:
            self.config(yscrollcommand = scroll.set) # text view changes scrollbar
        self.resettingModified = False
        self.overrideModified = False
        self.textIsModified = False
        self.startingText = ''
        self.bind('<<Modified>>',self.textModifiedCallback)

    def textModifiedCallback(self,event): # prevents edit_modified(False) from triggering modified callback
        if self.resettingModified == True:
            self.resettingModified = False
            return
        self.resettingModified = True
        self.edit_modified(False)
        if self.overrideModified:
            self.overrideModified = False
            return
        self.textModified()

    def textModified(self): # modified callback
        entryText = self.get("1.0","end-1c")
        if (len(entryText) != 0) and (self.startingText != entryText):
            self.textIsModified = True
            self.master.master.saveButton.grid(row=0,column=1,sticky='e')
        else:
            self.textIsModified = False
            self.master.master.saveButton.grid_remove()

class AutoHideScrollBar(tk.Scrollbar):
    def set(self,first,last):
        if (float(first) <= 0.0) and (float(last) >= 1.0):
            self.grid_remove()
        else:
            self.grid()
        tk.Scrollbar.set(self,first,last)

class SavePopup(tk.Toplevel):
    def __init__(self,master=None):
        super().__init__(master=master)
        self.title("Save Entry?")
        self.resizable(False,False)
        self.transient(self.master.master)

        self.choice = None
        self.popupFrame = tk.Frame(self,bg=_BG)

        label = tk.Label(self.popupFrame,bg=_BG,fg=_FONT_COLOR,font=_FONT_SMALL,text="The current entry has unsaved changes.\nDo you want to save these changes?")
        label.grid(column=0,row=0)

        buttonFrame = tk.Frame(self.popupFrame,bg=_BG)
        buttonFrame.grid(column=0,row=1)

        saveButton = tk.Button(buttonFrame,bg=_FG,fg=_FONT_COLOR,font=_FONT_SMALL,relief=tk.FLAT,overrelief=tk.GROOVE,text="Save",command=lambda:self.choiceSelected(True))
        saveButton.grid(column=0,row=0,padx=15,pady=3)

        dontSaveButton = tk.Button(buttonFrame,bg=_FG,fg=_FONT_COLOR,font=_FONT_SMALL,relief=tk.FLAT,overrelief=tk.GROOVE,text="Don't Save",command=lambda:self.choiceSelected(False))
        dontSaveButton.grid(column=1,row=0,padx=15,pady=3)

    def choiceSelected(self,choice):
        self.choice = choice
        self.grab_release() # enable interaction with main window
        self.destroy()

    def show(self):
        self.popupFrame.grid()
        self.protocol("WM_DELETE_WINDOW",lambda:self.choiceSelected(False)) # if user closes popup
        self.grab_set() # disable interaction with main window once focus is set
        self.focus()
        self.wait_window() # wait for popup window to be closed
        return self.choice

def checkJournalDir(dirPath):
    if dirPath in os.listdir():
        return True
    else:
        return False

def checkJournalFile(dirPath,year):
    if (str(year) + '.xml') in os.listdir(dirPath):
        return True
    else:
        return False

def createJournalFile(dirPath,year):
    journal = ET.Element('journal', attrib={'year':str(year)})
    journalTree = ET.ElementTree(journal)
    ET.indent(journalTree,space='    ')
    journalPath = os.path.join(dirPath,str(year) + '.xml')
    journalTree.write(journalPath,encoding='utf-8',xml_declaration=True)

def parseJournalFile(dirPath,year,targetMonth=None,targetDay=None):
    journalPath = os.path.join(dirPath,str(year) + '.xml')
    try:
        journalTree = ET.parse(journalPath)
    except FileNotFoundError:
        return False
    journalRoot = journalTree.getroot()
    journal = {}
    for month in journalRoot:
        monthNum = int(month.attrib['mon'])
        monthLog = {}
        for entry in month:
            dayNum = int(entry.attrib['day'])
            monthLog[dayNum] = entry.text
        journal[monthNum] = monthLog
    if targetMonth is not None: # if asked for specific month
        if targetDay is not None: # if asked for specific day
            try:
                return journal[targetMonth][targetDay]
            except KeyError:
                return False
        try:
            return journalMonth
        except KeyError:
            return False
    return journal

def saveJournalEntry(dirPath,year,month,day,entry):
    if checkJournalDir(dirPath) == False: # create journal directory if necessary
        os.mkdir(dirPath)
    if checkJournalFile(dirPath,year) == False: # create journal file if necessary
        createJournalFile(dirPath,year)

    journalPath = os.path.join(dirPath,str(year) + '.xml')
    journalTree = ET.parse(journalPath)
    journalRoot = journalTree.getroot()

    # check if month element exists
    listedMonths = []
    for monthElement in journalRoot:
        listedMonths.append(int(monthElement.get('mon')))
    if month not in listedMonths: # create month element if necessary
        monthElement = ET.Element('month', attrib={'mon':str(month)})
        journalRoot.append(monthElement)

    # check if entry element exists
    listedDays = []
    entriesFindString = "./*[@mon='" + str(month) + "']/entry"
    for entryElement in journalRoot.findall(entriesFindString):
        listedDays.append(int(entryElement.get('day')))
    if day not in listedDays: # create entry element if necessary
        monthFindString = "./*[@mon='" + str(month) + "']"
        monthElement = journalRoot.find(monthFindString)
        entryElement = ET.Element('entry', attrib={'day':str(day)})
        monthElement.append(entryElement)

    # save text to entry element
    entryFindString = "./*[@mon='" + str(month) + "']/*[@day='" + str(day) + "']"
    entryElement = journalRoot.find(entryFindString)
    entryElement.text = entry

    # write journal file
    ET.indent(journalTree,space='    ')
    journalPath = os.path.join(dirPath,str(year) + '.xml')
    journalTree.write(journalPath,encoding='utf-8',xml_declaration=True)


# SCRIPT
if __name__ == '__main__':
    if platform == 'win32':
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1) # fix blurry text in Windows

    app = MainWindow(dirPath=journalDirPath)
    app.mainloop()
