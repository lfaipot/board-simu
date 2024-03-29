# board-simu

board-simu has been developed for educational purpose.

It aims at providing a tool to teach/learn assembly languages
* edu1: a simple example of assembly language, designed by teachers (very limited).
* 6502: almost complete, added to provide a more powerful but still simple language, to develop more elaborated programs.

With board-simu, you can edit a program, load it into the emulated memory, execute it step by step while seeing changes into memory, registers and indicators.

[Screenshot #1] (https://raw.githubusercontent.com/lfaipot/board-simu/master/doc/board-simu-screenshot1.png)

Prerequisites
* requires python-qt4

Quick Start Guide
* launch "board_simulator (or "board_simulator.bat for Windows)
* In the "Board Simulator" window
    * select a board: for example "6502 with 1 8-led display": "Execution" window and "Led" window will appear
    * open a program: for example, examples/arch_6502/test_led_rotate.ass
    * click on "Load". Any error will be displayed in the bottom window
* In the "Execution" window
    * click on "Run" or "Step". Adapt the speed while running with the slider
    * click on "Information" to know more about the board and the processor instructions and directives (in French for Edu1)
* The "Led" window shows the value written at 0xFF

Notes
* Qt Designer used to define GUI (src/Ui/*.py generated from equivalent src/Ui/.ui)
* examples/arch_xxx contain programs used as unit tests to check instructions (unit_test will be used later)
* boards displayed in the "Board" menu are defined into src/hardware/board/board_decription.cfg. For each board, it defines the processor type, the memory size, a help file (HTML) and the external device connected to (currently only Leds are emulated)

