#!/bin/sh

VERSION=$1

mkdir /var/www/pythonapps/pawseyportal/$VERSION

git archive --format=tar --prefix=$VERSION/ $VERSION | (cd /var/www/pythonapps/pawseyportal/ && tar xf -)

virtualenv --system-site-packages /var/www/pythonapps/pawseyportal/$VERSION/virtualenv
# Activate virtualenv put these into a requirements file
source /var/www/pythonapps/pawseyportal/$VERSION/virtualenv/bin/activate
pip install django==1.9.4
pip install django_auth_ldap
pip install django_ajax_selects
pip install commonware

cd /var/www/pythonapps/pawseyportal/$VERSION
python manage.py collectstatic --noinput
python manage.py migrate
