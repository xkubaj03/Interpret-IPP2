# Implementační dokumentace k 2. úloze do IPP 2021/2022
Jméno a příjmení: Josef Kuba

Login: xkubaj03

## Použití
--help výpis nápovědy

--source=file vstupní soubor s XML reprezentací zdrojového kódu

--input=file soubor se vstupy pro samotnou interpretaci zadaného zdrojového kódu

Alespoň jeden z parametrů (--source nebo --input) musí být vždy zadán. Pokud jeden z nich chybí, jsou chybějící data načítána ze standardního vstupu.)

## Popis
Skript interpret.py má za úkol provést Instrukce zadané ve vstupním xml souboru, který je výstupem předchozího úkolu parse.php. Moji implementaci jsem pro přehlednost rozdělil do dvou souborů interpret.py a Instructions.py. Moje implementace obsahuje rozšíření NVI (aplikování objektově orientovaného programování), díky čemuž jsem dosáhl zvýšení přehlednosti kódu.

Soubor Instructions.py obsahuje jednotlivé třídy používané interpret.py. Za zmínku rozhodně stojí třída Instruction, která obsahuje (nahrané) pole vstupů, seznam instrukcí, aktuální pozice v programu (ProgramIndex), globální rámec, zásobník ve kterém jsou uloženy lokální rámce, dočasný rámec (Temporary frame), zásobník pozic (používaný instrukcemi CALL a RETURN), seznam návěští, zásobníkem hodnot a proměnnými ve kterých je uloženo zda jsou definovány lokální a dočasný rámec (TF). Dále pro jednotlivé instrukce ukládá opcode a pořadí. Zde jsou důležité metody get_symb a get_memory. Metoda get_symb vrátí hodnotu a typ ať už jde o konstantu nebo proměnnou. Metoda get_memory vrátí ukazatel na uzel v paměti do kterého budeme ukládat. 
Třídy pojmenovány po jednotlivých opcodech dědí z třídy Instruction a obsahují argumenty potřebné k své funkčnosti. Dále také obsahují metodu execute, která provede instrukci (s jejími parametry).

Třída Factory má metodu resolve, která je použitá pro zvolení správného konstruktoru, jemuž předá parametry. Pokud není nalezena příslušná třída, ukončí skript s příslušným chybovým návratovým kódem. 

Soubor interpret.py nejprve zkontroluje počet parametrů, poté jejich obsah a rozhodne, zda se má vypsat nápověda nebo se může pokračovat. Dále se pokusí otevřít soubory se zdrojem (source) a vstupem (input). Poté načte pomocní knihovny (xml.etree.ElementTree) jednotlivé parametry, které dále předá factory, která vytvoří příslušný objekt. Nakonec se volá na načtené instrukce metody execute čímž dojde k jejich provedení.
