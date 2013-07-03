# Deploy nitrate for OpenShift
### 1. Create non-scalable python-2.6 app and embedded mysql cartridge.

    #rhc app-create tcms python-2.6 mysql-5.1
    

Then you will get the database information (ipaddress,port,username,password), the app information(ipaddress,port).

### 2. SSH into the app
(1)create two directory:

    #mkdir /tmp/uploads /tmp/log

(2)create database named "nitrate" in mysql

### 3.Get the nitrate project.

    #git clone git@github.com/xltian/nitrate.git

And copy the source code to the app.

    # cp -rf nitrate/* tcms/

### 4.Modify the folllowing environment variables in  tcms/settings.py like following
    DATABASE_ENGINE = 'mysql'     
    DATABASE_NAME = 'nitrate'        
    DATABASE_USER = os.environ['OPENSHIFT_MYSQL_DB_USERNAME']        
    DATABASE_PASSWORD = os.environ['OPENSHIFT_MYSQL_DB_PASSWORD']     
    DATABASE_HOST = os.environ['OPENSHIFT_MYSQL_DB_HOST']              
    DATABASE_PORT = os.environ['OPENSHIFT_MYSQL_DB_PORT'] 

### 5. Replace  wsgi/application file with the following content:
    #!/usr/bin/python
    import os
    import sys
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tcms.settings'
    sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR']))
    virtenv = os.environ['OPENSHIFT_PYTHON_DIR'] + '/virtenv/'
    os.environ['PYTHON_EGG_CACHE'] = os.path.join(virtenv, 'lib/python2.6/site-packages')
    virtualenv = os.path.join(virtenv, 'bin/activate_this.py')
    try:
      execfile(virtualenv, dict(__file__=virtualenv))
    except IOError:
      pass

    import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()

### 6. Commit above changes in step 4 and step 5  and git push 

### 7.Initial database
   SSH into the app
    
   # mysql -u [db_username] -p nitrate < ${OPENSHIFT_REPO_DIR}/docs/testopia-dump-blank.sql
   # mysql -u [db_username] -p nitrate < ${OPENSHIFT_REPO_DIR}/docs/mysql_initial.sql

    
    If this is your first time, please run "django-admin.py syncdb", and create superuser, if not, skip this step
    
    django-admin.py syncdb
