rem # minimal afanasy setup
set CGRU_LOCATION=%~dp0/cgru
set AF_ROOT=%CGRU_LOCATION%/afanasy
set PYTHONPATH=%CGRU_LOCATION%/lib/python;%AF_ROOT%/python;$PYTHONPATH
echo PYTHONPATH: %PYTHONPATH%
rem # afanasy done

python -c "import opencloudrender as ocr;ocr.showUI()"