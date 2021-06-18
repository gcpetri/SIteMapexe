# pyqt imports
from PyQt5 import QtWidgets, uic, QtGui
from PyQt5.QtCore import pyqtSlot, Qt, QObject, pyqtSignal, QThread, QSemaphore

# file imports
from SiteMap.settings import Settings
from SiteMap.settingholder import SettingHolder

# python libaries
import sys
import os
import time
import PyPDF2
from pikepdf import Pdf
from zipfile import ZipFile
import simplekml
import re
from lxml import etree
from io import StringIO, BytesIO
from pathlib import Path
import math
import time


# ============== Thread Semaphore ============ #
LOCK = QSemaphore(0)
# ============== Worker Thread =============== #

class Worker(QThread):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str)
    dir = []

    def __init__(self, index, dir):
        super(Worker, self).__init__(None)
        self.dir = dir
        self.index = index
        self.global_location = os.path.dirname(os.path.realpath(__file__))

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
                print('file', filePath)
                fileContinue = len(SettingHolder.file_includes_keys) == 0
                filename = os.path.basename(filePath)
                fileContinue = filename.endswith('.kmz') and ('.kmz' in SettingHolder.checked_file_types)
                thisFileIncludes = []
                for fileInc in SettingHolder.file_includes_keys:
                    if fileInc in filename:
                        thisFileIncludes.append(fileInc)
                        fileContinue = True
                for fileExc in SettingHolder.file_excludes_keys:
                    if fileExc in filename:
                        fileContinue = False
                if fileContinue:
                    # print(filePath)
                    if filename.endswith('.txt'):
                        self.handle_txt(filePath, thisFileIncludes)
                    elif filename.endswith('.pdf'):
                        self.handle_pdf(filePath, thisFileIncludes)
                    elif filename.endswith('.kmz') and ('.kmz' in SettingHolder.output_file_types):
                        self.handle_kmz(filePath)

    def handle_txt(self, filePath, thisFileIncludes):
        _name = os.path.basename(os.path.dirname(filePath))
        fp = open(filePath)
        file_includes = []
        for fc in thisFileIncludes:
            file_includes += SettingHolder.file_includes[fc]
        oneline = ''
        print(file_includes)
        for i, line in enumerate(fp):
            if i in file_includes:
                oneline += line.strip() + ' '
        fp.close()
        # check for gps coordinates
        gpsfound = False
        if '.kmz' in SettingHolder.output_file_types:
            print('print to kmz')
            matchingObj = re.search(SettingHolder.regex, oneline)
            if matchingObj:
                gpsfound = True
                LOCK.acquire()
                pnt = SettingHolder.kmlFile.newpoint(name=_name)
                pnt.coords = [eval(matchingObj.group(0))]
                SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
                LOCK.release()
        if '.txt' in SettingHolder.output_file_types:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write(_name + '\n')
            outputFile.write(oneline + '\n')
            if gpsfound:
                outputFile.write('############ Gps coordinate found\n')
            outputFile.close()
            LOCK.release()


    def handle_pdf(self, filePath, thisFileIncludes):
        _name = os.path.basename(os.path.dirname(filePath))
        pdfFileObj = open(filePath, 'rb')
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        text = ''
        if pdfReader.isEncrypted:
            # print('is encrypted')
            try:
                with Pdf.open(filePath) as pdfFile:
                    num_pages = len(pdfFile.pages)
                    try:
                        del pdfFile.pages[-1]
                    except:
                        pass
                    temppdf = os.path.join(self.global_location, SettingHolder.artifacts) + str(self.index) + '_decrypted.pdf'
                    pdfFile.save(temppdf)
                pdfFileObj = open(temppdf, 'rb')
                pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            except:
                LOCK.acquire()
                outputFile = open(SettingHolder.output_file_log, 'a')
                outputFile.write('\n-----------------------------------------\n')
                outputFile.write(_name + '\n')
                outputFile.write('pdf file could not be dycrypted !!!!!!!!\n')
                outputFile.close()
                LOCK.release()
                return
        file_includes = []
        for fc in thisFileIncludes:
            file_includes += SettingHolder.file_includes[fc]
        # generate a random number
        tempfile = os.path.join(self.global_location, SettingHolder.artifacts) + str(self.index) + '_temp_file.txt'
        tempFile = open(tempfile, 'a+')
        for i in range(pdfReader.numPages - 1):
            try:
                tempFile.write(pdfReader.getPage(i).extractText())
            except:
                # print('error writing to file')
                pass
        pdfFileObj.close()
        oneline = ''
        tempFile.close()
        # print(file_includes)
        tempFile = open(tempfile, 'r')
        for i, line in enumerate(tempFile):
            if i in file_includes:
                oneline += line.strip() + ' '
        tempFile.close()
        # check for gps coordinate
        gpsfound = False
        if '.kmz' in SettingHolder.output_file_types:
            matchingObj = re.search(SettingHolder.regex, oneline)
            if matchingObj:
                gpsfound = True
                LOCK.acquire()
                pnt = SettingHolder.kmlFile.newPoint(name=_name)
                pnt.coords = [eval(matchingObj.group(0))]
                SettingHolder.kmlFile.save(SettingHolder.kml_output_file)
                LOCK.release()
        if '.txt' in SettingHolder.output_file_types:
            LOCK.acquire()
            outputFile = open(SettingHolder.output_file_log, 'a')
            outputFile.write('\n-----------------------------------------\n')
            outputFile.write(_name + '\n')
            outputFile.write(oneline + '\n')
            if gpsfound:
                outputFile.write('########## Gps coordinate found\n')
            outputFile.close()
            LOCK.release()

    def handle_kmz(self, filePath):
        _name = os.path.basename(os.path.dirname(filePath))
        # extract kmz
        kmz = ZipFile(filePath, 'r')
        kml = kmz.open('doc.kml', 'r').read()
        tree = etree.fromstring(kml)
        # print(etree.tostring(tree))
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
            outputFile.write(_name + '\n')
            outputFile.write('########## .kmz file present\n')
            outputFile.close()
            LOCK.release()

# ============== Main Dashboard =============== #

class Dashboard(QtWidgets.QMainWindow):

    signalFolder = pyqtSignal()

    def __init__(self):

        # create widget and load ui
        super().__init__()
        self._widget = QtWidgets.QMainWindow()
        dashboardui = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dashboard.ui")
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
        self._widget.lbl_num_folders.setVisible(False)
        self._widget.lbl_num_folders_label.setVisible(False)

        # load settings
        SettingHolder.printSettings()
        Settings.load_settings(self._widget)

        self.global_location = os.path.dirname(os.path.realpath(__file__))

        # ----- remove past artifacts ------
        for f in os.listdir(os.path.join(self.global_location, SettingHolder.artifacts)):
            os.remove(os.path.join(self.global_location, SettingHolder.artifacts, f))
    
        # ------ set button image -------
        icon  = QtGui.QIcon(os.path.join(self.global_location,'fileSelect.png'))
        self._widget.btn_file_drag_drop.setIcon(icon)

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
        self._widget.cbout_txt.toggled.connect(self.Cbout)
        self._widget.cbout_kmz.toggled.connect(self.Cbout)
        self._widget.btn_directory_location.clicked.connect(self.open_folder_dialog)

        # file scraper
        self._widget.btn_files_clear.clicked.connect(self.clear_reviewed)
        self._widget.btn_file_drag_drop.clicked.connect(self.drag_and_drop_dialog)

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

        self._widget.closeEvent = self.closeEvent

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
        self._widget.txt_folders_including.setText("")
    @pyqtSlot()
    def addFolderExc(self):
        txt = self._widget.txt_folders_excluding.text().strip()
        if txt == "" or txt in SettingHolder.folder_excludes: return
        if txt in SettingHolder.folder_includes:
            return
        SettingHolder.folder_excludes.append(txt)
        self._widget.lbl_folders_excluding.setText(self._widget.lbl_folders_excluding.text() + ' | ' + txt)
        self._widget.txt_folders_excluding.setText("")
    @pyqtSlot()
    def delFolderInc(self):
        if len(SettingHolder.folder_includes) > 0:
            SettingHolder.folder_includes.pop()
        self._widget.lbl_folders_including.setText("")
        for i in SettingHolder.folder_includes:
            self._widget.lbl_folders_including.setText(self._widget.lbl_folders_including.text() + ' | ' + i)
    @pyqtSlot()
    def delFolderExc(self):
        if len(SettingHolder.folder_excludes) > 0:
            SettingHolder.folder_excludes.pop()
        self._widget.lbl_folders_excluding.setText("")
        for i in SettingHolder.folder_excludes:
            self._widget.lbl_folders_excluding.setText(self._widget.lbl_folders_excluding.text() + ' | ' + i)
    # file modifiers
    @pyqtSlot()
    def addFileInc(self):
        txt = self._widget.txt_files_including.text().strip()
        if txt == '' or txt in SettingHolder.file_includes_keys: return
        if txt in SettingHolder.file_excludes_keys:
            return
        SettingHolder.file_includes_keys.append(txt)
        SettingHolder.file_includes[txt] = []
        self._widget.list_files.clear()
        self._widget.list_files_lines.clear()
        for i in SettingHolder.file_includes_keys:
            self._widget.list_files_lines.addItem(QtWidgets.QListWidgetItem(str(SettingHolder.file_includes[i])))
            self._widget.list_files.addItem(QtWidgets.QListWidgetItem(i))
        self._widget.lbl_files_including.setText(self._widget.lbl_files_including.text() + ' | ' + txt)
        self._widget.txt_files_including.setText('')
    @pyqtSlot()
    def addFileExc(self):
        txt = self._widget.txt_files_excluding.text().strip()
        if txt == "" or txt in SettingHolder.file_excludes_keys: return
        if txt in SettingHolder.file_includes_keys:
            return
        SettingHolder.file_excludes_keys.append(txt)
        self._widget.lbl_files_excluding.setText(self._widget.lbl_files_excluding.text() + ' | ' + txt)
        self._widget.txt_files_excluding.setText("")
    @pyqtSlot()
    def delFileInc(self):
        if len(SettingHolder.file_includes_keys) > 0:
            last = SettingHolder.file_includes_keys[-1]
            SettingHolder.file_includes_keys.pop()
            print(last)
            try:
                del SettingHolder.file_includes[last]
            except:
                pass
            self._widget.list_files.clear()
            self._widget.list_files_lines.clear()
            for i in SettingHolder.file_includes_keys:
                self._widget.list_files.addItem(QtWidgets.QListWidgetItem(i))
                self._widget.list_files_lines.addItem(QtWidgets.QListWidgetItem(str(SettingHolder.file_includes[i])))
        self._widget.lbl_files_including.setText('')
        for i in SettingHolder.file_includes:
            self._widget.lbl_files_including.setText(self._widget.lbl_files_including.text() + ' | ' + i)
    @pyqtSlot()
    def delFileExc(self):
        if len(SettingHolder.file_excludes_keys) > 0:
            last = SettingHolder.file_excludes_keys[-1]
            SettingHolder.file_excludes_keys.pop()
        self._widget.lbl_files_excluding.setText('')
        for i in SettingHolder.file_excludes_keys:
            self._widget.lbl_files_excluding.setText(self._widget.lbl_files_excluding.text() + ' | ' + i)
    @pyqtSlot()
    def Cb(self):
        if not self._widget.cb_pdf.isChecked() and not self._widget.cb_txt.isChecked():
            self._widget.lbl_scraper_file_warning.setVisible(False)
            self._widget.lbl_files_reviewed.setVisible(False)
            self._widget.list_files.setVisible(False)
            self._widget.btn_files_clear.setVisible(False)
            self._widget.list_files_lines.setVisible(False)
        else:
            self._widget.lbl_scraper_file_warning.setVisible(True)
            self._widget.lbl_files_reviewed.setVisible(True)
            self._widget.list_files.setVisible(True)
            self._widget.btn_files_clear.setVisible(True)
            self._widget.list_files_lines.setVisible(True)
    @pyqtSlot()
    def Cbout(self):
        SettingHolder.output_file_types = []
        if self._widget.cbout_txt.isChecked():
            SettingHolder.output_file_types.append('.txt')
        if self._widget.cbout_kmz.isChecked():
            SettingHolder.output_file_types.append('.kmz')
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
        SettingHolder.file_includes_keys = []
        SettingHolder.file_excludes_keys = []
        SettingHolder.file_includes.clear()
        SettingHolder.filenames_reviewed = []
        SettingHolder.checked_file_types = []
        SettingHolder.output_file_types = []
        # file settings
        self._widget.txt_directory_location.setText('')
        self._widget.lbl_scraper_file_warning.setVisible(False)
        self._widget.txt_files_excluding.setText('')
        self._widget.txt_files_including.setText('')
        self._widget.txt_folders_excluding.setText('')
        self._widget.txt_folders_including.setText('')
        self._widget.lbl_folders_including.setText('')
        self._widget.lbl_folders_excluding.setText('')
        self._widget.lbl_files_including.setText('')
        self._widget.lbl_files_excluding.setText('')
        self._widget.cb_pdf.setChecked(False)
        self._widget.cb_txt.setChecked(False)
        self._widget.cb_kmz.setChecked(False)
        self._widget.cbout_txt.setChecked(False)
        self._widget.cbout_kmz.setChecked(False)
        # file scraper
        self._widget.list_files.clear()
        self._widget.list_files.setVisible(False)
        self._widget.list_files_lines.clear()
        self._widget.list_files_lines.setVisible(False)
        self._widget.btn_files_clear.setVisible(False)
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
        helpui = os.path.join(os.path.dirname(os.path.realpath(__file__)), "help.ui")
        uic.loadUi(helpui, self.helpWidget)
        self.helpWidget.show()
    @pyqtSlot()
    def show_issue(self):
        self.issueWidget = QtWidgets.QWidget()
        issueui = os.path.join(os.path.dirname(os.path.realpath(__file__)), "issue.ui")
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
    # @pyqtSlot()
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
        for f in os.listdir(os.path.join(self.global_location, SettingHolder.artifacts)):
            try:
                os.remove(os.path.join(self.global_location, SettingHolder.artifacts, f))
            except:
                pass
        reply = QtWidgets.QMessageBox()
        reply.setIcon(QtWidgets.QMessageBox.Information)
        reply.setText('done')
        reply.exec()
    # pyqtSlot()
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
        if not self._widget.cb_txt.isChecked() and not self._widget.cb_pdf.isChecked() and not self._widget.cb_kmz.isChecked():
            self._widget.lbl_error.setText('Select at least one input file type')
            return
        if not self._widget.cbout_txt.isChecked() and not self._widget.cbout_kmz.isChecked():
            self._widget.lbl_error.setText('Select at least one output file type')
            return
        if (self._widget.cb_txt.isChecked() or self._widget.cb_pdf.isChecked()) and len(SettingHolder.file_includes_keys) == 0:
            self._widget.lbl_error.setText('You must select some .txt or .pdf file lines in the file scraper')
            return
        try:
            os.remove(SettingHolder.output_file_log)
        except:
            pass
        del SettingHolder.checked_file_types[:]
        if self._widget.cb_pdf.isChecked():
            SettingHolder.checked_file_types.append('.pdf')
        if self._widget.cb_kmz.isChecked():
            SettingHolder.checked_file_types.append('.kmz')
        if self._widget.cb_txt.isChecked():
            SettingHolder.checked_file_types.append('.txt')
        self._widget.lbl_status.setText('working...')
        self._widget.btn_start.setEnabled(False)
        self._widget.btn_clear.setEnabled(False)
        print(SettingHolder.output_file_types)


        # start threading
        self._widget.lbl_status.setText('working...')
        self._widget.lbl_num_folders.setVisible(True)
        self._widget.lbl_num_folders.setText('0')
        self._widget.lbl_num_folders_label.setVisible(True)
        self.init_threads()
        LOCK.release()
        for i in self.thread:
            self.thread[i].start()
    # ------------------- file scraper -------------------
    # specifying lines in a file
    @pyqtSlot()
    def fileClick(self):
        cursor = self._widget.scraperWidget.txt_scraper.textCursor()
        line_num = cursor.blockNumber()
        cursor = QtGui.QTextCursor(self._widget.scraperWidget.txt_scraper.document().findBlockByNumber(line_num))
        print(line_num)
        if line_num in self.tempFileLines:
            self.tempFileLines.remove(line_num)
            cursor.setBlockFormat(self.plain_format)
        else:
            self.tempFileLines.append(line_num)
            cursor.setBlockFormat(self.highlight_format)
        self.tempFileLines.sort()
        SettingHolder.file_includes[self.tempInclude] = self.tempFileLines
        self._widget.list_files_lines.clear()
        for i in SettingHolder.file_includes:
            self._widget.list_files_lines.addItem(QtWidgets.QListWidgetItem(str(SettingHolder.file_includes[i])))

    # choosing a file
    @pyqtSlot()
    def drag_and_drop_dialog(self):
        if not self._widget.cb_pdf.isChecked() and not self._widget.cb_txt.isChecked():
            self._widget.lbl_error.setText('only .pdf or .txt files require this action')
            return
        self._widget.lbl_files_reviewed.setText("Includes Reviewed")
        self.tempFileLines = []
        self.tempInclude = ''
        # --------- begin validation --------
        # verify outer folder is selected
        if (SettingHolder.dir == ''):
            self._widget.lbl_error.setText('Please select a directory first')
            return

        options = ''
        # check what file types to open
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
        folderCont = 0
        print(os.path.basename(filepath))
        print(SettingHolder.folder_includes)
        print(SettingHolder.folder_excludes)
        if len(SettingHolder.folder_includes) != 0:
            for folder_substring in SettingHolder.folder_includes:
                if folder_substring in os.path.basename(filepath):
                    print(folder_substring)
                    folderCont += 1
            if folderCont == 0:
                self._widget.lbl_error.setText('File not in an allowed directory, check folder includes')
                return
        if len(SettingHolder.folder_excludes) != 0:
            for folder_substring in SettingHolder.folder_excludes:
                if folder_substring in os.path.basename(filepath):
                    self._widget.lbl_error.setText('File not in an allowed directory, check folder excludes')
                    return

        # find the right file include
        self.tempInclude = ''
        if len(SettingHolder.file_includes_keys) != 0:
            sorted_list = sorted(SettingHolder.file_includes_keys, key=len)
            for file_substring in sorted_list:
                if file_substring in os.path.basename(fileSelected[0]):
                    self.tempInclude = file_substring
            if self.tempInclude == '' and (SettingHolder.file_includes_keys[0] not in ['.txt', '.pdf']):
                self._widget.lbl_error.setText('Filename not allowed, check includes')
                return
        if len(SettingHolder.file_excludes_keys) != 0:
            for file_substring in SettingHolder.file_excludes_keys:
                if file_substring in fileSelected[0]:
                    self._widget.lbl_error.setText('Filename not allowed, check excludes')
                    return
        if self.tempInclude == '':
            self.tempInclude = os.path.splitext(fileSelected[0])[1]
            self._widget.lbl_files_including.setText('| ' + self.tempInclude)
        if self.tempInclude != '':
            item = self._widget.list_files.findItems(self.tempInclude, Qt.MatchExactly)
            if len(item) == 0:
                self._widget.list_files.addItem(QtWidgets.QListWidgetItem(self.tempInclude))
                SettingHolder.file_includes_keys.append(self.tempInclude)
            else:
                self.tempFileLines = SettingHolder.file_includes[self.tempInclude]
        print(self.tempInclude)
        # end validation

        # read pdf file
        if fileSelected[1] == 'PDF (*.pdf)':
            self._widget.scraperWidget = QtWidgets.QWidget()
            scraperui = os.path.join(self.global_location, 'scraper.ui')
            uic.loadUi(scraperui, self._widget.scraperWidget)
            self._widget.scraperWidget.lbl_scraper_filename.setText(os.path.basename(fileSelected[0]))
            self._widget.scraperWidget.show()
            pdfFileObj = open(fileSelected[0], 'rb')
            pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
            text = ''
            if pdfReader.isEncrypted:
                print('is encrypted')
                try:
                    with Pdf.open(fileSelected[0]) as pdfFile:
                        del pdfFile.pages[-1]
                        pdfFile.save(os.path.join(self.global_location, SettingHolder.artifacts, 'decrypted.pdf'))
                    pdfFileObj = open(os.path.join(self.global_location, SettingHolder.artifacts, 'decrypted.pdf'), 'rb')
                    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
                except:
                    self._widget.lbl_error.setText('File could not be dycrypted')
                    return
            else:
                print('File Not Encrypted')
            for i in range(pdfReader.numPages - 1):
                text += pdfReader.getPage(i).extractText()
            pdfFileObj.close()
            self._widget.scraperWidget.txt_scraper.setText(text)
            self._widget.scraperWidget.txt_scraper.cursorPositionChanged.connect(self.fileClick);

            cursor = ''
            for line in self.tempFileLines:
                cursor = QtGui.QTextCursor(self._widget.scraperWidget.txt_scraper.document().findBlockByNumber(line))
                cursor.setBlockFormat(self.highlight_format)
        # read text file
        elif fileSelected[1] == 'TXT (*.txt)':
            text = open(fileSelected[0]).read()
            self._widget.scraperWidget = QtWidgets.QWidget()
            scraperui = os.path.join(self.global_location, 'scraper.ui')
            uic.loadUi(scraperui, self._widget.scraperWidget)
            self._widget.scraperWidget.lbl_scraper_filename.setText(fileSelected[0])
            self._widget.scraperWidget.show()
            self._widget.scraperWidget.txt_scraper.setText(text)

            self._widget.scraperWidget.txt_scraper.cursorPositionChanged.connect(self.fileClick)
            cursor = ''
            for line in self.tempFileLines:
                cursor = QtGui.QTextCursor(self._widget.scraperWidget.txt_scraper.document().findBlockByNumber(line))
                cursor.setBlockFormat(self.highlight_format)
        self._widget.lbl_error.setText('')
        SettingHolder.filenames_reviewed.append(fileSelected[0])

    @pyqtSlot()
    def clear_reviewed(self):
        SettingHolder.filenames_reviewed = []
        # self._widget.list_files.clear()
        self._widget.list_files_lines.clear()
        for fileInc in SettingHolder.file_includes_keys:
            SettingHolder.file_includes[fileInc] = []
        for i in range(len(SettingHolder.file_includes_keys)):
            self._widget.list_files_lines.addItem(QtWidgets.QListWidgetItem('[]'))


#start the app
#if __name__ == '__main__':
#    app = QtWidgets.QApplication(sys.argv)
#    window = Dashboard()
#    app.exec()
