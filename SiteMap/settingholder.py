
class SettingHolder:

    # folder restrictions
    folder_includes = []
    folder_excludes = []

    # file restrictions
    file_excludes_keys = []
    file_includes_keys = []
    file_includes = {}

    # files already reviewed
    filenames_reviewed = []

    # files types already checked
    checked_file_types = []

    # output file types
    output_file_types = []

    # output file settings
    output_file_log = 'C:\\tmp\\siteMap_log.txt'
    kml_output_file = 'C:\\tmp\\siteMap.kml'

    # artifacts path
    artifacts = 'artifacts/'

    # outermost directory
    dir = ''

    # kmz file class
    kmlFile = None

    # regular expression to find gps coordinates
    regex = r'([\(\s]?.?\d?\d\.\d*,.?.?\d?\d?\d\.\d*[\s\)]?)|([\s\(]?.?\d?\d[\.\°]\d?\d[\.\'\′]\d?\d[\.\"]?\d?\d?.?N?,?.?.?\d?\d?\d[\.\°]\d?\d[\.\'\′]\d?\d[\.\"]?\d?\d?.?W?[\s\)]?)'

    def printSettings():
        print('-------- SiteMap Settings --------')
        print('Include in Folder: ', SettingHolder.folder_includes)
        print('Exclude in Folder: ', SettingHolder.folder_excludes)
        print('Include in File: ', str(SettingHolder.file_includes))
        print('Exclude in File: ', SettingHolder.file_excludes_keys)
        print('Files Reviewed: ', SettingHolder.filenames_reviewed)
        print('File Types Reviewed: ', SettingHolder.checked_file_types)
        print('Output File Types: ', SettingHolder.output_file_types)
        print('Output file path: ', SettingHolder.output_file_log)
        print('Outermost Directory: ', SettingHolder.dir)
        print('--------- End Settings ----------')
