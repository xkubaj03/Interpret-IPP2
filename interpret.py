"""
VUT FIT IPP projekt
Autor: Josef Kuba
Login: xkubaj03
"""
#Import knihoven
import sys
import xml.etree.ElementTree as ET
from Instructions import *

#Načtení xml a input souvorů
sourceFileName = ""
inputFileName = ""
sourceFile = ""
inputFile = ""

if(len(sys.argv) == 1):#Vypíše text pokud nebyly zadány žádné argumenty
    print("Pro nápovědu použijte parametr --help\n")
    exit(0)
elif(len(sys.argv) == 2):#Byl zadán pouze 1 argument
    if(sys.argv[1] == "--help"):
        print("""        --help výpis tohoto textu
        --source=file vstupní soubor s XML reprezentací zdrojového kódu
        --input=file soubor se vstupy12 pro samotnou interpretaci zadaného zdrojového kódu

        Alespoň jeden z parametrů (--source nebo --input) musí být vždy zadán. Pokud jeden z nich
        chybí, jsou chybějící data načítána ze standardního vstupu.""")
        exit(0)
    elif(sys.argv[1].startswith("--source=")): #Byl zadán pouze source  (druhý je stdin)
        sourceFileName = sys.argv[1][9:] #Ořízne z argumentu pouze cestu
        try: #Pokusí se otevřít soubor pomocí cesty
            sourceFile = open(sourceFileName, "r")
        except FileNotFoundError:
            exit(11)
        inputFile = sys.stdin
    elif (sys.argv[1].startswith("--input=")): #Byl zadán pouze input  (druhý je stdin)
        inputFileName = sys.argv[1][8:] #Ořízne z argumentu pouze cestu
        sourceFile = sys.stdin
        try: #Pokusí se otevřít soubor pomocí cesty
            inputFile = open(inputFileName, "r")
        except FileNotFoundError:
            exit(11)
    else:
        exit(10)
elif(len(sys.argv) == 3): #Byly zadány 2 argumenty
    if ((sys.argv[1].startswith("--source=")) and (sys.argv[2].startswith("--input="))): #Byl zadán source i input
        sourceFileName = sys.argv[1][9:] #Ořízne z argumentu pouze cestu
        inputFileName = sys.argv[2][8:]
        try: #Pokusí se otevřít soubory pomocí cesty
            sourceFile = open(sourceFileName, "r")
            inputFile = open(inputFileName, "r")
        except FileNotFoundError:
            exit(11)
    elif ((sys.argv[2].startswith("--source=")) and (sys.argv[1].startswith("--input="))): #Byl zadán source i input
        sourceFileName = sys.argv[2][9:] #Ořízne z argumentu pouze cestu
        inputFileName = sys.argv[1][8:]
        try: #Pokusí se otevřít soubor pomocí cesty
            sourceFile = open(sourceFileName, "r")
            inputFile = open(inputFileName, "r")
        except FileNotFoundError:
            exit(11)
    else:
        exit(10)
else:
    exit(10)


tree = ET.parse(sourceFile) #Převedení pro použití knihovny na čtení xml
root = tree.getroot() #Načtení kořene xml


instr = {} #Dictionary do kterého se budou ukládat jednotlivé instrukce
tmpArgs = [[1, 2], [3, 4], [5, 6]] #Pole do kterého se budou načítat argumenty jednotlivých instrukcí
factory = Factory()
for instruction in tree.findall("instruction"): #Projde xml a načte instrukce (včetně opcode a order) a jejich argumentů (včetně typ a obsah)
    for i in range(len(instruction)): #Načítá argumenty a jejich obsah
        if instruction.find("arg" + str(i+1)) is None: #Kontrola zda instrukce obsahuje argument
            exit(32)
        if instruction.find("arg" + str(i+1)).text is None: #Pokud je textová část None tak ji uloží jako prázdný string
            tmpArgs[i][0] = ""
        else:
            if "#" in instruction.find("arg" + str(i + 1)).text or "#" in instruction.find("arg" + str(i + 1)).get("type"):
                exit(32) #Kontroluje zda text obsahuje "#" a pokud ano vyhodí error
            tmpArgs[i][0] = instruction.find("arg" + str(i+1)).text
        tmpArgs[i][1] = instruction.find("arg" + str(i+1)).get("type")
    if instruction.get("order") in instr: #Kontroluje zda se právě nenačítá duplicitní order
        exit(32)
    #Samotné načtení instrukce
    instr[instruction.get("order")] = (factory.resolve(str(instruction.get("opcode")),
                                                       instruction.get("order"),
                                                       len(instruction),
                                                       tmpArgs))



Instruction._input = inputFile.read().split("\n") #Připraví a načte input do Instruction classy
lastInstr = 0
for i in instr: #Najde nejvyšší order (kvůli možnostem mezer v orderech)
    tmp = int(i)
    if tmp > lastInstr:
        lastInstr = tmp
while Instruction._ProgramIndex <= lastInstr: #Provede jednotlivé instrukce
    if str(Instruction._ProgramIndex) in instr: #Provede instrukci pokud existuje
        instr[str(Instruction._ProgramIndex)].execute() #Samotné provedení instrukce
    Instruction._ProgramIndex += 1 #Inkrementuje Program index

exit(0)
