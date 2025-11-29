rm -Recurse build
rm -Recurse dist

pyinstaller --onefile --runtime-tmpdir=. --hidden-import win32timezone windows_service.py
.\dist\windows_service.exe --startup delayed install