class VMWriter:
    f = 0
    output = ''
    def __init__(self, outputfile) -> None:
        self.f = open(outputfile, 'w+')
    
    def WritePush(self, segment, index):
        self.output = 'push' + ' ' + segment + ' ' + str(index) + '\n'
        self.__writeOutputToTail()
    
    def WritePop(self, segment, index):
        self.output = 'pop' + ' ' + segment + ' ' + str(index) + '\n'
        self.__writeOutputToTail()
    
    def WriteArithmetic(self, command):
        self.output = command + '\n'
        self.__writeOutputToTail()
    
    def WriteLabel(self, label):
        self.output = 'label' + ' ' + label + '\n'
        self.__writeOutputToTail()
    
    def WriteGoto(self, label):
        self.output = 'goto' + ' ' + label + '\n'
        self.__writeOutputToTail()
    
    def WriteIf(self, label):
        self.output = 'if-goto' + ' ' + label + '\n'
        self.__writeOutputToTail()
    
    def writeCall(self, name, nArgs):
        self.output = 'call' + ' ' + name + ' ' + str(nArgs) +'\n'
        self.__writeOutputToTail()
    
    def writeFunction(self, name, nLocals):
        self.output = 'function' + ' ' + name + ' ' + str(nLocals) +'\n'
        self.__writeOutputToTail()
    
    def writeReturn(self):
        self.output = 'return' + '\n'
        self.__writeOutputToTail()
    
    def close(self):
        self.f.close()
    
    def __writeOutputToTail(self):
        self.f.seek(0,2)
        self.f.write(self.output) 