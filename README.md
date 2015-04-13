USAGE
=====
VRay
----

> **Note:**
> Arnold and Mantra will be supported later - Contributors welcome!

1. Export one or more .vrscene-files from your host-application 
2. drag&drop the .vrscene(s) from your filebrowser into the GUI.
3. hit sync and wait for the uplaod to finish - if successful the "synced"-field will say True
4. Hit submit and you are done - now log-in to the webinterface of your afanasy-server and wait for your renderjob to finish!
5. When your job(s) are done just click "sync images" and the application will try to download the files that are found inside your vrscene! It will not check the whole S3 bucket!

PREREQUISITES
=============
Python - on Windows only:
----------------

Please install python 2.7.9 including pip

PySide
------

Linux - yum based distros:

```
sudo yum install python-pyside
```

> **Note:**
> On Centos 7 you have to compile & install PySide by yourself as described here:
> http://unix.stackexchange.com/questions/160496/how-to-install-pyside-package-for-centos-7

OSX:

install macports and do:
```
sudo port install py-pyside
```
Windows:
```
pip install -U PySide
```

Boto
----

Windows (might also work on Linux/MacOs):
```
pip install -U boto
```
Linux/Mac - from source:
```
git clone https://github.com/boto/boto.git
cd boto
sudo python setup.py install
```

INSTALL
=======

```
git clone https://github.com/ultra-sonic/opencloudrender.git
cd opencloudrender
#get cgru rendermanger - submodule
git submodule init
git submodule update
```
> **Note:**
> I originally intended to install opencloudrender using distutils, but due to the dependency on "cgru/afanasy" this seems impossible.
> If anybody comes up with a clever way let me know!

CONFIGURE
=========
Afanasy
---------
you must configure the hostname or ip of your afserver here:
cgru/afanasy/config_default.json

just change this line:
"af_servername":"yourserver.here.com",
Boto
-----
please copy .boto-default to your user-home and rename it to .boto
now fill in your own aws credentials - also remove those <> brackets
> **Note:**
> Windows might complain that you cannot rename the file for some strange reason. Open the file in a texteditor and "Save as..." .boto

LAUNCH
======
just launch 
```
bin/ocrSubmitUI.sh
```
or
```
bin/ocrSubmitUI.bat
```

SETUP-ASSISTANCE
================
During the beta phase I will offer free assistance to selected users. After that I can give paid setup-assistance to anyone who needs it! Feel free to get in touch!

CONTRIBUTION
============
I am always thankful for people doing code revision!
If you want to contribute Arnold or Mantra functionality you are more than welcome to do so!