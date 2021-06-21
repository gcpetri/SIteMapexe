# pyqt imports
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSlot, Qt, pyqtSignal, QThread, QSemaphore

# file imports
from SiteMap.settings import Settings
from SiteMap.settingholder import SettingHolder

# python libaries
import sys
import os
from tika import parser
from zipfile import ZipFile
import simplekml
import re
from lxml import etree
import math
import time


# ============== Thread Semaphore ============ #
LOCK = QSemaphore(0)
# ============== Worker Thread =============== #

class Worker(QThread):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str)
    dir = []
    regex = r''

    def __init__(self, index, dir):
        super(Worker, self).__init__(None)
        self.dir = dir
        self.index = index
        self.global_location = os.path.dirname(os.path.realpath(__file__))
        for idx, value in enumerate(SettingHolder.regex_lines):
            self.regex += '(' + value + ')'
            if idx != len(SettingHolder.regex_lines) - 1:
                self.regex += '|'
        print(self.regex)

    def run(self):
        self.loopFolder(SettingHolder.dir, self.dir)
        self.finished.emit(self.index)

    def loopFolder(self, dirPath, dir):
        for filepath in dir:
            filePath = os.path.join(dirPath, filepath)
            if os.path.isdir(filePath):
                print('dir', filePath)
                folderContinue = len(SettingHolder.folder_includes) == 0
                for folderInc in SettingHolder.folder_includes:
                    if folderInc in filepath:
                        folderContinue = True
                for folderExc in SettingHolder.folder_excludes:
                    if folderExc in filepath:
                        folderContinue = False
                if folderContinue:
                    self.progress.emit(filePath)
                    self.loopFolder(filePath, os.listdir(filePath))
            elif os.path.isfile(filePath):
                fileContinue = len(SettingHolder.file_includes) == 0
                filename = os.path.basename(filePath)
                for fileInc in SettingHolder.file_includes:
                    if fileInc in filename:
                        fileContinue = True
                for fileExc in SettingHolder.file_excludes:
                    if fileExc in filename:
                        fileContinue = False
                if fileContinue:
                    if filename.endswith('.txt') and '.txt' in SettingHolder.input_file_types:
                        print('file', filePath)
                        self.handle_txt(filePath)
                    elif filename.endswith('.pdf') and '.pdf' in SettingHolder.input_file_types:
                        print('file', filePath)
                        self.handle_pdf(filePath)
                if filename.endswith('.kmz') and '.kmz' in SettingHolder.input_file_types and '.kml' in SettingHolder.output_file_types:
                    print('file', filePath)
                    self.handle_kmz(filePath)

    def handle_txt(self, filePath):
        _name = os.path.basename(os.path.dirname(filePath))
        fp = open(filePath).read()
        # check for gps coordinate(s)
        matchingObj = re.findall(self.regex, fp)
        if not matchingObj:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: no gps coordinates found in txt !!!!\n')
            outputFile.close()
            LOCK.release()
            return
        gps_coordinates = []
        for i in matchingObj:
            for j in i:
                if len(j) != 0:
                    gps_coord = re.sub('[^0-9\.,]|\s', '', j)
                    if len(gps_coord) != 0:
                        gps_coordinates.append(gps_coord)
        if '.kmz' in SettingHolder.output_file_types:
            LOCK.aquire()
            for coord in gps_coordinates:
                pnt = SettingHolder.kmlFile.newPoint(name=_name)
                pnt.coords = [eval(coord)]
                SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
            LOCK.release()
        if '.txt' in SettingHolder.output_file_types:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: ' + str(matchingObj) + '\n')
            LOCK.release()

    def handle_pdf(self, filePath):
        _name = os.path.basename(os.path.dirname(filePath))
        parsed_pdf = None
        try:
            parsed_pdf = parser.from_file(filePath)
        except:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: pdf could not be dycrypted !!!!\n')
            outputFile.close()
            LOCK.release()
            return
        if not parsed_pdf:
            return
        text = parsed_pdf['content'] 
        # check for gps coordinate(s)
        matchingObj = re.findall(self.regex, text)
        if not matchingObj:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: no gps coordinates found in pdf !!!!\n')
            outputFile.close()
            LOCK.release()
            return
        gps_coordinates = []
        for i in matchingObj:
            for j in i:
                if len(j) != 0:
                    gps_coord = re.sub('[^0-9\.,]|\s', '', j)
                    if len(gps_coord) != 0:
                        gps_coordinates.append(gps_coord)
        if '.kmz' in SettingHolder.output_file_types:
            LOCK.acquire()
            for coord in gps_coordinates:
                pnt = SettingHolder.kmlFile.newPoint(name=_name)
                pnt.coords = [eval(coord)]
                SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
            LOCK.release()
        if '.txt' in SettingHolder.output_file_types:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: ' + str(matchingObj) + '\n')
            outputFile.close()
            LOCK.release()

    def handle_kmz(self, filePath):
        _name = os.path.basename(os.path.dirname(filePath))
        # extract kmz
        kmz = ZipFile(filePath, 'r')
        kml = kmz.open('doc.kml', 'r').read()
        tree = etree.fromstring(kml)
        for element in tree.iter():
            if (element.tag.endswith('Point')):
                for elem in element.iter():
                    if (elem.tag.endswith('coordinates')):
                        LOCK.acquire()
                        pnt = SettingHolder.kmlFile.newpoint(name=_name)
                        pnt.coords = [eval(elem.text)]
                        SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
                        LOCK.release()
            elif (element.tag.endswith('Polygon')):
                LOCK.acquire()
                pol = SettingHolder.kmlFile.newpolygon(name=_name)
                outer = []
                inner = []
                for elem in element.iter():
                    if (elem.tag.endswith('outerBoundaryIs')):
                        for ele in elem:
                            for el in ele:
                                if (el.tag.endswith('coordinates')):
                                    tempOuter = el.text.split(' ')
                                    for i in tempOuter:
                                        outer.append(eval(i))
                    if (elem.tag.endswith('innerBoundaryIs')):
                        for ele in elem:
                            for el in ele:
                                if (el.tag.endswith('coordinates')):
                                    tempInner = el.text.split(' ')
                                    for i in tempInner:
                                        inner.append(eval(i))
                pol.outerboundaryis = outer
                pol.innerboundaryis = inner
                SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
                LOCK.release()
        if '.txt' in SettingHolder.output_file_types:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write('Folder: ' + _name + '\n')
            outputFile.write('File: ' + os.path.basename(filePath) + '\n')
            outputFile.write('Log: .kmz file present ####\n')
            outputFile.close()
            LOCK.release()

# ============== Main Dashboard =============== #

class Dashboard(QtWidgets.QMainWindow):

    signalFolder = pyqtSignal()

    def __init__(self):

        # create widget and load ui
        super().__init__()
        self._widget = QtWidgets.QMainWindow()
        dashboardui = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'dashboard.ui')
        uic.loadUi(dashboardui, self._widget)

        # file scraper holders
        self.tempFileLines = []
        self.tempInclude = ''
        self.tempListIndex = 0
        self.tempFolder = ''

        # create style elements
        self.highlight_format = QtGui.QTextBlockFormat()
        self.highlight_format.setBackground(QtGui.QColor(60, 110, 113, 100))
        self.plain_format = QtGui.QTextBlockFormat()
        self.plain_format.setBackground(Qt.white)

        # initialize widget element visibility
        self._widget.lbl_num_folders.setVisible(False)
        self._widget.lbl_num_folders_label.setVisible(False)

        # load settings
        SettingHolder.printSettings()
        Settings.load_settings(self._widget)

        self.global_location = os.path.dirname(os.path.realpath(__file__))
    
        # ------ set button image -------
        icon = QtGui.QIcon(os.path.join(self.global_location,'filePreviewIcon.png'))
        self._widget.btn_file_preview.setIcon(icon)

        # ----- connect buttons -----
        # controls
        self._widget.btn_save_settings.clicked.connect(self.save_settings)
        self._widget.btn_help.clicked.connect(self.show_help)
        self._widget.btn_report_issue.clicked.connect(self.show_issue)
        self._widget.btn_start.clicked.connect(self.start)
        self._widget.btn_clear.clicked.connect(self.clearScreen)

        # file settings
        self._widget.btn_folder_inc.clicked.connect(self.addFolderInc)
        self._widget.btn_folder_exc.clicked.connect(self.addFolderExc)
        self._widget.btn_file_inc.clicked.connect(self.addFileInc)
        self._widget.btn_file_exc.clicked.connect(self.addFileExc)
        self._widget.btn_folder_inc_del.clicked.connect(self.delFolderInc)
        self._widget.btn_folder_exc_del.clicked.connect(self.delFolderExc)
        self._widget.btn_file_inc_del.clicked.connect(self.delFileInc)
        self._widget.btn_file_exc_del.clicked.connect(self.delFileExc)
        self._widget.cb_pdf.toggled.connect(self.Cb)
        self._widget.cb_txt.toggled.connect(self.Cb)
        self._widget.cb_kmz.toggled.connect(self.Cb)
        self._widget.cbout_txt.toggled.connect(self.Cbout)
        self._widget.cbout_kml.toggled.connect(self.Cbout)
        self._widget.btn_directory_location.clicked.connect(self.open_folder_dialog)
        self._widget.btn_regex_clear.clicked.connect(self.clearRegex)
        self._widget.btn_regex_add.clicked.connect(self.addRegex)

        # file regex
        self._widget.btn_file_preview.clicked.connect(self.file_preview)
        self._widget.list_regex.itemPressed.connect(self.removeRegex)
        for i in SettingHolder.regex_lines:
            listWidgetItem = QtWidgets.QListWidgetItem(i)
            listWidgetItem.setTextAlignment(Qt.AlignCenter)
            self._widget.list_regex.addItem(listWidgetItem)


        # set output file name
        tm1, tm2 = str(time.time()).split(".")
        SettingHolder.output_file_log = 'C:\\tmp\\' + str(tm1) + str(tm2) + '_siteMap_log.txt'
        SettingHolder.kml_output_file = 'C:\\tmp\\' + str(tm1) + str(tm2) + '_siteMap_map.kml'

        # start a kml file
        self.idx = 0
        SettingHolder.kmlFile = simplekml.Kml()

        # multi threads
        self.thread = {}
        self.num_threads = 0
        self.done_threads = 0

        # redirect close event
        self._widget.closeEvent = self.closeEvent

        # regex widget holder
        self.regexWidget = None

        # show it!
        self._widget.show()

    # close event
    def closeEvent(self, event):
        print('close')
        for i in range(self.num_threads - 1):
            LOCK.release()
            try:
                self.thread[i].terminate()
            except:
                pass
        self.close()

    # initialize threads
    def init_threads(self):
        dir = os.listdir(SettingHolder.dir)
        sm = 0
        for f in dir: sm += 1
        num_folders_per_thread = 5
        print('Number of folders', sm)
        if (sm > 30):
            num_folders_per_thread = math.ceil(sm / 30)

        thread_num = 0
        inc = 0
        curList = []
        for f in dir:
            curList.append(f)
            if inc == num_folders_per_thread:
                inc = 0
                self.thread[thread_num] = Worker(thread_num, curList)
                self.thread[thread_num].progress.connect(self.showCurFolder)
                self.thread[thread_num].finished.connect(self.end_thread)
                thread_num += 1
                curList = []
            inc += 1
        if len(curList) > 0:
            thread_num += 1
            self.thread[thread_num] = Worker(thread_num, curList)
            self.thread[thread_num].progress.connect(self.showCurFolder)
            self.thread[thread_num].finished.connect(self.end_thread)
        print(thread_num, ' threads initialized...')
        self.num_threads = thread_num

    # -------------------------- file settings ------------------------------
    @pyqtSlot()
    def save_settings(self):
        Settings.save_settings(self._widget)

    # folder modifiers
    @pyqtSlot()
    def addFolderInc(self):
        txt = self._widget.txt_folders_including.text().strip()
        if txt == '' or txt in SettingHolder.folder_includes: return
        if txt in SettingHolder.folder_excludes:
            return
        SettingHolder.folder_includes.append(txt)
        self._widget.lbl_folders_including.setText(self._widget.lbl_folders_including.text() + ' | ' + txt)
        self._widget.txt_folders_including.setText('')

    @pyqtSlot()
    def addFolderExc(self):
        txt = self._widget.txt_folders_excluding.text().strip()
        if txt == "" or txt in SettingHolder.folder_excludes: return
        if txt in SettingHolder.folder_includes:
            return
        SettingHolder.folder_excludes.append(txt)
        self._widget.lbl_folders_excluding.setText(self._widget.lbl_folders_excluding.text() + ' | ' + txt)
        self._widget.txt_folders_excluding.setText('')

    @pyqtSlot()
    def delFolderInc(self):
        if len(SettingHolder.folder_includes) > 0:
            SettingHolder.folder_includes.pop()
        self._widget.lbl_folders_including.setText('')
        for i in SettingHolder.folder_includes:
            self._widget.lbl_folders_including.setText(self._widget.lbl_folders_including.text() + ' | ' + i)

    @pyqtSlot()
    def delFolderExc(self):
        if len(SettingHolder.folder_excludes) > 0:
            SettingHolder.folder_excludes.pop()
        self._widget.lbl_folders_excluding.setText('')
        for i in SettingHolder.folder_excludes:
            self._widget.lbl_folders_excluding.setText(self._widget.lbl_folders_excluding.text() + ' | ' + i)

    # file modifiers
    @pyqtSlot()
    def addFileInc(self):
        txt = self._widget.txt_files_including.text().strip()
        if txt == '' or txt in SettingHolder.file_includes: return
        if txt in SettingHolder.file_excludes:
            return
        SettingHolder.file_includes.append(txt)
        self._widget.lbl_files_including.setText(self._widget.lbl_files_including.text() + ' | ' + txt)
        self._widget.txt_files_including.setText('')

    @pyqtSlot()
    def addFileExc(self):
        txt = self._widget.txt_files_excluding.text().strip()
        if txt == '' or txt in SettingHolder.file_excludes: return
        if txt in SettingHolder.file_includes:
            return
        SettingHolder.file_excludes.append(txt)
        self._widget.lbl_files_excluding.setText(self._widget.lbl_files_excluding.text() + ' | ' + txt)
        self._widget.txt_files_excluding.setText('')

    @pyqtSlot()
    def delFileInc(self):
        if len(SettingHolder.file_includes) > 0:
            last = SettingHolder.file_includes[-1]
            SettingHolder.file_includes.pop()
            print(last)
        self._widget.lbl_files_including.setText('')
        for i in SettingHolder.file_includes:
            self._widget.lbl_files_including.setText(self._widget.lbl_files_including.text() + ' | ' + i)

    @pyqtSlot()
    def delFileExc(self):
        if len(SettingHolder.file_excludes) > 0:
            SettingHolder.file_excludes.pop()
        self._widget.lbl_files_excluding.setText('')
        for i in SettingHolder.file_excludes:
            self._widget.lbl_files_excluding.setText(self._widget.lbl_files_excluding.text() + ' | ' + i)

    @pyqtSlot()
    def Cb(self):
        SettingHolder.input_file_types.clear()
        if self._widget.cb_txt.isChecked():
            SettingHolder.input_file_types.append('.txt')
        if self._widget.cb_kmz.isChecked():
            SettingHolder.input_file_types.append('.kmz')
        if self._widget.cb_pdf.isChecked():
            SettingHolder.input_file_types.append('.pdf')
        print(SettingHolder.input_file_types)

    @pyqtSlot()
    def Cbout(self):
        SettingHolder.output_file_types.clear()
        if self._widget.cbout_txt.isChecked():
            SettingHolder.output_file_types.append('.txt')
        if self._widget.cbout_kml.isChecked():
            SettingHolder.output_file_types.append('.kml')
        print(SettingHolder.output_file_types)

    @pyqtSlot()
    def open_folder_dialog(self):
        past_dir = SettingHolder.dir
        new_dir = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select a folder:', 'C:\\', QtWidgets.QFileDialog.ShowDirsOnly)
        if past_dir != new_dir:
            self._widget.txt_directory_location.setText(new_dir)
            SettingHolder.dir = new_dir
            SettingHolder.folder_includes = []
            SettingHolder.folder_excludes = []
            SettingHolder.filenames_reviewed = []
            self._widget.lbl_folders_including.setText('')
            self._widget.lbl_folders_excluding.setText('')
    # ---------------------- end settings ---------------------------------

    # ---------------------- controls ---------------------------------
    @pyqtSlot()
    def clearScreen(self):
        # SettingHolder
        SettingHolder.dir = ''
        SettingHolder.folder_includes = []
        SettingHolder.folder_excludes = []
        SettingHolder.file_includes = []
        SettingHolder.file_excludes = []
        SettingHolder.filenames_reviewed = []
        SettingHolder.input_file_types = []
        SettingHolder.output_file_types = []
        SettingHolder.regex_lines = []
        # file settings
        self._widget.txt_directory_location.setText('')
        self._widget.lbl_scraper_file_warning.setVisible(False)
        self._widget.txt_folders_excluding.setText('')
        self._widget.txt_folders_including.setText('')
        self._widget.lbl_folders_including.setText('')
        self._widget.lbl_folders_excluding.setText('')
        self._widget.txt_files_excluding.setText('')
        self._widget.txt_files_including.setText('')
        self._widget.lbl_files_including.setText('')
        self._widget.lbl_files_excluding.setText('')
        self._widget.cb_pdf.setChecked(False)
        self._widget.cb_txt.setChecked(False)
        self._widget.cb_kmz.setChecked(False)
        self._widget.cbout_txt.setChecked(False)
        self._widget.cbout_kml.setChecked(False)
        self._widget.list_regex.clear()
        # controls
        self._widget.lbl_error.setText('')
        self._widget.lbl_status.setText('')
        self._widget.lbl_num_folders.setVisible(False)
        self._widget.lbl_num_folders.setText('0')
        self._widget.lbl_num_folders_label.setVisible(False)
        self._widget.statusBar().showMessage('')

    @pyqtSlot()
    def show_help(self):
        self.helpWidget = QtWidgets.QWidget()
        helpui = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'help.ui')
        uic.loadUi(helpui, self.helpWidget)
        self.helpWidget.show()

    @pyqtSlot()
    def show_issue(self):
        self.issueWidget = QtWidgets.QWidget()
        issueui = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'issue.ui')
        uic.loadUi(issueui, self.issueWidget)
        self.issueWidget.show()

    @pyqtSlot()
    def start(self):
        self.idx = 0
        self._widget.lbl_error.setText('')
        self._widget.lbl_status.setText('')
        self.finished = True
        print(SettingHolder.file_includes)
        self.start_scraper()
    # ---------------- end controls -----------------

    # ---------------- start file scraper --------------
    def showCurFolder(self, filePath):
        self._widget.statusBar().showMessage(filePath)
        LOCK.acquire()
        self.idx += 1
        LOCK.release()
        self._widget.lbl_num_folders.setText(str(self.idx))

    def end_scraper(self):
        self._widget.lbl_status.setText('done!')
        self._widget.btn_start.setEnabled(True)
        self._widget.btn_clear.setEnabled(True)
        reply = QtWidgets.QMessageBox()
        reply.setIcon(QtWidgets.QMessageBox.Information)
        reply.setText('done')
        reply.exec()

    def end_thread(self, index):
        self.thread[index].terminate()
        print('thread ending: ', index)
        LOCK.acquire()
        self.done_threads += 1
        if (self.done_threads == self.num_threads): self.end_scraper()
        LOCK.release()

    @pyqtSlot()
    def start_scraper(self):
        scraper_dir = self._widget.txt_directory_location.text()
        if len(scraper_dir) == 0:
            self._widget.lbl_error.setText('Choose a directory')
            return
        if len(SettingHolder.input_file_types) == 0:
            self._widget.lbl_error.setText('Select at least one input file type')
            return
        if len(SettingHolder.output_file_log) == 0:
            self._widget.lbl_error.setText('Select at least one output file type')
            return
        if (self._widget.cb_pdf.isChecked()) and len(SettingHolder.file_includes) == 0:
            reply = QtWidgets.QMessageBox()
            reply.setIcon(QtWidgets.QMessageBox.Information)
            reply.setWindowTitle("No File Includes/Excludes")
            reply.setText('Are you sure you want to scrape from every pdf file in this directory?\n(this can take a long time)')
            reply.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
            returnValue = reply.exec()
            if returnValue != QtWidgets.QMessageBox.Ok:
                return
        try:
            os.remove(SettingHolder.output_file_log)
        except:
            pass
        self._widget.lbl_status.setText('working...')
        self._widget.btn_start.setEnabled(False)
        self._widget.btn_clear.setEnabled(False)
        self._widget.lbl_num_folders.setVisible(True)
        self._widget.lbl_num_folders_label.setVisible(True)
        self._widget.lbl_num_folders.setText('0')

        with open(SettingHolder.output_file_log, 'w+') as output_log:
            output_log.write('======= SiteMap scraper starting =======\n')
            output_log.write('Time: ' + str(time.time()))
            output_log.write(SettingHolder.getSettings())

        # start threading
        self.init_threads()
        LOCK.release()
        for i in self.thread:
            self.thread[i].start()

    # ---------- file scraper regex -----------
    @pyqtSlot()
    def file_preview(self):
        if not self._widget.cb_pdf.isChecked() and not self._widget.cb_txt.isChecked():
            self._widget.lbl_error.setText('only .pdf or .txt files require this action')
            return
        if (SettingHolder.dir == ''):
            self._widget.lbl_error.setText('Please select a directory first')
            return

        # check what file types to open
        options = ''
        if self._widget.cb_pdf.isChecked() and self._widget.cb_txt.isChecked():
            options = 'PDF (*.pdf);;TXT (*.txt)'
        elif self._widget.cb_pdf.isChecked():
            options += 'PDF (*.pdf)'
        elif self._widget.cb_txt.isChecked():
            options += 'TXT (*.txt)'
        
        # select a file
        fileSelected = QtWidgets.QFileDialog.getOpenFileName(self._widget, 'Open File', SettingHolder.dir, options)
        file = os.path.split(fileSelected[0])
        filepath = file[0]
        if filepath == '':
            return
        if (SettingHolder.dir not in filepath):
            self._widget.lbl_error.setText('File not within the outer directory')
            return

        folderCont = len(SettingHolder.folder_includes) == 0
        for folder_substring in SettingHolder.folder_includes:
            if folder_substring in os.path.basename(filepath):
                folderCont = True
        if not folderCont:
            self._widget.lbl_error.setText('File not in an allowed directory, check folder includes')
            return
        for folder_substring in SettingHolder.folder_excludes:
            if folder_substring in os.path.basename(filepath):
                self._widget.lbl_error.setText('File not in an allowed directory, check folder excludes')
                return
        fileCont = len(SettingHolder.file_includes) == 0
        for file_substring in SettingHolder.file_includes:
            if file_substring in os.path.basename(fileSelected[0]):
                fileCont = True
        if not fileCont:
            self._widget.lbl_error.setText('Filename not allowed, check includes')
            return
        for file_substring in SettingHolder.file_excludes:
            if file_substring in os.path.basename(fileSelected[0]):
                self._widget.lbl_error.setText('Filename not allowed, check excludes')
                return
        
        # read file
        if fileSelected[1] == 'PDF (*.pdf)':
            parsed_pdf = None
            try:
                parsed_pdf = parser.from_file(fileSelected[0])
            except:
                self._widget.lbl_error.setText('pdf could not be opened')
                return
            text = parsed_pdf['content'] 
            self._widget.scraperWidget = QtWidgets.QWidget()
            uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scraper.ui'), self._widget.scraperWidget)
            self._widget.scraperWidget.lbl_scraper_filename.setText(os.path.basename(fileSelected[0]))
            self._widget.scraperWidget.show()
            regex = r''
            for idx, value in enumerate(SettingHolder.regex_lines):
                regex += '(' + value + ')'
                if idx != len(SettingHolder.regex_lines) - 1:
                    regex += '|'
            print(regex)
            colorStr = '<span style=\"background-color: #7aaacc;\">'
            resetStr = '</span>'
            lastMatch = 0
            formattedText = ''
            formattedText = '<div>'
            for match in re.finditer(regex, text):
                start, end = match.span()
                formattedText += text[lastMatch: start] + colorStr + text[start: end] + resetStr
                lastMatch = end
            formattedText += text[lastMatch:] + '</div>'
            self._widget.scraperWidget.txt_scraper.setText(formattedText)
        elif fileSelected[1] == 'TXT (*.txt)':
            text = open(fileSelected[0]).read()
            self._widget.scraperWidget = QtWidgets.QWidget()
            uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'scraper.ui'), self._widget.scraperWidget)
            self._widget.scraperWidget.lbl_scraper_filename.setText(os.path.basename(fileSelected[0]))
            self._widget.scraperWidget.show()
            regex = r''
            for idx, value in enumerate(SettingHolder.regex_lines):
                regex += '(' + value + ')'
                if idx != len(SettingHolder.regex_lines) - 1:
                    regex += '|'
            print(regex)
            colorStr = '<span style=\"background-color: #7aaacc;\">'
            resetStr = '</span>'
            lastMatch = 0
            formattedText = '<div>'
            for match in re.finditer(regex, text):
                start, end = match.span()
                formattedText += text[lastMatch: start] + colorStr + text[start: end] + resetStr
                lastMatch = end
            formattedText += text[lastMatch:] + '</div>'
            self._widget.scraperWidget.txt_scraper.setText(formattedText)
        self._widget.lbl_error.setText('')
    
    @pyqtSlot()
    def addRegexList(self):
        regex_entered = self.regexWidget.txt_regex_input.text()
        if regex_entered in SettingHolder.regex_lines or len(regex_entered) == 0:
            return
        self.regexWidget.txt_regex_input.setText('')
        listWidgetItem = QtWidgets.QListWidgetItem(regex_entered)
        listWidgetItem.setTextAlignment(Qt.AlignCenter)
        self._widget.list_regex.addItem(listWidgetItem)
        SettingHolder.regex_lines.append(regex_entered)

    @pyqtSlot()
    def addRegex(self):
        self.regexWidget = QtWidgets.QDialog()
        uic.loadUi(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'regex.ui'), self.regexWidget)
        self.regexWidget.setWindowTitle('Regular Expression')
        self.regexWidget.btn_save_regex.clicked.connect(self.addRegexList)
        self.regexWidget.exec()

    @pyqtSlot()
    def removeRegex(self):
        listItems = self._widget.list_regex.selectedItems()
        if not listItems: return
        reg = listItems[0].text()
        self._widget.list_regex.takeItem(self._widget.list_regex.row(listItems[0]))
        SettingHolder.regex_lines.remove(reg)

    @pyqtSlot()
    def clearRegex(self):
        self._widget.list_regex.clear()
        SettingHolder.regex_lines.clear()
