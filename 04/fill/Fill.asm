// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

//C pseudo code
//presentpixelreg = SCREEN-1;
//while(1)
//{
//    if (key == PRESSED)
//    {
//        //fill
//        if (presentpixelreg < SCREEN + 8K - 1){
//            presentpixelreg++;
//            RAM[presentpixelreg] = -1;
//        }
//    }
//    else{
//        //clear
//        if (presentpixelreg >= SCREEN){
//            RAM[presentpixelreg] = 0;
//            presentpixelreg--;
//        }
//    }
//}
// Put your code here.
      @16383  //SCREEN-1
      D=A
      @0
      M=D

(LOOP)
      @KBD
      D=M
      @CLEAR
      D;JEQ
      @FILL
      0;JMP

(FILL)
      @0
      D=M
      @24575 //SCREEN+8K-1
      D=D-A
      @LOOP
      D;JGE
      @0
      M=M+1
      A=M
      M=-1
      @LOOP
      0;JMP

(CLEAR)
      @0
      D=M
      @SCREEN
      D=D-A
      @LOOP
      D;JLT
      @0
      A=M
      M=0
      @0
      M=M-1
      @LOOP
      0;JMP





      