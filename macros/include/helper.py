# Class to help with some methods accessing files and stuff
import os


class helper:

    def __init__(self, input, central, redirector = None):
        self.input = input
        self.isCentral = central
        if redirector:
            self.redirector = redirector
        elif central:
            self.redirector = 'root://cmsxrootd.fnal.gov'
        else:
            self.redirector = None
        print("Using helper to access the files:")
        print("  > Central: ", central)
        print("  > Redirector: %s"%(redirector))
        print("  > Looking in: %s"%(input))

    def getFiles(self, step, number):
        files = []
        if self.isCentral:
            os.system(f"""dasgoclient -query="file dataset={self.input}" > temp.txt""")
        else:
            os.system(f'xrdfs %s ls {self.input} > temp.txt'%(self.redirector))
        with open('temp.txt', 'r') as file:
            filenames = file.readlines()
            for f in filenames[step*number:number*(step+1)]:
                if '.root' in f:
                    filename = '%s/'%(self.redirector)+f[:-1] if self.isCentral else '%s:/'%(self.redirector)+f[:-1]
                    files.append(filename)
        #os.system('rm temp.txt')
        print("Found files:")
        print(files)
        return files
