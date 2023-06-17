class SymbolTable:
    table = {}
    kindCnt = {}
    
    def __init__(self) -> None:
        self.table = {}
        self.kindCnt['STATIC'] = 0
        self.kindCnt['FIELD'] = 0
        self.kindCnt['ARG'] = 0
        self.kindCnt['VAR'] = 0
    
    def startSubroutine(self):
        self.table.clear()
        self.kindCnt['STATIC'] = 0
        self.kindCnt['FIELD'] = 0
        self.kindCnt['ARG'] = 0
        self.kindCnt['VAR'] = 0
    
    def Define(self, name, type, kind):
        self.table[name] = (type, kind, self.kindCnt[kind])
        self.kindCnt[kind] = self.kindCnt[kind] + 1
    
    def VarCount(self, kind):
        if kind not in self.kindCnt:
            return 0
        return self.kindCnt[kind]
    
    def KindOf(self, name):
        if name not in self.table:
            return 'NONE'
        value = self.table[name]
        kind = value[1]
        if kind != 'STATIC' and kind != 'FIELD'\
            and kind != 'ARG' and kind != 'VAR':
            kind = 'NONE'
        return kind
        
    def TypeOf(self, name):
        if name not in self.table:
            return 'NONE'
        value = self.table[name]
        return value[0]
    
    def indexOf(self, name):
        if name not in self.table:
            return 'NONE'
        value = self.table[name]
        return value[2]