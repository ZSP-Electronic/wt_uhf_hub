import pip

class installRequired():
    
    def run(self):
        REQIREDIR = './requirements.txt'
        pullData = open(REQIREDIR, 'r').read()
        requirelist = pullData.split(',\n')
        for package in requirelist:
            pip.main(['install', package])
