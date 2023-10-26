"""
VUT FIT IPP projekt
Autor: Josef Kuba
Login: xkubaj03
"""
#Importování knihoven
import sys
import re


class Instruction:
    _input = [] #Pole inputů
    _listOfInstructions = []
    _GlobalFrame = {}
    _LocalFrameStack = []
    _TemporaryFrame = {}
    _PositionStack = [] #Zásobník pozic od call pro return
    _LabelOrder = {}
    _LocalIsDefined = 0 #Určuje za se smí přistoupit k danému rámci
    _TempIsDefined = 0 #Určuje za se smí přistoupit k danému rámci
    _DataStack = []

    _ProgramIndex = 1 #Index který určuje aktuální pozici při vykonávání

    def __init__(self, oppcode, order): #konstruktor
        self._oppcode = oppcode #Opcode
        self._order: int = order #Pořadí
        self._listOfInstructions.append(self) #Přidání do seznamu instrukcí
    #Pomocné metody
    def get_oppcode(self):
        return self._oppcode

    def get_order(self):
        return self._order

    def get_list(self):
        return self._listOfInstructions

    def get_symb(self, typ, value): #Metoda pro načtení typu a hodnoty (Pokud je to proměnná tak vrací její typ a hodnotu jinak vrátí sama sebe)
        if value.startswith("GF@", 0, 3): #Globální proměnná
            if value[3:] in self._GlobalFrame: #Ověření existence proměnné
                if self._GlobalFrame[value[3:]]["typ"] is None: #Pokud je typ None
                    exit(56)
                return self._GlobalFrame[value[3:]]["typ"], self._GlobalFrame[value[3:]]["value"] #Vrácení typu a hodnoty
            else:
                exit(54)
        elif value.startswith("TF@", 0, 3):#Následující část je shodná s částí pro GF
            if self._TempIsDefined:
                if value[3:] in self._TemporaryFrame:
                    if self._TemporaryFrame[value[3:]]["typ"] is None:
                        exit(56)
                    return self._TemporaryFrame[value[3:]]["typ"], self._TemporaryFrame[value[3:]]["value"]  #Vrácení typu a hodnoty
                else:
                    exit(54)
            else:
                exit(55)
        elif value.startswith("LF@", 0, 3):#Následující část je stejná jako obě předchozí až na rozdíl přístupu k vrcholku zásobníku ([-1])
            if self._LocalIsDefined:
                if value[3:] in self._LocalFrameStack[-1]:
                    if self._LocalFrameStack[-1][value[3:]]["typ"] is None:
                        exit(56)
                    return self._LocalFrameStack[-1][value[3:]]["typ"], self._LocalFrameStack[-1][value[3:]]["value"]  #Vrácení typu a hodnoty
                else:
                    exit(54)
            else:
                exit(55)
        else: #Pokud textový obsah nezačíná GF@ TF@ ani LF@ potom je to konstanta a vrací sama sebe
            return typ, value

    def get_memory(self, typ, value):
        """Metoda pro získání paměti je velice podobná metodě get_symb až na to že nevrací hodnoty,
         ale přímo uzel do kterého budeme zapisovat nové hodnoty z čehož je patrné že zde není ani část pro konstantu"""
        if value.startswith("GF@", 0, 3): #Globální proměnná
            if value[3:] in self._GlobalFrame:
                return self._GlobalFrame[value[3:]]
            else:
                exit(54)
        elif value.startswith("TF@", 0, 3):
            if self._TempIsDefined:
                if value[3:] in self._TemporaryFrame:
                    return self._TemporaryFrame[value[3:]]
                else:
                    exit(54)
            else:
                exit(55)
        elif value.startswith("LF@", 0, 3):
            if self._LocalIsDefined:
                if value[3:] in self._LocalFrameStack[-1]:
                    return self._LocalFrameStack[-1][value[3:]]
                else:
                    exit(54)
            else:
                exit(55)
        else:
            exit(666)


"""
Následují třídy jednotlivých instrukcí které ve svém konstruktoru volají
nadřezený kostruktor a navíc obsahují jednotlivé argumenty a unikátní 
metody execute které provedou příslušný příkaz.
"""
class Move(Instruction): #MOVE var symb

    def __init__(self, num, numOfArgs, ArgAr): #Konstruktor
        super().__init__("MOVE", num) #Volání nadřazeného konstruktoru
        self._NumberOfArguments = numOfArgs #Uložení jednotlivých parametrů
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]

    def execute(self):
        typ, value = self.get_symb(self._Arg2Type, self._Arg2Value) #Získá typ a hodnotu
        target = self.get_memory(self._Arg1Type, self._Arg1Value) #Získá uzel do kterého se bude zapisovat
        target["typ"] = typ #Zapsání typu do uzlu
        target["value"] = value #Zapsání hodnoty do uzlu
class CreateFrame(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("CREATEFRAME", num)

    def execute(self):
        Instruction._TempIsDefined = 1
        self._TemporaryFrame.clear()
class PushFrame(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("PUSHFRAME", num)
    def execute(self):
        if Instruction._TempIsDefined: #Pokud je definovaný rámec
            self._LocalFrameStack.append(self._TemporaryFrame.copy()) #Přidá na konec TF
            Instruction._TempIsDefined = 0 #TF není definován
            Instruction._LocalIsDefined = 1 #LF je definován
            self._TemporaryFrame.clear() #Vyčistí obsah TF
        else:
            exit(55)
class PopFrame(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("POPFRAME", num)

    def execute(self):
        if self._LocalFrameStack: #Pokud není prázdný stack
            Instruction._TemporaryFrame = self._LocalFrameStack.pop() #Popne LF na TF
            Instruction._TempIsDefined = 1 #TF je definován
            if not self._LocalFrameStack: #Pokud je stack prázdný nemůžeme k němu přistoupit
                Instruction._LocalIsDefined = 0
        else:
            exit(55)
class Defvar(Instruction):

    def __init__(self, num, str_arg, ArgAr):
        super().__init__("DEFVAR", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]

    def execute(self):
        if self._Arg1Type == "var": #Musí mít typ var
            if self._Arg1Value.startswith("GF@", 0, 3): #Vybere se na který rámec se má vytvořit
                if not self._Arg1Value[3:] in self._GlobalFrame:#Pokud už neobsahuje zvolený název
                    self._GlobalFrame[self._Arg1Value[3:]] = {"typ": None, "value": None} #Přidá proměnnou na daný rámec s příslušným jménem a hodnotami None
                else:
                    exit(52)
            elif self._Arg1Value.startswith("TF@", 0, 3): #Provedeme stejný postup jako u GF ale přidáme kontrolu zda je rámec definován
                if self._TempIsDefined: #Pokud je rámec definován
                    if not self._Arg1Value[3:] in self._TemporaryFrame:
                        self._TemporaryFrame[self._Arg1Value[3:]] = {"typ": None, "value": None}
                    else:
                        exit(52)
                else:
                    exit(55)
            elif self._Arg1Value.startswith("LF@", 0, 3):
                if self._LocalIsDefined: #Pokud je rámec definován
                    if not self._Arg1Value[3:] in self._LocalFrameStack[-1]: #Přistupuje k vrcholku stacku proto [-1]
                        self._LocalFrameStack[-1][self._Arg1Value[3:]] = {"typ": None, "value": None}
                    else:
                        exit(52)
                else:
                    exit(55)
            else:
                exit(666)
        else:
            exit(666)
class Call(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("CALL", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]

    def execute(self):
        if self._Arg1Type == "label":
            if self._Arg1Value in self._LabelOrder: #Pokud existuje label na který má skočit
                self._PositionStack.append(int(self.get_order())) #pridani hodnoty na stack (po každém provedení instrukce se inkrementuje Program index)
                Instruction._ProgramIndex = int(self._LabelOrder[self._Arg1Value]) #Nastavení ProgramIndex na pozici daného labelu
            else:
                exit(52)
        else:
            exit(32)
class Return(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("RETURN", num)

    def execute(self):
        if self._PositionStack: #Pokud není prázdný stack
            Instruction._ProgramIndex = self._PositionStack.pop() #Popne pozici na kterou se má vrátit (po každém provedení instrukce se inkrementuje Program index)
        else:
            exit(56)
class Pushs(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("PUSHS", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]

    def execute(self):
        typ, value = self.get_symb(self._Arg1Type, self._Arg1Value)
        if typ in {"bool", "int", "string", "nil"}: #Pokud má povolený typ
            if typ is None and value is None: #Pokud obsahuje None
                exit(56)
            self._DataStack.append({"typ": typ, "value": value}) #Pushne hodnotu a typ na stack
        else:
            exit(52)
class Pops(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("POPS", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]

    def execute(self):
        if self._DataStack:
           target = self.get_memory(self._Arg1Type, self._Arg1Value)
           tmp = self._DataStack.pop() #Popne ze stacku a uloží data do získaného uzlu
           target["value"] = tmp["value"]
           target["typ"] = tmp["typ"]
        else:
            exit(56)
class Add(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("ADD", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        try: #Kontrola zda lze obsah převést na int
            int(value1)
            int(value2)
        except ValueError:
            exit(53)
        if type1 == "int" and type2 == "int":
            target["typ"] = "int" #Zapíše příslušný typ
            target["value"] = int(value1) + int(value2) #Zapíše součet
        else:
            exit(53)
class Sub(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("SUB", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        try: #Kontrola zda lze obsah převést na int
            int(value1)
            int(value2)
        except ValueError:
            exit(53)
        if type1 == "int" and type2 == "int": #Musí být oba int
            target["typ"] = "int"
            target["value"] = int(value1) - int(value2)
        else:
            exit(53)
class Mul(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("MUL", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        try: #Kontrola zda lze obsah převést na int
            int(value1)
            int(value2)
        except ValueError:
            exit(53)
        if type1 == "int" and type2 == "int":
            target["typ"] = "int"
            target["value"] = int(value1) * int(value2)
        else:
            exit(53)
class Idiv(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("IDIV", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        try: #Kontrola zda lze obsah převést na int
            int(value1)
            int(value2)
        except ValueError:
            exit(53)
        if type1 == "int" and type2 == "int":
            if value2 == 0:
                exit(57)
            target["typ"] = "int"
            target["value"] = int(value1) // int(value2) #Celočíselné dělení
        else:
            exit(53)
class LT(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("LT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        target["typ"] = "bool"
        if type1 == "nil" or type2 == "nil": #Porovnání nilu dojde k chybě
            exit(53)
        if type1 == type2 == "bool": #Porovnávání bool
            if value1 == "false" and value2 == "true":
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "int": #Porovnání int
            if int(value1) < int(value2):
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "string": #Porovnání stringů (délky)
            if len(value1) < len(value2):
                target["value"] = "true"
            else:
                target["value"] = "false"
        else:
            exit(53)
class GT(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("GT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self): #Podobné LF
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        target["typ"] = "bool"
        if type1 == "nil" or type2 == "nil":
            exit(53)
        elif type1 == type2 == "bool":
            if value1 == "true" and value2 == "false":
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "int":
            if int(value1) > int(value2):
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "string":
            if len(value1) > len(value2):
                target["value"] = "true"
            else:
                target["value"] = "false"
        else:
            exit(53)
class EQ(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("EQ", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self): #Podobné GF a LF až na možnost porovnání nil a porovnává se obsah stringu a ne délka
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        target["typ"] = "bool"
        if type1 == "nil" or type2 == "nil":
            if value1 == value2 == "nil":
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "bool":
            if value1 == value2 == "true" or value1 == value2 == "false":
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "int":
            if int(value1) == int(value2):
                target["value"] = "true"
            else:
                target["value"] = "false"
        elif type1 == type2 == "string":
            if value1 == value2:
                target["value"] = "true"
            else:
                target["value"] = "false"
        else:
            exit(53)
class And(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("AND", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        if type1 == "bool" and type2 == "bool": #Oba argumenty musí mít typ bool
            target["typ"] = "bool"
            if value1 == "true" and value2 == "true":
                target["value"] = "true"
            else:
                target["value"] = "false"
        else:
            exit(53)
class Or(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("OR", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        if type1 == "bool" and type2 == "bool": #Oba argumenty musí mít typ bool
            target["typ"] = "bool"
            if value1 == "true" or value2 == "true":
                target["value"] = "true"
            else:
                target["value"] = "false"
        else:
            exit(53)
class Not(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("NOT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        if type1 == "bool": #Argument musí mít typ bool
            target["typ"] = "bool"
            if value1 == "true":
                target["value"] = "false"
            else:
                target["value"] = "true"
        else:
            exit(53)
class Int2Char(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("INT2CHAR", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        if type1 == "int":
            target["typ"] = "string"
            try: #Kontrola zda lze převést value1 na int
                target["value"] = chr(int(value1))
            except ValueError:
                exit(58)
        else:
            exit(53)
class Stri2Int(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("STRI2INT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)

        if type1 == "string" and type2 == "int":
            target["typ"] = "int"
            try: #Kontrola zda lze převést value2 na int a zároveň kontrola zda nepřistupuje mimo pole
                target["value"] = ord(value1[int(value2)])
            except (IndexError, ValueError):
                exit(58), exit(53)
        else:
            exit(53)
class Read(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("READ", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        if value1 not in {"bool", "int", "string"}: #Může načíst pouze povolené typy
            exit(32)
        if Instruction._input: #Pokud je co číst
            tmp = Instruction._input[0]
            Instruction._input = Instruction._input[1:]
        else: #Jinak nastaví value a typ nil
            tmp = ""
        if tmp == "":
            target["value"] = "nil"
            target["typ"] = "nil"
        elif value1 == "int":
            target["value"] = tmp
            target["typ"] = "int"
        elif value1 == "string":
            target["value"] = tmp
            target["typ"] = "string"
        elif value1 == "bool":
            if tmp.lower() == "true":
                target["value"] = "true"
            else:
                target["value"] = "false"
            target["typ"] = "bool"
        else:
            exit(32)
class Write(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("WRITE", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]

    def execute(self):
        typ, value = self.get_symb(self._Arg1Type, self._Arg1Value)
        if typ == "bool" and value == "1":
            print("true", end="")
        elif typ == "bool" and value == "0":
            print("false", end="")
        elif typ == "nil": #Vypisování nil nevypíše nic
            print("", end="") #Nemusí zde být (nebo pass)
        else:
            list = re.findall(r"\\[0-9]{3}", str(value)) #Načte list které hodnoty se musí nahradit
            i = 0
            while i < len(list):
                value = re.sub(r"\\[0-9]{3}", chr(int(list[i][2:])), value, 1) #Nahrazení podle listu
                i += 1
            print(value, end="")
class Concat(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("CONCAT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        if type1 == "string" and type2 == "string": #Oba typy musí být string
            target["typ"] = "string"
            target["value"] = str(value1) + str(value2)
        else:
            exit(53)
class StrLen(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("STRLEN", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type, value = self.get_symb(self._Arg2Type, self._Arg2Value)
        print(type, value)
        if type == "string":
            target["value"] = len(value)# - len(re.findall(r"\\[0-9]{3}", str(value))) * 3
            #Nevím zda se mají počítat sekvence jako jeden znak. Pokud ano stačí odkomentovat a počítá správně
            target["typ"] = "int"
        else:
            exit(53)
class GetChar(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("GETCHAR", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        target["typ"] = "string"
        if type1 == "string" and type2 == "int":
            try: #Kontrola zda lze převést na int a indexaci mimo pole
                target["value"] = value1[int(value2)]
            except (IndexError, ValueError):
                exit(58), exit(58)
        else:
            exit(53)
class SetChar(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("SETCHAR", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        type1, value1 = self.get_symb(self._Arg2Type, self._Arg2Value)
        type2, value2 = self.get_symb(self._Arg3Type, self._Arg3Value)
        if target["typ"] == "string" and type1 == "int" and type2 == "string":
            if value2 == "":
                exit(58)
            try: #Kontrola zda lze převést na int a indexaci mimo pole
                if int(value1) < 0 or int(value1) >= len(target["value"]):
                    exit(58)
                target["value"] = target["value"][0:int(value1)] + value2[0] + target["value"][int(value1)+1:]
            except ValueError:
                exit(58)
        else:
            exit(53)
class Type(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("TYPE", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]

    def execute(self): #Prochází stejně jako get_symb a get_memory ale při chybě vrátí prázdný string
        target = self.get_memory(self._Arg1Type, self._Arg1Value)
        target["typ"] = "type"
        if self._Arg2Value.startswith("GF", 0, 2):
            if self._Arg2Value[3:] in self._GlobalFrame:
                target["value"] = self._GlobalFrame[self._Arg2Value[3:]]["typ"]
            else:
                target["value"] = ""
        elif self._Arg2Value.startswith("TF", 0, 2):
            if self._TempIsDefined:
                if self._Arg2Value[3:] in self._TemporaryFrame:
                    target["value"] = self._TemporaryFrame[self._Arg2Value[3:]]["typ"]
                else:
                    target["value"] = ""
            else:
                target["value"] = ""
        elif self._Arg2Value.startswith("LF", 0, 2):
            if self._LocalIsDefined:
                if self._Arg2Value[3:] in self._LocalFrameStack[-1]:
                    target["value"] = self._LocalFrameStack[-1][self._Arg2Value[3:]]["typ"]
                else:
                    target["value"] = ""
            else:
                target["value"] = ""
        else:
            target["value"] = ""
class Label(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("LABEL", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        #V tomto případě jsem přidal label do seznamu návěští aby se nepřidávalo vícekrát (a bylo možné kontrolovat duplikáty)
        if self._Arg1Type == "label":
            if not self._Arg1Value in self._LabelOrder:
                self._LabelOrder[self._Arg1Value] = self._order
            else:
                exit(52)
        else:
            exit(666)

    def execute(self):
        pass
class Jump(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("JUMP", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
    def execute(self):
        if self._Arg1Type == "label":
            if self._Arg1Value in self._LabelOrder:
                Instruction._ProgramIndex = int(self._LabelOrder[self._Arg1Value]) #Nastaví ProgramIndex na pořadí jeho návěští
            else:
                exit(666)
        else:
            exit(666)
class JumpIfEq(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("JUMPIFEQ", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]
    def execute(self):
        type3, value3 = self.get_symb(self._Arg3Type, self._Arg3Value)
        type2, value2 = self.get_symb(self._Arg2Type, self._Arg2Value)
        if type3 != type2: #Kontrola tejných typů
            exit(53)
        if value3 == value2:
            if self._Arg1Value in self._LabelOrder: #Kontrola existence návěští
                Instruction._ProgramIndex = int(self._LabelOrder[self._Arg1Value])
            else:
                exit(666) #neexistující návěští
class JumpIfNEq(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("JUMPIFNEQ", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
        self._Arg2Value = ArgAr[1][0]
        self._Arg2Type = ArgAr[1][1]
        self._Arg3Value = ArgAr[2][0]
        self._Arg3Type = ArgAr[2][1]

    def execute(self):
        type3, value3 = self.get_symb(self._Arg3Type, self._Arg3Value)
        type2, value2 = self.get_symb(self._Arg2Type, self._Arg2Value)
        if type3 != type2:
            exit(53)
        if value3 != value2:
            if self._Arg1Value in self._LabelOrder:
                Instruction._ProgramIndex = int(self._LabelOrder[self._Arg1Value])
            else:
                exit(666) #neexistující návěští
class Exit(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("EXIT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
    def execute(self):
        type, value = self.get_symb(self._Arg1Type, self._Arg1Value)
        if type == "int":
            try: #Kontroluje zda je možné převést value na int
                int(value)
            except ValueError:
                exit(53)
            if int(value) >= 0 and int(value) <= 49: #Kontrola rozsahu
                exit(int(value))
            else:
                exit(57)
        else:
            exit(53)
class DPrint(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("DPRINT", num)
        self._Arg1Value = ArgAr[0][0]
        self._Arg1Type = ArgAr[0][1]
    def execute(self):
        type, value = self.get_symb(self._Arg1Type, self._Arg1Value)
        sys.stderr.write(value) #Výpis hodnoty na stderr
class Break(Instruction):
    def __init__(self, num, numOfArgs, ArgAr):
        super().__init__("Break", num)
    def execute(self): #Vypsání údajů o paměti na stderr
        sys.stderr.write(str(self.get_order()))
        sys.stderr.write(str(self._GlobalFrame))
        sys.stderr.write(str(self._TemporaryFrame))
        sys.stderr.write(str(self._LocalFrameStack))

class Factory: #Vybírá správný kostruktor
    def resolve(self, opcode: str, numOfInstr, numOfArgs, ArgArr):
        if opcode.upper() == "MOVE":
            return Move(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "CREATEFRAME":
            return CreateFrame(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "PUSHFRAME":
            return PushFrame(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "POPFRAME":
            return PopFrame(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "DEFVAR":
            return Defvar(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "CALL":
            return Call(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "RETURN":
            return Return(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "PUSHS":
            return Pushs(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "POPS":
            return Pops(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "ADD":
            return Add(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "SUB":
            return Sub(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "MUL":
            return Mul(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "IDIV":
            return Idiv(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "LT":
            return LT(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "GT":
            return GT(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "EQ":
            return EQ(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "AND":
            return And(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "OR":
            return Or(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "NOT":
            return Not(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "INT2CHAR":
            return Int2Char(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "STRI2INT":
            return Stri2Int(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "READ":
            return Read(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "WRITE":
            return Write(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "CONCAT":
            return Concat(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "STRLEN":
            return StrLen(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "GETCHAR":
            return GetChar(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "SETCHAR":
            return SetChar(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "TYPE":
            return Type(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "LABEL":
            return Label(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "JUMP":
            return Jump(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "JUMPIFEQ":
            return JumpIfEq(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "JUMPIFNEQ":
            return JumpIfNEq(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "EXIT":
            return Exit(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "DPRINT":
            return DPrint(numOfInstr, numOfArgs, ArgArr)
        elif opcode.upper() == "BREAK":
            return Break(numOfInstr, numOfArgs, ArgArr)
        else:
            #Neznámý opcode
            exit(53)
