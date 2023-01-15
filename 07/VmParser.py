class VmParser:
    f = 0
    str = ''
    eof = 0
    cmd_type = ('C_ARITHMETIC', 'C_PUSH', 'C_POP', 'C_LABEL',
                'C_GOTO', 'C_IF', 'C_FUNCTION', 'C_RETURN', 'C_CALL', 'NONE')
    cmd_content = []
    arithmetic_cmds = ['add', 'sub', 'neg', 'eq', 'gt', 'lt', 'and', 'or', 'not']
    def __init__(self, filepath) -> None:
        self.f = open(filepath, 'r')
        self.f.seek(0, 2)
        self.eof = self.f.tell()
        self.f.seek(0, 0)
    def hasMoreCommands(self):
        if self.f.tell() < self.eof:
            return True
        else:
            self.f.close()
            return False
    def advance(self):
        self.str = self.f.readline()
        # remove space, table, enter
        if self.str[0:2] == '//':
            self.str = ''
        elif '//' in self.str:
            self.str = self.str[0:self.str.find('//')]
        # print(self.str)
        self.cmd_content = self.str.split()
        # print(self.cmd_content)
    def commandType(self):
        if self.cmd_content == []:
            return self.cmd_type[9]
        elif (self.cmd_content[0] in self.arithmetic_cmds):
            return self.cmd_type[0]
        elif self.cmd_content[0] == 'push':
            return self.cmd_type[1]
        elif self.cmd_content[0] == 'pop':
            return self.cmd_type[2]
        elif self.cmd_content[0] == 'label':
            return self.cmd_type[3]
        elif self.cmd_content[0] == 'goto':
            return self.cmd_type[4]
        elif self.cmd_content[0] == 'if-goto':
            return self.cmd_type[5]
        elif self.cmd_content[0] == 'function':
            return self.cmd_type[6]
        elif self.cmd_content[0] == 'return':
            return self.cmd_type[7]
        elif self.cmd_content[0] == 'call':
            return self.cmd_type[8]
    def arg1(self):
        if self.commandType() == 'C_RETURN':
            return 'err'
        elif self.commandType() == 'C_ARITHMETIC':
            return self.cmd_content[0]
        else:
            return self.cmd_content[1]
    def arg2(self):
        if (self.commandType() != 'C_PUSH'
            and self.commandType() != 'C_POP'
            and self.commandType() != 'C_FUNCTION'
            and self.commandType() != 'C_CALL'):
            return -1
        return int(self.cmd_content[2])
        