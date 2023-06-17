import sys
import os
from JackTokenizer import JackTokenizer
from CompilationEngine import CompilationEngine
from SymbolTable import SymbolTable
import xml.dom.minidom

file_path = sys.argv[1]
output_path = sys.argv[2]

# JackCompile func
def JackCompile(intput_file, output_path):
    # tokenize
    jack_lexer = JackTokenizer(intput_file)
    doc = xml.dom.minidom.Document()
    root = doc.createElement("tokens")
    doc.appendChild(root)
    while jack_lexer.hasMoreTokens() == True:
        jack_lexer.advance()
        if jack_lexer.tokenType() == 'KEYWORD':
            curr_token = jack_lexer.keyWord()
            if curr_token != 'ERROR':
                new_element = doc.createElement("keyword")
                text_node = doc.createTextNode(curr_token)
                new_element.appendChild(text_node)
                root.appendChild(new_element)
        elif jack_lexer.tokenType() == 'SYMBOL':
            curr_token = jack_lexer.symbol()
            if curr_token != 'ERROR':
                if curr_token == '<':
                    element_text = '&lt'
                elif curr_token == '>':
                    element_text = '&gt'
                elif curr_token == '&':
                    element_text = '&amp'
                else:
                    element_text = curr_token
                new_element = doc.createElement("symbol")
                text_node = doc.createTextNode(element_text)
                new_element.appendChild(text_node)
                root.appendChild(new_element)
        elif jack_lexer.tokenType() == 'INT_CONST':
            curr_token = jack_lexer.intVal()
            if curr_token >= 0:
                element_text = str(curr_token)
                new_element = doc.createElement("integerConstant")
                text_node = doc.createTextNode(element_text)
                new_element.appendChild(text_node)
                root.appendChild(new_element)
        elif jack_lexer.tokenType() == 'STRING_CONST':
            curr_token = jack_lexer.stringVal()
            if curr_token != 'ERROR':
                new_element = doc.createElement("stringConstant")
                text_node = doc.createTextNode(curr_token)
                new_element.appendChild(text_node)
                root.appendChild(new_element)
        elif jack_lexer.tokenType() == 'IDENTIFIER':
            curr_token = jack_lexer.identifier()
            if curr_token != 'ERROR':
                new_element = doc.createElement("identifier")
                text_node = doc.createTextNode(curr_token)
                new_element.appendChild(text_node)
                root.appendChild(new_element)             
    
    # write XxxT.xml
    doc_str = doc.toprettyxml(indent="\t", newl="\n")
    
    fdir, fname = os.path.split(intput_file)
    fbase, fext = os.path.splitext(fname)
    filename_xml = fbase + 'T' + '.xml'
    filepath_tokens_xml = os.path.join(output_path, filename_xml) 
    
    with open(filepath_tokens_xml, "w") as file_tokens:
        file_tokens.write(doc_str)
            
    #parse
    filename_vm = fbase + '.vm'
    filepath_vm_output = os.path.join(output_path, filename_vm)
    jack_parser = CompilationEngine(filepath_tokens_xml, filepath_vm_output)
    jack_parser.CompileClass()
    

# main program
if os.path.isfile(file_path):
    fname, fext = os.path.splitext(file_path)
    if fext == '.jack':
        # parse and translate singal vm file
        JackCompile(file_path, output_path)
elif os.path.isdir(file_path):
    # parse and translate all vm files in directory
    for filename in os.listdir(file_path):
        fname, fext = os.path.splitext(filename)
        if fext == '.jack':
            JackCompile(os.path.join(file_path, filename), output_path)
    