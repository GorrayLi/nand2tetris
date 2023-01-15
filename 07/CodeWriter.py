class CodeWriter:
    f = 0
    vm_file = ''
    output = ''
    Ari_output1 = ''
    Ari_output2 = ''
    Ari_output3 = ''
    index = 0
    def __init__(self, output_filepath) -> None:
        self.f = open(output_filepath, 'w+')
    def setFileName(self, vmFileName):
        self.vm_file = vmFileName
        self.f.write('//'+self.vm_file+'\n')
    def writeArithmetic(self, command):
        self.Ari_output1 = '@SP\n'+'AM=M-1\n'+'D=M\n'+'A=A-1\n'
        self.Ari_output2 = '@SP\n'+'AM=M-1\n'
        self.Ari_output3 = '@SP\n'+'M=M+1\n'
        if command == 'add':
            self.output = self.Ari_output1 + 'M=M+D\n'
        elif command == 'sub':
            self.output = self.Ari_output1 + 'M=M-D\n'
        elif command == 'neg':
            self.output = self.Ari_output2 + 'M=-M\n' + self.Ari_output3
        elif command == 'eq':
            self.output = self.__convertAriJudgementCmd('JEQ', self.index)
            self.index = self.index + 1
        elif command == 'gt':
            self.output = self.__convertAriJudgementCmd('JGT', self.index)
            self.index = self.index + 1
        elif command == 'lt':
            self.output = self.__convertAriJudgementCmd('JLT', self.index)
            self.index = self.index + 1
        elif command == 'and':
            self.output = self.Ari_output1 + 'M=M&D\n'
        elif command == 'or':
            self.output = self.Ari_output1 + 'M=M|D\n'
        elif command == 'not':
            self.output = self.Ari_output2 + 'M=!M\n' + self.Ari_output3
        # print(self.output)
        self.f.seek(0,2)
        self.f.write(self.output)
        
    def WritePushPop(self, command, segment, index):
        id = str(index)
        if command == 'C_PUSH':
            pushTemp = '@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            if segment == 'CONSTANT':
                self.output = '@'+id+'\n'+'D=A\n'+pushTemp
            elif segment == 'ARGUMENT':
                self.output = '@ARG\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'LOCAL':
                self.output = '@LCL\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'STATIC':
                self.output = '@'+self.vm_file+'.'+id+'\nD=M\n'+pushTemp
            elif segment == 'THIS' or segment == 'THAT':
                self.output = '@'+segment+'\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'POINTER':
                if index == 0:
                    SEG = 'THIS'
                elif index == 1:
                    SEG = 'THAT'
                else:
                    return
                self.output = '@'+SEG+'\n'+'D=M\n'+pushTemp
            elif segment == 'TEMP':
                self.output = '@R5\n'+'D=A\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp  
        elif command == 'C_POP':
            popTemp = '@SP\n'+'AM=M-1\n'+'D=M\n'
            if segment == 'ARGUMENT':
                self.output = '@ARG\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'LOCAL':
                self.output = '@LCL\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'STATIC':
                self.output = popTemp+'@'+self.vm_file+'.'+id+'\nM=D\n'
            elif segment == 'THIS' or segment == 'THAT':
                self.output = '@'+segment+'\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'POINTER':
                if index == 0:
                    SEG = 'THIS'
                elif index == 1:
                    SEG = 'THAT'
                else:
                    return
                self.output = popTemp+'@'+SEG+'\nM=D\n'
            elif segment == 'TEMP':
                self.output = '@R5\n'+'D=A\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
        # print(self.output)
        self.f.seek(0,2)
        self.f.write(self.output)
        
    def close(self):
        self.f.close()
        
    def __convertAriJudgementCmd(self, judgeCmd, index):
        string = '@SP\n'\
            + 'AM=M-1\n'\
            + 'D=M\n'\
            + 'A=A-1\n'\
            + 'D=M-D\n'\
            + '@TRUE' + str(index) + '\n'\
            + 'D;' + judgeCmd + '\n'\
            + '@SP\n'\
            + 'AM=M-1\n'\
            + 'M=0\n'\
            + '@SP\n'\
            + 'M=M+1\n'\
            + '@CONTINUE' + str(index) + '\n'\
            + '0;JMP\n'\
            + '(TRUE' + str(index) + ')\n'\
            + '@SP\n'\
            + 'AM=M-1\n'\
            + 'M=-1\n'\
            + '@SP\n'\
            + 'M=M+1\n'\
            + '(CONTINUE' + str(index) + ')\n'
        return string
        
        