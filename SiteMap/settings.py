import json
import os
from SiteMap.settingholder import SettingHolder
from PyQt5.QtWidgets import QListWidgetItem


class Settings:

    def load_settings(_widget):

        # load json data from external file
        data = ''
        save_settingsjson = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_settings.json")
        with open(save_settingsjson, 'r') as json_file:
            data = json.load(json_file)

        # ---- dir ----
        _widget.txt_directory_location.setText(data['dir'])
        SettingHolder.dir = data['dir']

        # ---- checked file types -------

        # default widgets to not visible
        _widget.cb_pdf.setChecked(False)
        _widget.cb_kmz.setChecked(False)
        _widget.cb_txt.setChecked(False)
        _widget.cbout_txt.setChecked(False)
        _widget.cbout_kmz.setChecked(False)
        _widget.btn_files_clear.setVisible(False)
        _widget.list_files.setVisible(False)
        _widget.list_files_lines.setVisible(False)

        show_warning = False
        for ftypes in data['checked-file-types']:
            if ftypes == '.pdf':
                show_warning = True
                _widget.cb_pdf.setChecked(True)
                SettingHolder.checked_file_types.append('.pdf')
            elif ftypes == '.kmz':
                _widget.cb_kmz.setChecked(True)
                SettingHolder.checked_file_types.append('.kmz')
            elif ftypes == '.txt':
                show_warning = True
                _widget.cb_txt.setChecked(True)
                SettingHolder.checked_file_types.append('.txt')

        _widget.lbl_scraper_file_warning.setVisible(show_warning)
        _widget.btn_files_clear.setVisible(show_warning)
        _widget.list_files.setVisible(show_warning)
        _widget.list_files_lines.setVisible(show_warning)
        _widget.lbl_scraper_file_warning.setVisible(show_warning)
        _widget.lbl_files_reviewed.setVisible(show_warning)

        # ------ output file types ------
        for ftypes in data['output-file-types']:
            if ftypes == '.txt':
                _widget.cbout_txt.setChecked(True)
                SettingHolder.output_file_types.append('.txt')
            elif ftypes == '.kmz':
                _widget.cbout_kmz.setChecked(True)
                SettingHolder.output_file_types.append('.kmz')

        # -------- folder specifications -------
        for f in data['folder-includes']:
            SettingHolder.folder_includes.append(f)
            _widget.lbl_folders_including.setText(_widget.lbl_folders_including.text() + ' | ' + f)
        for f in data['folder-excludes']:
            SettingHolder.folder_excludes.append(f)
            _widget.lbl_folders_excluding.setText(_widget.lbl_folders_excluding.text() + ' | ' + f)

        # -------- file specifications ---------
        SettingHolder.file_includes_keys = data['file-includes-keys']
        SettingHolder.file_includes = data['file-includes']
        for f in data['file-includes-keys']:
            _widget.lbl_files_including.setText(_widget.lbl_files_including.text() + ' | ' + f)
            _widget.list_files.addItem(QListWidgetItem(f))
            _widget.list_files_lines.addItem(QListWidgetItem(str(data['file-includes'][f])))
        SettingHolder.file_excludes_keys = data['file-excludes-keys']
        for f in data["file-excludes-keys"]:
            _widget.lbl_files_excluding.setText(_widget.lbl_files_excluding.text() + ' | ' + f)

        # ---------- files reviewed ----------
        for f in data['files-reviewed']:
            if '.txt' in f:
                _widget.cbout_txt.setChecked(True)
                SettingHolder.files_reviewed.append('.txt')

    def save_settings(_widget):
        dict = {
            "dir": "",
            "checked-file-types": [],
            "output-file-types": [],
            "folder-includes": [],
            "folder-excludes": [],
            "file-includes-keys": [],
            "file-excludes-keys": [],
            "file-includes": {},
            "files-reviewed": [],
        }
        dict["dir"] = _widget.txt_directory_location.text()
        dict["file-includes-keys"] = SettingHolder.file_includes_keys
        dict["file-excludes-keys"] = SettingHolder.file_excludes_keys
        dict["folder-includes"] = SettingHolder.folder_includes
        dict["folder-excludes"] = SettingHolder.folder_excludes
        dict["file-includes"] = SettingHolder.file_includes
        if _widget.cb_pdf.isChecked():
            dict["checked-file-types"].append('.pdf')
        if _widget.cb_kmz.isChecked():
            dict["checked-file-types"].append('.kmz')
        if _widget.cb_txt.isChecked():
            dict["checked-file-types"].append('.txt')
        if _widget.cbout_txt.isChecked():
            dict["output-file-types"].append('.txt')
        if _widget.cbout_kmz.isChecked():
            dict["output-file-types"].append('.kmz')

        # write to json file
        save_settingsjson = os.path.join(os.path.dirname(os.path.realpath(__file__)), "save_settings.json")
        with open(save_settingsjson, 'w+') as save_settings:
            json.dump(dict, save_settings, indent=4)
