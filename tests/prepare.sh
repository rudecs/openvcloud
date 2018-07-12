
echo "[+] Install requirements ..."
apt update
apt-get install python-dev build-essential libssl-dev libffi-dev \
    libxml2-dev libxslt1-dev zlib1g-dev \
    python-pip python3-pip iputils-ping tmux wget unzip -y

pip install -r requirements.txt
pip3 install -r ovc_master_hosted/Portal/requirements.txt
chmod 777 ovc_master_hosted/Portal

echo "[+] Download chrome driver for portal tests ..."
apt-get install -y xvfb chromium-chromedriver -y
ln -fs /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
ln -fs /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver