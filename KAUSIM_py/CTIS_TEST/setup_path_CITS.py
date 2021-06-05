import os,sys,inspect,logging

class SetupPath:
    @staticmethod
    def getDirLevels(path):
        path_norm = os.path.normpath(path)
        return len(path_norm.split(os.sep))

    @staticmethod
    def getCurrentPath():
        cur_filepath = os.path.abspath(inspect.getfile(inspect.currentframe()))
        return os.path.dirname(cur_filepath)

    @staticmethod
    def getGrandParentDir():
        cur_path = SetupPath.getCurrentPath()
        if SetupPath.getDirLevels(cur_path) >= 2:
            return os.path.dirname(os.path.dirname(cur_path))
        return ''

    @staticmethod
    def getParentDir():
        cur_path = SetupPath.getCurrentPath()
        if SetupPath.getDirLevels(cur_path) >= 1:
            return os.path.dirname(cur_path)
        return ''

    @staticmethod
    def addModulePath():

        parent = SetupPath.getParentDir()
        if parent !=  '':
            module_path = os.path.join(parent, 'KAUSIM_TCP')
            client_path = os.path.join(module_path, 'CITS_Server.py')
            if os.path.exists(client_path):
                sys.path.insert(0, parent)
        else:
            logging.warning("CITS module not found in parent folder.")

SetupPath.addModulePath()
