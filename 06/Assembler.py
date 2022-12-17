import sys
from AsmParser import AsmParser
from HackCode import HackCode
from SymbolTable import SymbolTable

file_path = sys.argv[1]
output_path = sys.argv[2]

# first pass: to build symbol table (to find LABEL symbol)
label_finder = AsmParser(file_path)
symbol_table = SymbolTable()
inst_cntr = 0
while label_finder.hasMoreCommands() == True:
    label_finder.advance()
    if label_finder.commandType() == 'NONE':
        continue
    elif label_finder.commandType() == 'A_COMMAND' or label_finder.commandType() == 'C_COMMAND':
        inst_cntr = inst_cntr + 1
    elif label_finder.commandType() == 'L_COMMAND':
        label = label_finder.symbol()
        symbol_table.addEntry(label, inst_cntr)         

# second pass: to parse and generate binary code
hack_bin = []
# parse cmd
parser = AsmParser(file_path)
coder = HackCode()
alloc_id = 0
VARI_ADDR_BASE = 16
while parser.hasMoreCommands() == True:
    parser.advance()
    if parser.commandType() == 'NONE':
        continue
    elif parser.commandType() == 'A_COMMAND' or parser.commandType() == 'L_COMMAND':
        symbol = parser.symbol()
    elif parser.commandType() == 'C_COMMAND':
        dest = parser.dest()
        comp = parser.comp()
        jump = parser.jump()

    # code binary cmd
    if parser.commandType() == 'A_COMMAND':
        if symbol.isdecimal():
            num = int(symbol)
        else:
            if symbol_table.contains(symbol):
                num = symbol_table.GetAddress(symbol)
            else:
                variable_addr = VARI_ADDR_BASE + alloc_id
                alloc_id = alloc_id + 1
                symbol_table.addEntry(symbol, variable_addr)
                num = variable_addr
        num_bin = bin(num)
        a_bin = num_bin[2:].rjust(16,'0')
        hack_bin.append(a_bin)
    elif parser.commandType() == 'C_COMMAND':
        if dest != '':
            dest_bin = coder.dest(dest)
        else:
            dest_bin = '000'
        if comp != '':
            comp_bin = coder.comp(comp)
        if jump != '':
            jump_bin = coder.jump(jump)
        else:
            jump_bin = '000'
        cmd_bin = '111' + comp_bin + dest_bin + jump_bin
        hack_bin.append(cmd_bin)

s = '\n'
output_code = s.join(hack_bin)
hack_file = open(output_path, 'w+')
hack_file.write(output_code)
hack_file.close()

