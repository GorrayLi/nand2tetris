import sys
import os
from VmParser import VmParser
from CodeWriter import CodeWriter

file_path = sys.argv[1]
output_path = sys.argv[2]

def translate(inputfile, outputfile):
    dirname, basename = os.path.split(inputfile)
    fname, fext = os.path.splitext(basename)
    code_writer.setFileName(fname)
    vm_parser = VmParser(inputfile)
    while vm_parser.hasMoreCommands() == True:
        vm_parser.advance()
        if vm_parser.commandType() == 'NONE':
            continue
        elif vm_parser.commandType() == 'C_ARITHMETIC':
            cmd = vm_parser.arg1()
            code_writer.writeArithmetic(cmd)
        elif vm_parser.commandType() == 'C_PUSH' or vm_parser.commandType() == 'C_POP':
            segment = vm_parser.arg1().upper()
            index = vm_parser.arg2()
            code_writer.WritePushPop(vm_parser.commandType(), segment, index)

# main program
code_writer = CodeWriter(output_path)
if os.path.isfile(file_path):
    fname, fext = os.path.splitext(file_path)
    if fext == '.vm':
        # parse and translate singal vm file
        translate(file_path, output_path)
elif os.path.isdir(file_path):
    # parse and translate all vm files in directory
    for filename in os.listdir(file_path):
        fname, fext = os.path.splitext(filename)
        if fext == '.vm':
            translate(os.path.join(file_path, filename), output_path)
code_writer.close()

