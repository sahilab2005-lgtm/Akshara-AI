from pdf2image import convert_from_path

pdf_path = "sample6.pdf"

pages = convert_from_path(
    pdf_path,
    poppler_path=r"C:\Users\Acer\Downloads\Release-26.02.0-0\poppler-26.02.0\Library\bin"
)

print("Pages:", len(pages))