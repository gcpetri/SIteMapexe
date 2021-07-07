import json
import os
import sys
from SiteMap.settingholder import SettingHolder


class Settings:

    def load_settings(_widget):

        # load json data from external file
        data = ''
        if getattr(sys, 'frozen', False):
            application_path = os.path.join(os.path.dirname(sys.executable), 'SiteMap')
        elif __file__:
            application_path = os.path.dirname(__file__)
        save_settingsjson = os.path.join(application_path, 'save_settings.json')
        json_file = open(save_settingsjson, 'r+')
        try:
            data = json.load(json_file)
        except:
            json_file.truncate(0)
            json_file.close()
            return
        json_file.close()

        # ---- dir ----
        _widget.txt_directory_location.setText(data['dir'])
        SettingHolder.dir = data['dir']

        # default widgets to not visible
        _widget.cb_pdf.setChecked(False)
        _widget.cb_kmz.setChecked(False)
        _widget.cb_txt.setChecked(False)
        _widget.cbout_txt.setChecked(False)
        _widget.cbout_kml.setChecked(False)

        # ----- input file types ------
        try:
            SettingHolder.input_file_types = data['input-file-types']
            for ftypes in data['input-file-types']:
                if ftypes == '.pdf':
                    _widget.cb_pdf.setChecked(True)
                elif ftypes == '.kmz':
                    _widget.cb_kmz.setChecked(True)
                elif ftypes == '.txt':
                    _widget.cb_txt.setChecked(True)

            # ------ output file types ------
            SettingHolder.output_file_types = data['output-file-types']
            for ftypes in data['output-file-types']:
                if ftypes == '.txt':
                    _widget.cbout_txt.setChecked(True)
                elif ftypes == '.kml':
                    _widget.cbout_kml.setChecked(True)

            # -------- folder specifications -------
            SettingHolder.folder_includes = data['folder-includes']
            SettingHolder.folder_excludes = data['folder-excludes']
            for f in data['folder-includes']:
                _widget.lbl_folders_including.setText(_widget.lbl_folders_including.text() + ' | ' + f)
            for f in data['folder-excludes']:
                _widget.lbl_folders_excluding.setText(_widget.lbl_folders_excluding.text() + ' | ' + f)

            # -------- file specifications ---------
            SettingHolder.file_includes = data['file-includes']
            SettingHolder.file_excludes = data['file-excludes']
            for f in data['file-includes']:
                _widget.lbl_files_including.setText(_widget.lbl_files_including.text() + ' | ' + f)
            for f in data["file-excludes"]:
                _widget.lbl_files_excluding.setText(_widget.lbl_files_excluding.text() + ' | ' + f)

            # ------- set output file location -------
            # TODO

            # -------- regex expressions --------
            SettingHolder.regex_lines = data['regex-lines']
        except:
            json_file = open(save_settingsjson, 'w+')
            json_file.write('')
            json_file.close()
            return


    def save_settings(_widget):
        dict = {
            'dir': '',
            'input-file-types': [],
            'output-file-types': [],
            'folder-includes': [],
            'folder-excludes': [],
            'file-includes': [],
            'file-excludes': [],
            'regex-lines': []
        }
        dict['dir'] = _widget.txt_directory_location.text()
        dict['folder-includes'] = SettingHolder.folder_includes
        dict['folder-excludes'] = SettingHolder.folder_excludes
        dict['file-includes'] = SettingHolder.file_includes
        dict['file-excludes'] = SettingHolder.file_excludes
        dict['input-file-types'] = SettingHolder.input_file_types
        dict['output-file-types'] = SettingHolder.output_file_types
        dict['regex-lines'] = SettingHolder.regex_lines

        # write to json file
        if getattr(sys, 'frozen', False):
            application_path = os.path.join(os.path.dirname(sys.executable), 'SiteMap')
        elif __file__:
            application_path = os.path.dirname(__file__)
        save_settingsjson = os.path.join(application_path, 'save_settings.json')
        with open(save_settingsjson, 'w+') as save_settings:
            json.dump(dict, save_settings, indent=4)
