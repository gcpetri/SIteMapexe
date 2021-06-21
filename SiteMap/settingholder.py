
class SettingHolder:

    # folder restrictions
    folder_includes = []
    folder_excludes = []

    # file restrictions
    file_excludes = []
    file_includes = []

    # files types already checked
    input_file_types = []

    # output file types
    output_file_types = []

    # output file settings
    output_file_log = 'C:\\tmp\\siteMap_log.txt'
    kml_output_file = 'C:\\tmp\\siteMap.kml'

    # outermost directory
    dir = ''

    # kmz file class
    kmlFile = None

    # sample regular expression to find gps coordinates
    # r'N\s?\d\d?.\d{5}o?,\s?W\s?-?\d\d?.\d{5}o?'

    # regular expressions entered
    regex_lines = []

    def printSettings():
        print('-------- SiteMap Settings --------')
        print('Include Folders With: ', SettingHolder.folder_includes)
        print('Exclude Folder With: ', SettingHolder.folder_excludes)
        print('Include Files With: ', SettingHolder.file_includes)
        print('Exclude Files With: ', SettingHolder.file_excludes)
        print('Input File Types: ', SettingHolder.input_file_types)
        print('Output File Types: ', SettingHolder.output_file_types)
        print('Output File log: ', SettingHolder.output_file_log)
        print('Output File kml: ', SettingHolder.kml_output_file)
        print('Outermost Directory: ', SettingHolder.dir)
        print('--------- End Settings ----------')

    def getSettings():
        settingStr = '\n-------- SiteMap Settings --------\nInclude Folders With: ' + str(SettingHolder.folder_includes) + '\nExclude Folder With: ' + str(SettingHolder.folder_excludes) + '\nInclude Files With: ' + str(SettingHolder.file_includes) +'\nExclude Files With: ' + str(SettingHolder.file_excludes) +'\nInput File Types: ' + str(SettingHolder.input_file_types) +'\nOutput File Types: ' + str(SettingHolder.output_file_types) +'\nOutput File log: ' + SettingHolder.output_file_log +'\nOutput File kml: ' + SettingHolder.kml_output_file +'\nOutermost Directory: ' + SettingHolder.dir + '\nRegular Expressions: ' + str(SettingHolder.regex_lines) + '\n--------- End Settings ----------\n\n\n'
        return settingStr