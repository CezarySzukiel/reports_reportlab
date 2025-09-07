from reportlab.lib.pagesizes import A4, LETTER, landscape
from reportlab.lib.units import cm, inch, mm
from reportlab.pdfgen import canvas

from src.config import ASSETS_PATH

c = canvas.Canvas(str(ASSETS_PATH / "pages_units.pdf"), pagesize=landscape(A4))
width, height = landscape(A4)


c.drawString(10 * mm, height - 10 * mm, "Nagłówek 10mm od lewej i góry.")
c.drawString(2 * cm, height - 2 * cm, "Pozycjonowanie w cm.")
c.drawString(2 * inch, height - 2 * inch, "Pozycjonowanie w inch.")

c.showPage()

c.setPageSize(LETTER)
c.drawString(72, height - 72, "Now strona")

c.save()
