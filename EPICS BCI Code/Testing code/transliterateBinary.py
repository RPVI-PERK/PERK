import ast
import csv
import json
import os


#with open('brailletobinary.txt', 'r', encoding = "utf-8") as f:
#    data = f.read()
#b2b = ast.literal_eval(data)

# def load_enabled_contractions(json_path='enabled_contractions.txt'):
#     """Reads JSON library and returns set of enabled contraction words."""
#     if not os.path.exists(json_path):
#         return set()
#     try:
#         with open(json_path, 'r', encoding='utf-8') as f:
#             contraction_data = json.load(f)
#             return {
#                 word for word, details in contraction_data.items()
#                 if details.get("enabled", 0) == 1
#             }
#     except Exception:
#         return set()

def findOutput(whatLong, howLong, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib):
    global translated
    global translatedOutput
    global i
    global lastOutput

    if translated:
        return

    if not whatLong or whatLong not in brailleLib:
        return

    
    for possibleOut in brailleLib[whatLong]:
        
        #WHole word contraction

        if possibleOut.startswith("_") and possibleOut.endswith("_"):
            contraction_word = possibleOut[1:-1]

            # Must be a complete word:
            # blank before + blank after.
            if (
                i > 0
                and i + howLong < len(inputarr)
                and inputarr[i - 1] == "000000" or "capital" in lastOutput
                and inputarr[i + howLong] == "000000"
            ):
                if contraction_word not in enabled_contractions:
                    continue
                
                translatedOutput += contraction_word
                lastOutput = contraction_word
                i += howLong
                translated = True
                return

            continue

        # Special ./ output
        
        if "./" in possibleOut:
            output = possibleOut.replace("^", "")
            
            translatedOutput += output
            lastOutput = output
            i += howLong
            translated = True
            return

        # ^xxx^ = must be inside a word

        if possibleOut.startswith('^') or possibleOut.endswith('^'):
            if (
                i > 0
                and i + howLong < len(inputarr)
                and inputarr[i - 1] != "000000"
                and inputarr[i + howLong] != "000000"
                and "./" not in lastOutput
            ):
                output = possibleOut.replace("^", "")
                translatedOutput += output
                lastOutput = output
                i += howLong
                translated = True
                return

            continue

        # ^xxx = must NOT be at beginning of word

        if possibleOut.startswith('^'):
            if i > 0 and inputarr[i - 1] != "000000":
                output = possibleOut.replace("^", "")
                translatedOutput += output
                lastOutput = output
                i += howLong
                translated = True
                return

            continue

        # xxx^ = must NOT be at end of word

        if possibleOut.endswith('^'):
            if (
                i + howLong < len(inputarr)
                and inputarr[i + howLong] != "000000"
            ):
                output = possibleOut.replace("^", "")
                translatedOutput += output
                lastOutput = output
                i += howLong
                translated = True
                return

            continue

    # Normal fallback

    if howLong == 5:
        shorter_exists = (
            fourLong in brailleLib
            or threeLong in brailleLib
            or twoLong in brailleLib
            or oneLong in brailleLib
        )

    elif howLong == 4:
        shorter_exists = (
            threeLong in brailleLib
            or twoLong in brailleLib
            or oneLong in brailleLib
        )

    elif howLong == 3:
        shorter_exists = (
            twoLong in brailleLib
            or oneLong in brailleLib
        )

    elif howLong == 2:
        shorter_exists = oneLong in brailleLib

    else:
        shorter_exists = False

    if not translated and not shorter_exists:
        output = brailleLib[whatLong][0]

        # Preserve your punctuation special case.
        if howLong == 1 and any(
            punctuation in brailleLib[oneLong]
            for punctuation in [".", ",", "!"]
        ):
            output = brailleLib[oneLong][1]

        translatedOutput += output
        lastOutput = output
        i += howLong
        translated = True


def transliterateBin(inputB, enabled_contractions, brailleLib):
   # global b2b
    global translated
    global translatedOutput
    global i
    global lastOutput

    # Load active contraction words dynamically
    
    
    inputarr = []
    i = 0

    #inputB is the line to be translated, and it chunks it into 6 digit chunks, and puts each chunk in a list
    while (i <= len(inputB) - 6):
        newStr = ""

        for j in range(6):
            newStr += inputB[i + j]
        inputarr.append(newStr)
        i += 6


    i = 0
    translatedOutput = ""
    lastOutput = ""
    

    inputarr.insert(0, "000000")
    inputarr.append("000000")

    
    while (i < len(inputarr)):
        fiveLong = ""
        fourLong = ""
        threeLong = ""
        twoLong = ""
        oneLong = ""

        #creating strings of 1, 2, 3, 4, and 5 braille characters to check for contractions
        
        if i <= len(inputarr) - 5:
            fiveLong = inputarr[i] + inputarr[i + 1] + inputarr[i + 2] + inputarr[i + 3] + inputarr[i + 4]
        if i <= len(inputarr) - 4:
            fourLong = inputarr[i] + inputarr[i + 1] + inputarr[i + 2] + inputarr[i + 3]
        if i <= len(inputarr) - 3:
            threeLong = inputarr[i] + inputarr[i + 1] + inputarr[i + 2]
        if i <= len(inputarr) - 2:
            twoLong = inputarr[i] + inputarr[i + 1]
        
        oneLong = inputarr[i]
        
        translated = False

        findOutput(fiveLong, 5, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib)
        findOutput(fourLong, 4, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib)
        findOutput(threeLong, 3, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib)
        findOutput(twoLong, 2, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib)
        findOutput(oneLong, 1, fourLong, threeLong, twoLong, oneLong, enabled_contractions, inputarr, brailleLib)
        if not translated:
            i += 1
    
    # print(translatedOutput)
    translatedOutput = translatedOutput.replace("_", "")
    # print(translatedOutput)
    
    while("./" in translatedOutput):
            if "./capital letter" in translatedOutput:
                capitalLetter_i = translatedOutput.find("./capital letter") + 16
                translatedOutput = translatedOutput[:capitalLetter_i] + translatedOutput[capitalLetter_i].upper() + translatedOutput[capitalLetter_i + 1:]
                translatedOutput = translatedOutput.replace("./capital letter", "", 1)
            if "./capital word" in translatedOutput:
                capitalWord_start = translatedOutput.find("./capital word") + 14
                capitalWord_end = translatedOutput[capitalWord_start:].find(" ") + capitalWord_start
                translatedOutput = translatedOutput[:capitalWord_start] + translatedOutput[capitalWord_start:capitalWord_end].upper() + translatedOutput[capitalWord_end:]
                translatedOutput = translatedOutput.replace("./capital word", "", 1)
            if "./capital passage" in translatedOutput:
                capitalPassage_start = translatedOutput.find("./capital passage") + 17
                if translatedOutput[capitalPassage_start:].find("./capital terminator") != -1:
                    capitalPassage_end = translatedOutput[capitalPassage_start:].find("./capital terminator") + capitalPassage_start
                    translatedOutput = translatedOutput[:capitalPassage_start] + translatedOutput[capitalPassage_start:capitalPassage_end].upper() + translatedOutput[capitalPassage_end:]
                else:
                    translatedOutput = translatedOutput[:capitalPassage_start] + translatedOutput[capitalPassage_start:].upper()
                
                translatedOutput = translatedOutput.replace("./capital passage", "", 1)
                translatedOutput = translatedOutput.replace("./capital terminator", "", 1)
            if "./numeric indicator" in  translatedOutput:
                a_to_n = {"a" : "1", "b" : "2", "c" : "3", "d" : "4", "e" : "5", "f" : "6", "g" : "7", "h" : "8", "i" : "9"}
                number_i = translatedOutput.find("./numeric indicator") + 19
                while (translatedOutput[number_i] in a_to_n.keys()):
                    translatedOutput = translatedOutput[:number_i] + a_to_n[translatedOutput[number_i]] + translatedOutput[number_i + 1:]
                    number_i += 1
                translatedOutput = translatedOutput.replace("./numeric indicator", "", 1)


    translatedOutput = translatedOutput.strip()
    f_out = open('transliterateOutput.txt', 'a')
    f_out.write(translatedOutput)
    print("\n", end='')
    print(translatedOutput)
    f_out.close()
    
    #print(translatedOutput.split())

    #Returned last word is used for TTS, so that the user can hear the last word they typed
    # if translatedOutput.split(): 
    #     # print(translatedOutput.split()[-1])

    if translatedOutput:
        return translatedOutput.split()[-1] # Return last "word"
