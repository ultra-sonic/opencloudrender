PREREQUISITES:
==============
0. Python - Windows only:
----------------

Please install python 2.7.9 including pip

1. PySide
---------

Linux - yum based distros:

```
sudo yum install python-pyside
```

> **Note:**
> On Centos 7 you have to compile & install PySide by yourself as described here:
> http://unix.stackexchange.com/questions/160496/how-to-install-pyside-package-for-centos-7

OSX:

```
install macports and do:
sudo port install py-pyside
```
Windows:
```
pip install -U PySide
```

2. Boto
-------

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

INSTALL:
========

```
git clone https://github.com/ultra-sonic/opencloudrender.git
cd opencloudrender
#get cgru rendermanger - submodule
git submodule init
git submodule update
```

CONFIGURE:
==========
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

LAUNCH:
=======
just launch 
```
bin/ocrSubmitUI.sh
or 
bin/ocrSubmitUI.bat)
```