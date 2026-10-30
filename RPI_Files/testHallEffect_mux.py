import time
import gpiozero
import threading

hallEffect = []

for pin in [31,33,37]:
	hallEffect.append(gpiozero.DigitalOutputDevice(f"BOARD{pin}", active_high = True))
output = gpiozero.DigitalInputDevice(f"BOARD36", pull_up = True)
outputnum = []
io = gpiozero.DigitalInputDevice(f"BOARD11")
def hallEffectRefresh():
    global outputnum
    global hallEffect
    outputnum = []
    for i in range(8):
        for j in range(3):
            hallEffect[j].on() if (i >> j) & 1 else hallEffect[j].off()
        time.sleep(0.005)
        
        outputnum.append(str(output.value))
       # outputnum.append(str(io.value))

    print(' '.join(outputnum), end='\r', flush=True)
    threading.Timer(0.1, hallEffectRefresh).start()

print("\n=============================")
print("PERK Input Testing Tool")
print("=============================\n")
hallEffectRefresh()
