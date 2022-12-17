class AsmParser:
    f = 0
    str = ''
    eof = 0
    cmd_type = ('A_COMMAND', 'C_COMMAND', 'L_COMMAND', 'NONE')
    es_pos = 0
    semi_pos = 0
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
        self.str = self.str.replace(' ','')
        self.str = self.str.replace('\t','')
        self.str = self.str.replace('\n','')
        if self.str[0:2] == '//':
            self.str = ''
        elif '//' in self.str:
            self.str = self.str[0:self.str.find('//')]
        # print(self.str)
    def commandType(self):
        if self.str == '':
            return self.cmd_type[3]
        elif self.str[0] == '@':
            return self.cmd_type[0]
        elif self.str[0] == '(':
            return self.cmd_type[2]
        else:
            return self.cmd_type[1]
    def symbol(self):
        if self.commandType() == 'A_COMMAND':
            return self.str[1:]
        elif self.commandType() == 'L_COMMAND':
            return self.str[1:-1]
        else:
            return ''
    def dest(self):
        if self.commandType() != 'C_COMMAND':
            return ''
        self.es_pos = self.str.find('=')
        if self.es_pos != -1:
            return self.str[0:self.es_pos]
        else:
            return ''
    def comp(self):
        if self.commandType() != 'C_COMMAND':
            return ''
        self.es_pos = self.str.find('=')
        if self.es_pos != -1:
            return self.str[self.es_pos+1:]
        else:
            self.semi_pos = self.str.find(';')
            if self.semi_pos != -1:
                return self.str[0:self.semi_pos]
            else:
                return ''
    def jump(self):
        if self.commandType() != 'C_COMMAND':
            return ''
        self.semi_pos = self.str.find(';')
        if self.semi_pos == -1:
            return ''
        return self.str[self.semi_pos+1:]
    