# 🐾 Rawrsembler 🐾
Rawrsembler is a purr-ssembler for highly nefarius CPUs, providing a custom assembly language for advanced and obscure architectures. It's paws-itively perfect for those who want to scratch beneath the surface of low-level coding!

# Features
## 🐾 Multi-Format File Saving
Rawrsembler lets you save compiled output in various formats including:
* pad – Saves binary with byte-aligned padding.
* txt – Saves binary with argument-based padding.
* pip – Dumps JSON output to stdout for easy pipelining (default mode, doesn’t save).
* hex – Saves the binary as a hexadecimal string.
* schem – Saves the compiled output as a schematic.
* bin – Saves the compiled program as plain bytes.
For supported formats, you can add a debug flag to include extra information in the output:
## 🐾 Advanced Address Resolver
Rawrsembler minimizes jump lengths to optimize execution using SMT-based solver.
* Dynamically calculates the shortest possible jump addresses.
* Adjusts instruction placement for optimal memory efficiency.
## 🐾 Syntax linter
You can install vs code extenion to highlit `.wvrn` files

# Usage

```x86asm
; Entry point
.ENTRY
; opcodes
   nop
; labels
LABEL:
   nop
; jumps
   jmp LABEL ;% this jump
; pseudoinstructions
   lim 69
```

Then rawr onto the code
```
rawr -i .\src\program.wvrn -c -s pad
```

This will generate a compiled output with debug comments (if -c is used), making it easy to analyze
```
00000000  sta 0              0
00000000  sta 0    (LABEL)   1
00000001  lda 0              2  this jump
00000000  sta 0              3  this jump
11100011  addi -2            4  this jump
00010100  nand 1             5  this jump
00001111  bt true            6  this jump
00000001  lda 0              7
01110011  addi 7             8
00010010  add 1              9
00010010  add 1             10
00110011  addi 3            11
00010010  add 1             12
01110011  addi 7            13
```

Another way to use rawrsembler

```ps
python rawr.py -i .\program.wvrn -s bin # creates ./out/compiled.bin
python rawr.py -i .\program.wvrn -c -s pad # creates ./out/compiled.txt
```

## 🐱 Install
To set up Rawrsembler in your shell, simply claw into the repository and run the setup script:
```ps
powershell -ExecutionPolicy Bypass -File setup.ps1
```
or
```ps
./setup.ps1
```
This script will:

🐾 Create a virtual environment (venv)

🐾 Add the alias rawr to python rawr.py (because every good kit needs a shortcut!)

🐾 Add the alias to-wve to python ./tools/get-wvrn-bin.py

🐾 Install a lint extension for VS Code to keep your code looking purr-fect

After installation you can use aliaes.
```ps
rawr -i .\program.wvrn -s bin # save as bin file
rawr -i .\program.wvrn | to-wve
```

## Manual installation
If you prefer to set things up by paw, follow these steps to get Rawrsembler purring on your machine:
```
python -m venv venv  
.\venv\Scripts\Activate  
pip install -r requirements.txt  
```

Keep your Rawrsembler code looking purr-fect
```
code --install-extension ./rawrsembler-lit/rawrsembler-0.2.2.vsix
```


## 🐾 Uninstall
```
./revert.ps1
```
Now go forth and assemble with the grace of a prowling cat! 🐱✨

