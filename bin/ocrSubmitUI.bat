rem # minimal afanasy setup
set CGRU_LOCATION=%~dp0/../cgru
set AF_ROOT=%CGRU_LOCATION%/afanasy
set PYTHONPATH=%~dp0/..;%CGRU_LOCATION%/lib/python;%AF_ROOT%/python;$PYTHONPATH
echo PYTHONPATH: %PYTHONPATH%
rem # afanasy done

python.exe %~dp0/ocrSubmitUI.py
pause