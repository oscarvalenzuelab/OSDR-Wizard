#!/bin/bash
sudo apt install python3-pip python3-dev
sudo apt autoremove
rm -rf envosdr
python3 -m venv envosdr
activate="envosdr/bin/activate"
if [ ! -f "$activate" ]
then
    echo "ERROR: activate not found at $activate"
    return 1
fi
. "$activate"
pip3 install --upgrade pip
rm -rf app/dbosdr.sqlite3
rm -rf instance/
rm -rf migrations/
pip3 install -r requirements.txt
exit
pycodestyle --ignore=E402,E722,E126,E127,E128 --exclude='envosdr/' . > pep8.log
export FLASK_CONFIG=development
export FLASK_APP=run.py
mkdir instance
echo "SECRET_KEY = 'p9Bv<3Eid9%i01'" > instance/config.py
echo "SQLALCHEMY_DATABASE_URI = 'sqlite:///envosdr.sqlite3'" >> instance/config.py
flask db init >> install.log
flask db migrate >> install.log
flask db upgrade >> install.log
echo "Importing SPDX Dataset"
cat datasets/spdx.sql | sqlite3 app/dbosdr.sqlite3
echo "Importing ThunderaBSA DB dump"
cat datasets/dbosdr.sql | sqlite3 app/dbosdr.sqlite3
echo "Creating admin user" 1>&2
read -p "Email address: " ADMIN_EMAIL_ADDRESS
read -p "First name: " ADMIN_FIRST_NAME
read -p "Last name: " ADMIN_LAST_NAME
read -s -p "Password: " ADMIN_PASSWORD && echo 1>&2
ADMIN_PASSWORD_HASH=`python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('$ADMIN_PASSWORD'))"`
echo $ADMIN_PASSWORD
sqlite3 -line app/dbthundera.sqlite3 "INSERT INTO users VALUES(1,'$ADMIN_EMAIL_ADDRESS','$ADMIN_FIRST_NAME','$ADMIN_LAST_NAME','$ADMIN_PASSWORD_HASH',1,1);"
echo "Launching OSDR"
flask run
deactivate
