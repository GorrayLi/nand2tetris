from xml.dom import minidom
from SymbolTable import SymbolTable
from VMWriter import VMWriter
import os

class CompilationEngine:
    tokenStream = []
    outputFilePath = ''
    index = 0
    outputDoc = 0
    ClassScopeSymTbl = 0
    MethodScopeSymTbl = 0
    JackVmWriter = 0
    CurrentClassName = ''
    IfLabelId = 0
    WhileLabelId = 0
    opCmd = {'+':'add', '-':'sub', '&amp':'and', '|':'or',
             '&lt':'lt', '&gt':'gt', '=':'eq', 
             '*':'call Math.multiply 2',
             '/':'call Math.divide 2'}
    def __init__(self, inputfile, outputfile) -> None:
        dom = minidom.parse(inputfile)
        root = dom.documentElement
        self.tokenStream = []
        for child in root.childNodes:
            if child.nodeType == child.ELEMENT_NODE:
                token = (child.tagName, child.firstChild.data)
                self.tokenStream.append(token)
        self.outputFilePath = outputfile
        self.outputDoc = minidom.Document()
        self.ClassScopeSymTbl = SymbolTable()
        self.MethodScopeSymTbl = SymbolTable()
        self.JackVmWriter = VMWriter(self.outputFilePath)
    
    def CompileClass(self):
        root = self.outputDoc.createElement("class")
        self.outputDoc.appendChild(root)
        
        # get keyword 'class'
        key, val = self.__getNextToken(True)
        if key != 'keyword' or val != 'class':
            print("error: not a class")
        self.__addNodeToParseTreeDoc(root, key, val)
        
        # get className
        key, val = self.__getNextToken(True)
        if key != 'identifier':
            print("error: not a name")
        self.CurrentClassName = val
        self.__addNodeToParseTreeDoc(root, key, val)
        
        # get '{'
        key, val = self.__getNextToken(True)
        if key != 'symbol':
            print("error: missing symbol '{'.")
        self.__addNodeToParseTreeDoc(root, key, val)           
                
        # need a lookahead to determine what's next
        key, val = self.__getNextToken(False)
        while val != '}':
            if val == 'static' or val == 'field':
                class_val_dec = self.outputDoc.createElement('classVarDec')
                self.CompileClassVarDec(class_val_dec)
                root.appendChild(class_val_dec)
            elif val == 'constructor' or val == 'function' or val == 'method':
                subroutine_dec = self.outputDoc.createElement('subroutineDec')
                self.CompileSubroutine(subroutine_dec)
                root.appendChild(subroutine_dec)
            elif key == '' and val == '':
                print("error: invalid token stream")
                return
            else:
                print("error: invalid class member")
                return
            key, val = self.__getNextToken(False)
            
        # add '}' symbol
        self.__addNodeToParseTreeDoc(root, key, val)
        
        # write parse tree xml file
        doc_str = self.outputDoc.toprettyxml(indent="\t", newl="\n")
        fbase, fext = os.path.splitext(self.outputFilePath)
        filename_xml = fbase + '.xml'
        with open(filename_xml, "w") as file:
            file.write(doc_str)
    
    def CompileClassVarDec(self, node):
        # get keyword ('static' | 'field')
        key, val = self.__getNextToken(True)
        if key == 'keyword' and (val == 'static' or val == 'field'):
            symKind = val.upper()
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: not 'static' or 'field'.")
        
        # get type ('int' | 'char' | 'boolean' | className)
        key, val = self.__getNextToken(True)
        if val == 'int' or val == 'char' or val == 'boolean' or key == 'identifier':
            symType = val
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: invalid variable type")
        
        # get var name
        key, val = self.__getNextToken(True)
        while val != ';':
            if key == 'identifier':
                symName = val
                self.ClassScopeSymTbl.Define(symName, symType, symKind)
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: invalid variable name")
                return
            key, val = self.__getNextToken(True)
            if val == ',':
                self.__addNodeToParseTreeDoc(node, key, val)
                key, val = self.__getNextToken(True)
            elif val != ';':
                print("error: vars should be seperated by ','.")
                return
            
        # add ';' symbol
        self.__addNodeToParseTreeDoc(node, key, val)
    
    def CompileSubroutine(self, node):
        self.MethodScopeSymTbl.startSubroutine()
        numLocals = 0 
        # get keyword ('constructor' | 'function' | 'method'))
        key, val = self.__getNextToken(True)
        if key == 'keyword' and (val == 'constructor'\
            or val == 'function' or val == 'method'):
            self.__addNodeToParseTreeDoc(node, key, val)
            SubroutineType = val
        else:
            print("error: not 'constructor', 'function' or 'method'.")
            return
        
        # get type 'void' | ('int' | 'char' | 'boolean' | className)
        key, val = self.__getNextToken(True)
        if val == 'void' or val == 'int' or val == 'char'\
            or val == 'boolean' or key == 'identifier':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: invalid return type")
            return
        
        # get subroutineName
        key, val = self.__getNextToken(True)
        if key == 'identifier':
            SubroutineName = self.CurrentClassName + '.' + val
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: not a subroutineName")
            return
        
        # get symbol '('
        key, val = self.__getNextToken(True)
        if val == '(':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no '(' after subroutineName")
            return
        
        # get parameterList
        parameterList = self.outputDoc.createElement('parameterList')
        self.compileParameterList(parameterList)
        node.appendChild(parameterList)
        
        # get symbol ')'
        key, val = self.__getNextToken(True)
        if val == ')':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no ')' after subroutineName")
            return
        
        # get subroutineBody
        subroutineBody = self.outputDoc.createElement('subroutineBody')
        # get symbol '{'
        key, val = self.__getNextToken(True)
        if val == '{':
            self.__addNodeToParseTreeDoc(subroutineBody, key, val)
        else:
            print("error: no '{' at the beginning subroutineBody")
            return
        # get vars declaration in subroutineBody
        key, val = self.__getNextToken(False)
        while val == 'var':
            numLocals = numLocals + 1
            varDec = self.outputDoc.createElement('varDec')
            self.compileVarDec(varDec)
            subroutineBody.appendChild(varDec)
            key, val = self.__getNextToken(False)

        # write function vm statement.
        self.JackVmWriter.writeFunction(SubroutineName, numLocals)
        if SubroutineType == 'constructor':
            fieldNumInClass = self.ClassScopeSymTbl.VarCount('field')
            self.JackVmWriter.WritePush('constant', fieldNumInClass)
            self.JackVmWriter.writeCall('Memory.alloc', 1)
            self.JackVmWriter.WritePop('pointer', 0)
        elif SubroutineType == 'method':
            self.JackVmWriter.WritePush('argument', 0)
            self.JackVmWriter.WritePop('pointer', 0)
        
        # get statements
        statements = self.outputDoc.createElement('statements')
        self.compileStatements(statements)
        subroutineBody.appendChild(statements)
        # get symbol '}'
        key, val = self.__getNextToken(True)
        if val == '}':
            self.__addNodeToParseTreeDoc(subroutineBody, key, val)
        else:
            print("error: no '}' at the end subroutineBody")
            return
        node.appendChild(subroutineBody)
    
    def compileParameterList(self, node):
        # put this into symbol table
        self.MethodScopeSymTbl.Define('this', self.CurrentClassName, 'ARG')
        
        # get next token to check if parameter empty 
        key, val = self.__getNextToken(False)
        if val == ')':
            return
        
        # get type ('int' | 'char' | 'boolean' | className)
        key, val = self.__getNextToken(False)
        while val != ')':
            if val == 'int' or val == 'char' or val == 'boolean' or key == 'identifier':
                key, val = self.__getNextToken(True)
                symType = val
                self.__addNodeToParseTreeDoc(node, key, val)
            # get varName
            key, val = self.__getNextToken(True)
            if key == 'identifier':
                symName = val
                self.MethodScopeSymTbl.Define(symName, symType, 'ARG')
                self.__addNodeToParseTreeDoc(node, key, val)
            # check ','
            key, val = self.__getNextToken(False)
            if val == ',':
                key, val = self.__getNextToken(True)
                self.__addNodeToParseTreeDoc(node, key, val)
                key, val = self.__getNextToken(False)
            elif val != ')':
                print("error: vars should be seperated by ','.")
                return
    
    def compileVarDec(self, node):
        # get keyword 'var'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'var':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'var'")
            return

        # get type ('int' | 'char' | 'boolean' | className)
        key, val = self.__getNextToken(True)
        if val == 'int' or val == 'char' or val == 'boolean' or key == 'identifier':
            symType = val
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: invalid variable type")
            return
        
        # get var name
        key, val = self.__getNextToken(True)
        while val != ';':
            if key == 'identifier':
                symName = val
                self.MethodScopeSymTbl.Define(symName, symType, 'VAR')
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: invalid variable name")
                return
            key, val = self.__getNextToken(True)
            if val == ',':
                self.__addNodeToParseTreeDoc(node, key, val)
                key, val = self.__getNextToken(True)
            elif val != ';':
                print("error: vars should be seperated by ','.")
                return
            
        # add ';' symbol
        self.__addNodeToParseTreeDoc(node, key, val)            
    
    def compileStatements(self, node):
        key, val = self.__getNextToken(False)
        while val != '}':
            if val == 'let':
                letStatement = self.outputDoc.createElement('letStatement')
                self.compileLet(letStatement)
                node.appendChild(letStatement)
            elif val == 'if':
                ifStatement = self.outputDoc.createElement('ifStatement')
                self.compileIf(ifStatement)
                node.appendChild(ifStatement)
            elif val == 'while':
                whileStatement = self.outputDoc.createElement('whileStatement')
                self.compileWhile(whileStatement)
                node.appendChild(whileStatement)
            elif val == 'do':
                doStatement = self.outputDoc.createElement('doStatement')
                self.compileDo(doStatement)
                node.appendChild(doStatement)
            elif val == 'return':
                returnStatement = self.outputDoc.createElement('returnStatement')
                self.compileReturn(returnStatement)
                node.appendChild(returnStatement)
            else:
                return
            key, val = self.__getNextToken(False)
                    
    def compileDo(self, node):
        # get 'do'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'do':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'do'")
            return
        
        # subroutineCall
        self.compilesubroutineCall(node)
        
        # get ';'
        key, val = self.__getNextToken(True)
        if val == ';':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no ';' at the end")        
        
    def compilesubroutineCall(self, node):
        FuncInSameObj = False
        isObjMethod = False
        # get subroutineName | className | varName
        key, val = self.__getNextToken(True)
        if key == 'identifier':
            self.__addNodeToParseTreeDoc(node, key, val)
            namepart1 = val
            tVarSeg, tVarIndex, tVarType = self.__getIndentifierInfo(val)
            if tVarSeg != '':
                isObjMethod = True
        else:
            print("error: not a name")
            return
        
        key, val = self.__getNextToken(False)
        if val == '.':
            # get symbol '.'
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            
            # subroutineName
            key, val = self.__getNextToken(True)
            if key == 'identifier':
                self.__addNodeToParseTreeDoc(node, key, val)
                namepart2 = val
            else:
                print("error: not a subroutineName")
                return
            subroutineName = namepart1 + '.' + namepart2
        elif val == '(':
            subroutineName = namepart1
            FuncInSameObj = True
        else:
            return
            
        # get symbol '('
        key, val = self.__getNextToken(True)
        self.__addNodeToParseTreeDoc(node, key, val)
        
        # push this pointer
        if isObjMethod == True:
            self.JackVmWriter.WritePush(tVarSeg, tVarIndex)
        elif FuncInSameObj == True:
            self.JackVmWriter.WritePush('pointer', 0)

        # get expressionList
        expressionList = self.outputDoc.createElement('expressionList')
        nargs = self.compileExpressionList(expressionList)
        node.appendChild(expressionList)
        if isObjMethod == True or FuncInSameObj == True:
            nargs = nargs + 1
        
        # get symbol ')'
        key, val = self.__getNextToken(True)
        if val == ')':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no ')' after expressionList")
            return
        # write func call
        self.JackVmWriter.writeCall(subroutineName, nargs)
    
    def compileLet(self, node):
        # get 'let'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'let':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'let'")
            return       

        # varName
        key, val = self.__getNextToken(True)
        if key == 'identifier':
            # get varName segment and index
            tVarSeg, tVarIndex, tVarType = self.__getIndentifierInfo(val)
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: missing varName")
            return

        # check if it's array or single var
        key, val = self.__getNextToken(False)
        if val == '[':
            # write array base addr
            self.JackVmWriter.WritePush(tVarSeg, tVarIndex)
            # add '['
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            
            # 'expression'
            expression = self.outputDoc.createElement('expression')
            self.compileExpression(expression)
            node.appendChild(expression)
            
            # add ']'
            key, val = self.__getNextToken(True)
            if val == ']':
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: missing ']'.")
                return
            # write 'add': add expression value to base addr
            self.JackVmWriter.WriteArithmetic('add')
        
        # add '='
        key, val = self.__getNextToken(True)
        if val == '=':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no '=' in let stm.")
            return
        
        # 'expression'
        expression = self.outputDoc.createElement('expression')
        self.compileExpression(expression)
        node.appendChild(expression)
        
        # add ';'
        key, val = self.__getNextToken(True)
        if val == ';':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no ';' at the end of let stm.")
            return
        
        # write assignment part
        if tVarType == 'Array':
            self.JackVmWriter.WritePop('temp', 0)
            self.JackVmWriter.WritePop('pointer', 1)
            self.JackVmWriter.WritePush('temp', 0)
            self.JackVmWriter.WritePop('that', 0)
        else:
            self.JackVmWriter.WritePop(tVarSeg, tVarIndex)
    
    def compileWhile(self, node):
        WhileFalseLabel = 'WHILE_FALSE'
        LoopLabel = 'LOOP'
        idx = self.WhileLabelId
        self.WhileLabelId = self.WhileLabelId + 1
        # get 'while'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'while':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'while'")
            return
        # write loop label
        self.JackVmWriter.WriteLabel(LoopLabel+str(idx))
        # get '('
        key, val = self.__getNextToken(True)
        if val == '(':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no '(' after while.")
            return        
        # expression    
        expression = self.outputDoc.createElement('expression')
        self.compileExpression(expression)
        node.appendChild(expression)
        # get ')'
        key, val = self.__getNextToken(True)
        if val == ')':
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WriteArithmetic('not')
            self.JackVmWriter.WriteIf(WhileFalseLabel+str(idx))
        else:
            print("error: missing ')' after condition expression.")
            return             

        # get '{'
        key, val = self.__getNextToken(True)
        if val == '{':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: missing '{'.")
            return        
        # statements    
        statements = self.outputDoc.createElement('statements')
        self.compileStatements(statements)
        node.appendChild(statements)
        # get '}'
        key, val = self.__getNextToken(True)
        if val == '}':
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WriteGoto(LoopLabel+str(idx))
        else:
            print("error: missing '}'.")
            return
        self.JackVmWriter.WriteLabel(WhileFalseLabel+str(idx))
    
    def compileReturn(self, node):
        # get 'return'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'return':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'return'")
            return

        # check if return val exists.
        key, val = self.__getNextToken(False)
        if val != ';':
            # 'expression'
            expression = self.outputDoc.createElement('expression')
            self.compileExpression(expression)
            node.appendChild(expression)
        else:
            self.JackVmWriter.WritePush('constant', 0)
        
        # ';'
        key, val = self.__getNextToken(True)
        if val == ';':
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.writeReturn()
        else:
            print("error: no ';' at the end of let stm.")
            return              
    
    def compileIf(self, node):
        IfFalseLabel = 'IF_FALSE'
        EndLabel = "IF_END"
        Idx = self.IfLabelId
        self.IfLabelId = self.IfLabelId + 1
        # get 'if'
        key, val = self.__getNextToken(True)
        if key == 'keyword' and val == 'if':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: keyword not 'if'")
            return
        # get '('
        key, val = self.__getNextToken(True)
        if val == '(':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: no '(' after if.")
            return        
        # expression    
        expression = self.outputDoc.createElement('expression')
        self.compileExpression(expression)
        node.appendChild(expression)
        # get ')'
        key, val = self.__getNextToken(True)
        if val == ')':
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WriteArithmetic('not')
            self.JackVmWriter.WriteIf(IfFalseLabel+str(Idx))
        else:
            print("error: missing ')' after condition expression.")
            return             

        # get '{'
        key, val = self.__getNextToken(True)
        if val == '{':
            self.__addNodeToParseTreeDoc(node, key, val)
        else:
            print("error: missing '{'.")
            return        
        # statements    
        statements = self.outputDoc.createElement('statements')
        self.compileStatements(statements)
        node.appendChild(statements)
        # get '}'
        key, val = self.__getNextToken(True)
        if val == '}':
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WriteGoto(EndLabel+str(Idx))
        else:
            print("error: missing '}'.")
            return
        
        self.JackVmWriter.WriteLabel(IfFalseLabel+str(Idx))
        # check if there's an else branch
        key, val = self.__getNextToken(False)
        if key == 'keyword' and val == 'else':
            # get 'else'
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            # get '{'
            key, val = self.__getNextToken(True)
            if val == '{':
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: missing '{'.")
                return        
            # statements    
            statements = self.outputDoc.createElement('statements')
            self.compileStatements(statements)
            node.appendChild(statements)
            # get '}'
            key, val = self.__getNextToken(True)
            if val == '}':
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: missing '}'.")
                return
        self.JackVmWriter.WriteLabel(EndLabel+str(Idx))
    
    def compileExpression(self, node):
        # term
        term = self.outputDoc.createElement('term')
        self.compileTerm(term)
        node.appendChild(term)
        
        # check op
        key, val = self.__getNextToken(False)
        while val == '+' or val == '-' or val == '*' or val == '/' or val == '&amp'\
            or val == '|' or val == '&lt'  or val == '&gt' or val == '=':
            op = self.opCmd[val]
            # op
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            #term
            term = self.outputDoc.createElement('term')
            self.compileTerm(term)
            node.appendChild(term)            
            key, val = self.__getNextToken(False)
            
            #write operation
            self.JackVmWriter.WriteArithmetic(op)
    
    def compileExpressionList(self, node):
        # check if expressionlist empty
        key, val = self.__getNextToken(False)
        nExp = 0
        while val != ')':
            # 'expression'
            expression = self.outputDoc.createElement('expression')
            self.compileExpression(expression)
            node.appendChild(expression)
            nExp = nExp + 1
            
            # check if ',' followed.
            key, val = self.__getNextToken(False)
            if val == ',':
                key, val = self.__getNextToken(True)
                self.__addNodeToParseTreeDoc(node, key, val)
                key, val = self.__getNextToken(False)
            elif val != ')':
                print("error: expressions should be seperated by ','.")
                return -1
        return nExp
    
    def compileTerm(self, node):
        # lookahead next token to determine which alternative.
        key, val = self.__getNextToken(False)
        if key == 'integerConstant':
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WritePush('constant', int(val))
        elif key == 'stringConstant':
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            stringValue = val
            strLength = len(stringValue)
            self.JackVmWriter.WritePush('constant', strLength)
            self.JackVmWriter.writeCall('String.new', 1)
            for char in stringValue:
                self.JackVmWriter.WritePush('constant', char)
                self.JackVmWriter.writeCall('String.appendChar', 2)
        elif val == 'true':
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WritePush('constant', 1)
            self.JackVmWriter.WriteArithmetic('neg')
        elif val == 'false' or val == 'null':
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WritePush('constant', 0)                 
        elif val == 'this':
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            self.JackVmWriter.WritePush('pointer', 0)
        elif key == 'identifier':
            # look ahead 2nd token to alter
            # varName | varName '[' expression ']' | subroutineCall
            self.index = self.index + 1
            key, val = self.__getNextToken(False)
            self.index = self.index - 1
            if val == '[':
                # varName '[' expression ']'
                # varName
                key, val = self.__getNextToken(True)
                self.__addNodeToParseTreeDoc(node, key, val)
                # get varName segment, index.
                tVarSeg, tVarIndex, tVarType = self.__getIndentifierInfo(val)
                # push varName.
                self.JackVmWriter.WritePush(tVarSeg, tVarIndex)
                # '['
                key, val = self.__getNextToken(True)
                self.__addNodeToParseTreeDoc(node, key, val)
                # expression
                expression = self.outputDoc.createElement('expression')
                self.compileExpression(expression)
                node.appendChild(expression)
                # ]
                key, val = self.__getNextToken(True)
                if val == ']':
                    self.__addNodeToParseTreeDoc(node, key, val)
                    self.JackVmWriter.WriteArithmetic('add')
                    self.JackVmWriter.WritePop('pointer', 1)
                    self.JackVmWriter.WritePush('that', 0)
                else:
                    print("error: missing ']' in array.")
            elif val == '(' or val == '.':
                # subroutineCall
                self.compilesubroutineCall(node)     
            else:
                # varName
                key, val = self.__getNextToken(True)
                self.__addNodeToParseTreeDoc(node, key, val)
                # get varName segment, index.
                tVarSeg, tVarIndex, tVarType = self.__getIndentifierInfo(val)
                # push varName.
                self.JackVmWriter.WritePush(tVarSeg, tVarIndex)
        elif val == '(':
            # '(' expression ')'
            # '('
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            # expression
            expression = self.outputDoc.createElement('expression')
            self.compileExpression(expression)
            node.appendChild(expression)
            # ')'
            key, val = self.__getNextToken(True)
            if val == ')':
                self.__addNodeToParseTreeDoc(node, key, val)
            else:
                print("error: missing ')' after expression.")
        elif val == '-' or val == '~':
            # unaryOp term
            # unaryOp
            key, val = self.__getNextToken(True)
            self.__addNodeToParseTreeDoc(node, key, val)
            unaryOp = val
            # term
            term = self.outputDoc.createElement('term')
            self.compileTerm(term)
            node.appendChild(term)
            # push operation
            if unaryOp == '-':
                self.JackVmWriter.WriteArithmetic('neg')
            else:
                self.JackVmWriter.WriteArithmetic('not')               
    
    def __getNextToken(self, advance):
        if self.index == len(self.tokenStream):
            return ('','')
        currToken = self.tokenStream[self.index]
        if advance:
            self.index = self.index + 1
        return currToken
    
    def __addNodeToParseTreeDoc(self, fatherNode, tag, text):
        new_element = self.outputDoc.createElement(tag)
        text_node = self.outputDoc.createTextNode(text)
        new_element.appendChild(text_node)
        fatherNode.appendChild(new_element)
    
    def __getIndentifierInfo(self, name):
        tVarKind = self.MethodScopeSymTbl.KindOf(name)
        tVarSeg = ''
        if tVarKind != 'NONE':
            if tVarKind == 'ARG':
                tVarSeg = 'argument'
            elif tVarKind == 'VAR':
                tVarSeg = 'local' 
            tVarIndex = self.MethodScopeSymTbl.indexOf(name)
            tVarType = self.MethodScopeSymTbl.TypeOf(name)
        else:
            tVarKind = self.ClassScopeSymTbl.KindOf(name)     
            if tVarKind == 'STATIC':
                tVarSeg = 'static'
            elif tVarKind == 'FIELD':
                tVarSeg = 'this'
            tVarIndex = self.ClassScopeSymTbl.indexOf(name)
            tVarType = self.ClassScopeSymTbl.TypeOf(name)
        return (tVarSeg, tVarIndex, tVarType)