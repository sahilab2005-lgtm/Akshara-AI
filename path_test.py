import os

path = r"C:\Users\Acer\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"

print(os.path.exists(path))
print(os.path.exists(path + r"\pdfinfo.exe"))