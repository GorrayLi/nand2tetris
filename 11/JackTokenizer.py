import re

class JackTokenizer:
    tokensAll = []
    currentToken = ''
    keyWordList = ['class', 'constructor', 'function', 'method', 'field', 'static', 'var', 'int', 'char', 'boolean',\
                    'void', 'true', 'false', 'null', 'this', 'let', 'do', 'if', 'else', 'while', 'return']
    symbolOpList = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~']
    def __init__(self, inputfile) -> None:
        with open(inputfile, 'r') as f:
            content = f.read()
        # Remove single-line comments (//)
        content = re.sub(r'//.*', '', content)
        # Remove multiline comments (/* ... */)
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)        
        # tokenize using regex
        self.tokensAll = self.__tokenize(content)
        
    def hasMoreTokens(self):
        if self.tokensAll == []:
            return False
        else:
            return True
        
    def advance(self):
        self.currentToken = self.tokensAll[0]
        del self.tokensAll[0]
        
    def tokenType(self):
        if self.currentToken in self.keyWordList:
            return 'KEYWORD'
        elif self.currentToken in self.symbolOpList:
            return 'SYMBOL'
        elif self.__isIntConstant(self.currentToken):
            return 'INT_CONST'
        elif self.__isStringConstant(self.currentToken):
            return 'STRING_CONST'
        elif self.__isIdentifier(self.currentToken):
            return 'IDENTIFIER'
        else:
            return 'UNKNOWN_TYPE'

    def keyWord(self):
        if self.tokenType() == 'KEYWORD':
            return self.currentToken
        else:
            return 'ERROR'
    
    def symbol(self):
        if self.tokenType() == 'SYMBOL':
            return self.currentToken
        else:
            return 'ERROR'        
    
    def identifier(self):
        if self.tokenType() == 'IDENTIFIER':
            return self.currentToken
        else:
            return 'ERROR'   
    
    def intVal(self):
        if self.tokenType() == 'INT_CONST':
            val = int(self.currentToken)
            if val >= 0 and val <=32767:
                return val
            else:
                return -1
        else:
            return -2 
    
    def stringVal(self):
        if self.tokenType() == 'STRING_CONST':
            return self.currentToken[1:-1]
        else:
            return 'ERROR'

    def __isIntConstant(self, text):
        pattern = r"^[0-9]*$"
        match = re.match(pattern, text)
        return match is not None

    def __isStringConstant(self, text):
        pattern = r"^\"[^\"\n]*\"$"
        match = re.match(pattern, text)
        return match is not None

    def __isIdentifier(self, text):
        pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"
        match = re.match(pattern, text)
        return match is not None
    
    def __tokenize(self, text):
        pattern = fr'\b({"|".join(self.keyWordList)})\b|\b(\d+)\b|("[^"\n]*")|\b(\w+)\b|([{"".join(re.escape(s) for s in self.symbolOpList)}])'
        tokens = re.findall(pattern, text)
        return [token[0] if token[0] \
                else token[1] if token[1]\
                else token[2] if token[2]\
                else token[3] if token[3]\
                else token[4] for token in tokens] 
    