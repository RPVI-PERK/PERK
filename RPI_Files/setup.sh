if nmcli -t -f DEVICE,STATE device | grep -q "^wlan:0:unavailable"; then
    echo "Network unavailable. Setting WLAN Country to US"
    sudo raspi-config nonint do_wifi_country US
fi
if nmcli -t -f DEVICE,STATE device | grep -q "^wlan:0:connected"; then
    echo "Internet!"
fi
if nmcli -t -f DEVICE,STATE device | grep -q "^wlan:0:disconnected"; then
    echo "You need an internet connection for this script."
    exit 1
fi
echo -n "Fetching Perk Files..."
if [ -e RPI_Files.zip ]
then 
    echo "Zip folder found"
    unzip RPI_Files.zip
    rm RPI_Files.zip
else 
    echo "Please use transfer the zip file from the repository into the Pi."
fi
echo "Done."

cd ~/RPI_Files

echo -n "Setting up I2C..."
sudo raspi-config nonint do_i2c 0
echo "Done."

echo -n "Creating venv..."
python -m venv pyperk --system-site-packages
echo "Done."

echo "Installing PiperVoice"
pyperk/bin/python -m pip install piper-tts

echo "Installing amy-medium"
pyperk/bin/python -m piper.download_voices en_US-amy-medium

echo "Installing i2c-tools"
sudo apt-get install -y i2c-tools

echo -n 'Enabling i2s...'
echo 'dtoverlay=i2s-dac' | sudo tee -a /boot/firmware/config.txt
sudo sed -i 's/^#dtparam=i2s=on/dtparam=i2s=on/' /boot/firmware/config.txt
echo 'Done.' 

echo "Pi Ready!."
echo "The Pi will reboot now."

sudo reboot now