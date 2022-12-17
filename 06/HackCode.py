class HackCode:
    dest_set = ['0','0','0']
    comp_set = {'0': '0101010',
                '1': '0111111',
                '-1': '0111010',
                'D': '0001100',
                'A': '0110000',
                'M': '1110000',
                '!D': '0001101',
                '!A': '0110001',
                '!M': '1110001',
                '-D': '0001111',
                '-A': '0110011',
                '-M': '1110011',
                'D+1': '0011111',
                'A+1': '0110111',
                'M+1': '1110111',
                'D-1': '0001110',
                'A-1': '0110010',
                'M-1': '1110010',
                'D+A': '0000010',
                'D+M': '1000010',
                'D-A': '0010011',
                'D-M': '1010011',
                'A-D': '0000111',
                'M-D': '1000111',
                'D&A': '0000000',
                'D&M': '1000000',
                'D|A': '0010101',
                'D|M': '1010101'}
    jump_set = {'JGT': '001',
                'JEQ': '010',
                'JGE': '011',
                'JLT': '100',
                'JNE': '101',
                'JLE': '110',
                'JMP': '111'}
    def __init__(self) -> None:
        pass    
    def dest(self, dst_str):
        self.dest_set = ['0','0','0']
        if 'A' in dst_str:
            self.dest_set[0] = '1'
        if 'D' in dst_str:
            self.dest_set[1] = '1'
        if 'M' in dst_str:
            self.dest_set[2] = '1'
        return  self.dest_set[0]+self.dest_set[1]+self.dest_set[2]
    def comp(self, comp_str):
        return self.comp_set[comp_str]
    def jump(self, jmp_str):
        return self.jump_set[jmp_str]