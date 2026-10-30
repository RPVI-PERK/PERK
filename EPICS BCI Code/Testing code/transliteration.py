# For Raspberry Pi
import ast
import time
# import gpiozero
# from gpiozero import DigitalInputDevice, DigitalOutputDevice, Button
import subprocess
import threading
import wave
import os
import json
# from piper import PiperVoice, SynthesisConfig

from transliterateBinary import transliterateBin

# def powerDown():
#     subprocess.run("aplay off.wav", shell = True)
#     subprocess.run('i2cset -y 1 0x18 0x00 0x01 && i2cset -y 1 0x18 0x2A 0x00', shell = True) # disable speaker
#     subprocess.run('sudo shutdown now', shell = True)

# model = "en_US-amy-medium.onnx"
# global voice
# global pair
# global speaker
# global held
# voice = PiperVoice.load(model)
# pair = Button(24, bounce_time=0.1)
# speaker = True
# held = False
# def switchAudio():
#     global voice
#     global speaker
#     global held
#     held = True
#     if speaker:
#        TTS("Headphone", voice)
#        subprocess.run('bash headphone.sh', shell = True)
#        speaker = False
#     else:
#        subprocess.run('bash speaker.sh', shell = True)
#        TTS("Speaker", voice)
#        speaker = True
#     time.sleep(0.2)
# def networkSearch():
#     global voice
#     global speaker
#     global pair
#     global held
#     if held:
#         held = False
#         return
#     subprocess.run('aplay search.wav', shell = True)
#     out = subprocess.check_output('sudo nmcli -f NAME connection show', shell = True)
#     for net in out.decode('utf-8').split("\n"):
#         if net[0:5] == "perk-":
#             out = subprocess.check_output(f'sudo nmcli connection delete {net}', shell = True)
#     out = subprocess.check_output('sudo nmcli -t -f SSID,SIGNAL dev wifi list', shell = True)
#     print(out.decode('utf-8'))
#     for net in out.decode('utf-8').split("\n"):
#         net = net.split(":")
#         if net[0][0:5] == "perk-":
#             subprocess.run(f'sudo nmcli dev wifi connect {net[0]} password perk12345', shell = True)
#             TTS(net[0], voice)
#             return
#     subprocess.run("aplay fail.wav", shell = True)

#pair.when_pressed = networkSearch
   

# def HallEffectRead(hallEffect, out):
#     outputnum = ""
#     for i in range(8):
#         for j in range(3):
#             hallEffect[j].on() if (i >> j) & 1 else hallEffect[j].off()
#         time.sleep(0.001)
#         outputnum += str(out.value)
#     return outputnum
     
 
# def TTS(word, voice):
#     syn = SynthesisConfig(volume = 1.5)
#     try:
#         with wave.open("output.wav", "wb") as f:
#             voice.synthesize_wav(word, f, syn_config=syn)
#         subprocess.run(['aplay', 'output.wav'], check = True)
#     except Exception as e: 
#         print(f"TTS error: {e}") 
        

def load_enabled_contractions(json_path='EPICS BCI Code/Testing code/enabled_contractions.txt'):
    """Reads JSON library and returns set of enabled contraction words."""
    if not os.path.exists(json_path):
        return set()
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            contraction_data = json.load(f)
            # print(contraction_data)
            return {
                word for word, details in contraction_data.items()
                if details.get("enabled", 0) == 1
            }
    except Exception:
        return set()

enabled_contractions = load_enabled_contractions()
print(enabled_contractions)

with open('EPICS BCI Code/Testing code/brailleLib.txt', 'r') as f:
    data = f.read()
brailleLib = ast.literal_eval(data)


#model = "en_US-amy-medium.onnx"
currentLine = 0
lastWordList = []
#voice = PiperVoice.load(model)
# open("output.txt", 'w').close()
# subprocess.run('aplay ready.wav', shell = True)

# hallEffect = [DigitalOutputDevice(f"BOARD{pin}", active_high = True) for pin in [31, 33, 37]]
# mux_out = DigitalInputDevice(f"BOARD36", pull_up = True)

# on_off = Button(23, bounce_time=0.1)
# #pair = Button(24,bounce_time=0.1)

# on_off.when_pressed = powerDown
# pair.when_released = networkSearch
# pair.when_held = switchAudio
binArray = []
space_press = 0
line_press = 0
current_line = 0
lastWord = ""
while True:
    # output = HallEffectRead(hallEffect, mux_out)
    output = input("Enter 8-bit binary string (00010001, fourth is space, eighth is newline): ")
    #00010001
    # newline = int(output[4])
    # space = int(output[6])
    # keys = output[5] + output[7] + output[3] + output[2] + output[1] + output[0]

    newline = int(output[7])
    space = int(output[3])
    keys = output[2] + output[1] + output[0] + output[4] + output[5] + output[6]

    
    
    if space:
        space_press = 1
        currentBinary = keys

    if space_press:
        print(currentBinary)
        # if lastWord and currentBinary == "000000": 
        #     # TTS(lastWord, voice)
        space_press = 0
        if current_line >= len(binArray):
            binArray.append(currentBinary)
        else:
            binArray[current_line] += currentBinary

        i = 0
        while i < len(binArray[current_line]):
            print(f"{binArray[current_line][i:(i+6)]} ",  end='')
            i += 6
        print()

        with open("tempbin.txt", 'w') as f:
            with open("transliterateOutput.txt", "w") as f_t:
                pass
            for line in binArray:
                f.write(line + '\n')
                #last word is returned from transliterateBin function and is used for TTS
                lastWord = transliterateBin(line, enabled_contractions, brailleLib)
                with open("transliterateOutput.txt", 'a') as f_out:
                    f_out.write("\n")           
    if newline:
        line_press = 1
    elif line_press:
        line_press = 0
        current_line += 1
   
    # time.sleep(0.1)
