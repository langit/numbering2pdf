from io import BytesIO
import os

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PyPDF4.pdf import PdfFileReader, PdfFileWriter

standard_fonts = (
    "Courier", "Courier-Bold", "Courier-Oblique", "Courier-BoldOblique",
    "Helvetica", "Helvetica-Bold", "Helvetica-Oblique", "Helvetica-BoldOblique",
    "Times-Roman", "Times-Bold", "Times-Italic", "Times-BoldItalic",
    "Symbol", "ZapfDingbats",
)

def add_numbering_to_pdf(pdf_file, new_pdf_file_path=None, position="center", 
                         start_page=1, end_page=None,
                         start_index=1, size=14, font="Times-Roman") -> bytes:
    """Adds numbering to pdf file"""
    pdf_file = get_pdf_file(pdf_file)
    original_pdf = PdfFileReader(BytesIO(pdf_file), strict=False)
    end_page = end_page or original_pdf.getNumPages() + 1
    empty_numbered_pdf = create_empty_numbered_pdf(original_pdf, position, 
                            start_page, end_page, start_index, size, font)
    new_pdf_file = merge_pdf_pages(original_pdf, empty_numbered_pdf)
    if new_pdf_file_path:
        save_file(new_pdf_file, new_pdf_file_path)
    else: return new_pdf_file


def get_pdf_file(pdf_file) -> bytes:
    """Path like string to file"""
    if isinstance(pdf_file, str):
        if isinstance(pdf_file, os.PathLike):
            pdf_file = os.fspath(pdf_file)
        file = open(pdf_file, "br")
        pdf_file = file.read()
        file.close()
    return pdf_file

alt_position = {
    "inner": ("right","left"),
    "outer": ("left","right")}
position_to_width = {
    "left": 10,
    "center": 38,
    "right": 65.5}
def create_empty_numbered_pdf(original_pdf, position, start_page, end_page, 
                              start_index, size, font) -> PdfFileReader:
    """Returns empty pdf file with numbering only"""
    number_of_pages = original_pdf.getNumPages()
    empty_canvas = canvas.Canvas("empty_canvas.pdf")
    for index in range(number_of_pages):
        page_num = index - start_page + start_index
        number = str(page_num) if start_page<=index<end_page else ""
        page_pos = position if position in position_to_width else \
            alt_position[position][page_num%2]
        pagebox = original_pdf.getPage(index).mediaBox
        ratio = pagebox.getWidth() / 200 # A4 paper?
        height = 15 * mm #from bottom? pagebox.getHeight()
        width_on_page = position_to_width[page_pos] * float(ratio) * mm
        empty_canvas.setFont(font, size)
        empty_canvas.drawString(width_on_page, height, number)
        empty_canvas.showPage()
    return PdfFileReader(BytesIO(empty_canvas.getpdfdata()))


def merge_pdf_pages(first_pdf, second_pdf) -> bytes:
    """Returns file with combined pages of first and second pdf"""
    writer = PdfFileWriter()
    for number_of_page in range(first_pdf.getNumPages()):
        page_of_first_pdf = first_pdf.getPage(number_of_page)
        page_of_second_pdf = second_pdf.getPage(number_of_page)
        page_of_first_pdf.mergePage(page_of_second_pdf)
        writer.addPage(page_of_first_pdf)
    result = BytesIO()
    writer.write(result)
    return result.getvalue()


def save_file(new_pdf_file, new_pdf_file_path) -> None:
    """Saves file with new file name"""
    with open(new_pdf_file_path, "bw") as file:
        file.write(new_pdf_file)
