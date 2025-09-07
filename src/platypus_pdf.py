# from pprint import pprint as pp


# pdfmetrics.registerFont(TTFont("Roboto-Light-Italic", "./fonts/Roboto-LightItalic.ttf"))
#
# doc = SimpleDocTemplate("pdf/platypus_intro.pdf", pagesize=A4)
# styles = getSampleStyleSheet()
#
# styles["Title"].fontName = "Roboto-Light-Italic"
# styles["BodyText"].fontName = "Roboto-Light-Italic"
#
# # pp(vars(styles["Title"]))
#
# img = ImageReader("img/ml_alg.jpg")
# iw, ih = img.getSize()
# scale = 300 / ih
#
# story = [
#     Paragraph("Tytuł dokumentu", styles["Title"]),
#     Spacer(1, 12),
#     Paragraph("To jest akapit treści. Platypus automatycznie zawija tekst i obsługuje style." * 30,
#               styles["BodyText"]),
#     Spacer(1, 24),
#     Image("img/ml_alg.jpg", width=iw * scale, height=ih * scale)
# ]
#
# doc.build(story)
