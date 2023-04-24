class CodeWriter:
    f = 0
    vm_file = ''
    output = ''
    Ari_output1 = ''
    Ari_output2 = ''
    Ari_output3 = ''
    index = 0
    call_index = 0
    def __init__(self, output_filepath) -> None:
        self.f = open(output_filepath, 'w+')
        
    def setFileName(self, vmFileName):
        self.vm_file = vmFileName
        self.f.write('//'+self.vm_file+'\n')
        
    def writeInit(self):
        self.output = '@256\n' + 'D=A\n' + '@SP\n' + 'M=D\n'
        self.output += self.__encodeCall('Sys.init', 0)
        self.__writeOutputToTail()
           
    def writeLabel(self, label):
        self.output = self.__encodeLabel(label)
        self.__writeOutputToTail()
        
    def writeGoto(self, label):
        self.output = self.__encodeGoto(label)
        self.__writeOutputToTail()
        
    def writeIf(self, label):
        self.output = self.__encodeIfGoto(label)
        self.__writeOutputToTail()

    def writeCall(self, functionName, numArgs):
        self.output = self.__encodeCall(functionName, numArgs)
        self.call_index = self.call_index + 1
        self.__writeOutputToTail()
    
    def writeReturn(self):
        self.output = self.__encodeReturn()
        self.__writeOutputToTail()
    
    def writeFunction(self, functionName, numLocals):
        self.output = self.__encodeFunction(functionName, numLocals)
        self.__writeOutputToTail()
        
    def writeArithmetic(self, command):
        self.output = self.__encodeArithmetic(command)
        # print(self.output)
        self.__writeOutputToTail()
        
    def WritePushPop(self, command, segment, index):
        self.output = self.__encodePushPop(command, segment, index)
        # print(self.output)
        self.__writeOutputToTail()
        
    def close(self):
        self.f.close()
        
    def __writeOutputToTail(self):
        self.f.seek(0,2)
        self.f.write(self.output)       
      
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
        
    def __encodeLabel(self, label):
        output = '(' + label + ')\n'
        return output
    
    def __encodeGoto(self, label):
        output = '@' + label + '\n' + '0;JMP\n'
        return output
    
    def __encodeIfGoto(self, label):
        output = '@SP\n' + 'AM=M-1\n' + 'D=M\n' + '@' + label + '\n' +'D;JNE\n'
        return output
    
    def __encodeCall(self, functionName, numArgs):
        # push return-address
        output = '@'+functionName+'_RA'+str(self.call_index)+'\n'+'D=A\n'\
                    +'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
        # push LCL
        output += '@LCL\n'+'D=M\n'\
                    +'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
        # push ARG
        output += '@ARG\n'+'D=M\n'\
                    +'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
        # push THIS
        output += '@THIS\n'+'D=M\n'\
                    +'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
        # push THAT
        output += '@THAT\n'+'D=M\n'\
                    +'@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
        # ARG = SP-numArgs-5
        ## calculate (numArgs + 5)
        output += '@'+str(numArgs)+'\n'+'D=A\n'\
                        +'@5\n'+'D=D+A\n'
        ## calculate SP=SP-D
        output += '@SP\n'+'D=M-D\n'
        ## ARG = SP
        output += '@ARG\n'+'M=D\n'               
        # LCL = SP
        output += '@SP\n'+'D=M\n'\
                    +'@LCL\n'+'M=D\n'
        #goto functionName
        output += self.__encodeGoto(functionName)
        #(return-address)
        output += self.__encodeLabel(functionName+'_RA'+str(self.call_index))
        return output
    
    def __encodeReturn(self):
        # FRAME = LCL
        output = '@LCL\n' + 'D=M\n' + '@R13\n' + 'M=D\n'
        # RET = *(FRAME-5)
        output += '@5\n' + 'A=D-A\n' + 'D=M\n' + '@R14\n' + 'M=D\n'
        # *ARG = pop()
        output += '@SP\n'+'AM=M-1\n'+'D=M\n'\
                    + '@ARG\n' + 'A=M\n' + 'M=D\n'
        # SP = ARG + 1
        output += '@ARG\n' + 'D=M+1\n'\
                    + '@SP\n' + 'M=D\n'
        # THAT = *(FRAME-1)
        output += '@R13\n' + 'D=M-1\n' + 'AM=D\n' + 'D=M\n'\
                    + '@THAT\n' + 'M=D\n'
        # THIS = *(FRAME-2)
        output += '@R13\n' + 'D=M-1\n' + 'AM=D\n' + 'D=M\n'\
                    + '@THIS\n' + 'M=D\n'
        # ARG = *(FRAME-3)
        output += '@R13\n' + 'D=M-1\n' + 'AM=D\n' + 'D=M\n'\
                    + '@ARG\n' + 'M=D\n'
        # LCL = *(FRAME-4)
        output += '@R13\n' + 'D=M-1\n' + 'AM=D\n' + 'D=M\n'\
                    + '@LCL\n' + 'M=D\n'
        # goto ret
        output += '@R14\n' + 'A=M\n' + '0;JMP\n'     
        return output
    
    def __encodeFunction(self, functionName, numLocals):
        output = self.__encodeLabel(functionName)
        iter = numLocals
        while iter != 0:
            output += self.__encodePushPop('C_PUSH', 'CONSTANT', 0)
            iter = iter - 1
        return output
    
    def __encodeArithmetic(self, command):
        self.Ari_output1 = '@SP\n'+'AM=M-1\n'+'D=M\n'+'A=A-1\n'
        self.Ari_output2 = '@SP\n'+'AM=M-1\n'
        self.Ari_output3 = '@SP\n'+'M=M+1\n'
        output = ''
        if command == 'add':
            output = self.Ari_output1 + 'M=M+D\n'
        elif command == 'sub':
            output = self.Ari_output1 + 'M=M-D\n'
        elif command == 'neg':
            output = self.Ari_output2 + 'M=-M\n' + self.Ari_output3
        elif command == 'eq':
            output = self.__convertAriJudgementCmd('JEQ', self.index)
            self.index = self.index + 1
        elif command == 'gt':
            output = self.__convertAriJudgementCmd('JGT', self.index)
            self.index = self.index + 1
        elif command == 'lt':
            output = self.__convertAriJudgementCmd('JLT', self.index)
            self.index = self.index + 1
        elif command == 'and':
            output = self.Ari_output1 + 'M=M&D\n'
        elif command == 'or':
            output = self.Ari_output1 + 'M=M|D\n'
        elif command == 'not':
            output = self.Ari_output2 + 'M=!M\n' + self.Ari_output3
        return output
    
    def __encodePushPop(self, command, segment, index):
        id = str(index)
        output = ''
        if command == 'C_PUSH':
            pushTemp = '@SP\n'+'A=M\n'+'M=D\n'+'@SP\n'+'M=M+1\n'
            if segment == 'CONSTANT':
                output = '@'+id+'\n'+'D=A\n'+pushTemp
            elif segment == 'ARGUMENT':
                output = '@ARG\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'LOCAL':
                output = '@LCL\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'STATIC':
                output = '@'+self.vm_file+'.'+id+'\nD=M\n'+pushTemp
            elif segment == 'THIS' or segment == 'THAT':
                output = '@'+segment+'\n'+'D=M\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp
            elif segment == 'POINTER':
                if index == 0:
                    SEG = 'THIS'
                elif index == 1:
                    SEG = 'THAT'
                else:
                    return
                output = '@'+SEG+'\n'+'D=M\n'+pushTemp
            elif segment == 'TEMP':
                output = '@R5\n'+'D=A\n'+'@'+id+'\n'+'A=D+A\n'+'D=M\n'+pushTemp  
        elif command == 'C_POP':
            popTemp = '@SP\n'+'AM=M-1\n'+'D=M\n'
            if segment == 'ARGUMENT':
                output = '@ARG\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'LOCAL':
                output = '@LCL\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'STATIC':
                output = popTemp+'@'+self.vm_file+'.'+id+'\nM=D\n'
            elif segment == 'THIS' or segment == 'THAT':
                output = '@'+segment+'\n'+'D=M\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
            elif segment == 'POINTER':
                if index == 0:
                    SEG = 'THIS'
                elif index == 1:
                    SEG = 'THAT'
                else:
                    return
                output = popTemp+'@'+SEG+'\nM=D\n'
            elif segment == 'TEMP':
                output = '@R5\n'+'D=A\n'+'@'+id+'\n'+'D=D+A\n'+'@R13\n'+'M=D\n'\
                    + popTemp + '@R13\n'+'A=M\n'+'M=D\n'
        return output