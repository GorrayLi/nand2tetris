import sys
import os
from VmParser import VmParser
from CodeWriter import CodeWriter

file_path = sys.argv[1]
#file_path = "ProgramFlow/FibonacciSeries"
output_path = sys.argv[2]
#output_path = "ProgramFlow/FibonacciSeries/FibonacciSeries.asm"

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
        elif vm_parser.commandType() == 'C_LABEL':
            label = vm_parser.arg1()
            code_writer.writeLabel(label)
        elif vm_parser.commandType() == 'C_GOTO':
            label = vm_parser.arg1()
            code_writer.writeGoto(label)
        elif vm_parser.commandType() == 'C_IF':
            label = vm_parser.arg1()
            code_writer.writeIf(label)
        elif vm_parser.commandType() == 'C_FUNCTION':
            func_name = vm_parser.arg1()
            num_locals = vm_parser.arg2()
            code_writer.writeFunction(func_name, num_locals)
        elif vm_parser.commandType() == 'C_RETURN':
            code_writer.writeReturn()
        elif vm_parser.commandType() == 'C_CALL':
            func_name = vm_parser.arg1()
            num_args = vm_parser.arg2()
            code_writer.writeCall(func_name, num_args)

# main program
code_writer = CodeWriter(output_path)
if os.path.isfile(file_path):
    fname, fext = os.path.splitext(file_path)
    if fext == '.vm':
        # parse and translate singal vm file
        translate(file_path, output_path)
elif os.path.isdir(file_path):
    # find Sys.vm, if found, writeInit
    for filename in os.listdir(file_path):
        if filename == 'Sys.vm':
            code_writer.writeInit()
    
    # parse and translate all vm files in directory
    for filename in os.listdir(file_path):
        fname, fext = os.path.splitext(filename)
        if fext == '.vm':
            translate(os.path.join(file_path, filename), output_path)
code_writer.close()

