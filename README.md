PREREQUISITES:

0. Windows only:
	install python 2.7.9 including pip

1. PySide
	Linux - yum:
		sudo yum install python-pyside
	Linux - apt-get:
		to be done

	On Centos 7 you have to compile & install PySide by yourself as described here:
		http://unix.stackexchange.com/questions/160496/how-to-install-pyside-package-for-centos-7

	OSX:
		install macports and do:
		sudo port install py-pyside

	Windows:
		pip install -U PySide

2. boto
	Windows (might also work on Linux/MacOs):
		pip install -U boto
	Linux/Mac - from source:
		git clone https://github.com/boto/boto.git
		cd boto
		sudo python setup.py install

INSTALL:

	git clone adresse here
	cd opencloudrender
	#get cgru rendermanger - submodule
	git submodule init
	git submodule update

CONFIGURE:

	you must configure the hostname or ip of your afserver here:
		cgru/afanasy/config_default.json
	just change this line:
			"af_servername":"yourserver.here.com",

	please copy .boto-default to your user-home and rename it to .boto
	now fill in your own aws credentials - also remove those <> brackets

LAUNCH:

	just launch bin/ocrSubmitUI.sh (or .bat)
