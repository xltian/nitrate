# Deploy nitrate for OpenShift
### 1. Create non-scalable python-2.6 app and embedded mysql cartridge.

    rhc app create tc python-2.6
    rhc cartridge add mysql-5.1 -a tc

Then you will get the database information (ipaddress,port,username,password), the app information(ipaddress,port).

    [root@test12 ~]# rhc app show tc 
    tc @ http://tc-xjia.rhcloud.com/ (uuid: 516790c9e0b8cd412f0000f9)
    -----------------------------------------------------------------
      Created: 9:42 PM
      Gears:   1 (defaults to small)
      Git URL: ssh://516790c9e0b8cd412f0000f9@tc-xjia.rhcloud.com/~/git/tc.git/
      SSH:     516790c9e0b8cd412f0000f9@tc-xjia.rhcloud.com
      python-2.6 (Python 2.6)
      -----------------------
        Gears: Located with mysql-5.1
      mysql-5.1 (MySQL Database 5.1)
      ------------------------------
        Gears:          Located with python-2.6
        Connection URL: mysql://$OPENSHIFT_MYSQL_DB_HOST:$OPENSHIFT_MYSQL_DB_PORT/
        Database Name:  tc
        Password:       4KzRqQLrqliN
        Username:       adminYClnU3H

You can ssh into the app, get the variable value for $OPENSHIFT_MYSQL_DB_HOST:$OPENSHIFT_MYSQL_DB_PORT.
    
    [root@test12 ~]# ssh 516790c9e0b8cd412f0000f9@tc-xjia.rhcloud.com
    [tc-xjia.rhcloud.com 516790c9e0b8cd412f0000f9]\> echo $OPENSHIFT_MYSQL_DB_HOST:$OPENSHIFT_MYSQL_DB_PORT
    127.10.64.1:3306

### 2. SSH into the app
(1)create two directory:

    mkdir /tmp/uploads /tmp/log

(2)create database named "nitrate"

### 3.Get the nitrate project.

    git clone git@github.com:xuanjia/nitrate.git

### 4.Edit tcms/settings.py

Modify these items:

    DATABASE_ENGINE = 'mysql'
    DATABASE_NAME = 'nitrate' 
    DATABASE_USER = 'adminYClnU3H'
    DATABASE_PASSWORD = '4KzRqQLrqliN'
    DATABASE_HOST = '127.10.64.1'
    DATABASE_PORT = '3306' 
    INTERNAL_IPS = ('127.10.64.1', )

Then git push

### 5.Stop http process in this app

    rhc cartridge stop python-2.6 -a tc

### 6.Initial database
SSH into the app
    
    mysql -u [db_username] -p nitrate < ${OPENSHIFT_REPO_DIR}/docs/testopia-dump-blank.sql
    mysql -u [db_username] -p nitrate < ${OPENSHIFT_REPO_DIR}/docs/mysql_initial.sql

### 7.Start django service
SSH into the app

    virtualenv --system-site-packages ${OPENSHIFT_HOMEDIR}/python-2.6/virtenv
    . ${OPENSHIFT_HOMEDIR}/python-2.6/virtenv/bin/activate
    cd ${OPENSHIFT_REPO_DIR}
    export PYTHONPATH=${OPENSHIFT_REPO_DIR}
    export DJANGO_SETTINGS_MODULE=tcms.settings
    
If this is your first time, please run "django-admin.py syncdb", and create superuser, if not, skip this step
    
    django-admin.py syncdb
    
Start django server
    
    nohup django-admin.py runserver ${OPENSHIFT_PYTHON_IP}:${OPENSHIFT_PYTHON_PORT} &
    
### 8.Stop django service
SSH into the app

    kill `ps -ef | grep django | grep -v grep | awk '{ print $2 }'` > /dev/null 2>&1

