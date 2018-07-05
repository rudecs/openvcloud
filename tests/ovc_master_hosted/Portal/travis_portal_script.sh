location=${1}
environment=https://${location}.demo.greenitglobe.com
admin=${2}
passwd=${3}
secret=${4}
directory=${5}
browser=${6}
ctrl_password=${7}

install_portal_requirements(){
    pip3 install virtualenv
    virtualenv env
    source env/bin/activate
    pip3 install -r requirements.txt
    apt-get install -y xvfb chromium-chromedriver
    # curl -o 'https://chromedriver.storage.googleapis.com/2.33/chromedriver_linux64.zip' /tmp/chromedriver_linux64.zip && unzip /tmp/chromedriver_linux64.zip -o /usr/lib/chromium-browser/
    ln -fs /usr/lib/chromium-browser/chromedriver /usr/bin/chromedriver
    ln -fs /usr/lib/chromium-browser/chromedriver /usr/local/bin/chromedriver
}

echo "Install Portal Requirements ..."
echo "${ctrl_password}" | sudo -S bash -c "$(declare -f install_portal_requirements); install_portal_requirements"

echo "Run Tests ..."
cd functional_testing/Openvcloud/ovc_master_hosted/Portal
xvfb-run -a nosetests-3.4 -v -s --exe --logging-level=WARNING ${directory} --tc-file=config.ini --tc=main.passwd:${passwd} --tc=main.secret:${secret} --tc=main.env:${environment} --tc=main.location:${location} --tc=main.admin:${admin} --tc=main.browser:${browser} 