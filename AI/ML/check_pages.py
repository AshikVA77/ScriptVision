import fitz

pdf_path = r"E:\Main Project\ScriptVision\AI\dataset\Student_1.pdf"

doc = fitz.open(pdf_path)

print("Number of pages:", len(doc))

for i in range(len(doc)):
    print("Page:", i + 1)

doc.close()