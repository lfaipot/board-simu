set PYTHONPATH=%PYTHONPATH%;src;src\Ui;src\hardware\arch;src\hardware\device
rem check if python is defined into the path
where python.exe
if errorlevel 1 (
	echo assume python is installed at the usual place
  	C:\Python27\python.exe src\boardSimu.py
) else (
	echo python is included into PATH
	python.exe src\boardSimu.py
)