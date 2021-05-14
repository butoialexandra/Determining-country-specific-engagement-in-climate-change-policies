import fitz
import re

class PDFParser():

    def __init__(self, pdf_document):
        self.document = fitz.open(pdf_document)
        self.no_pages = self.document.pageCount
        self.doc_text = self.process_document(self.document)

    def save_text(self):
        pass

    def process_text(self, text):
        text = text.strip() # remove trailing spaces
        text = re.sub(r'\n', '', text) # remove new line
        text = re.sub(' +', ' ', text).strip() # remove multiple spaces

        return text

    def process_page(self, document, page_no):
        page = document.loadPage(page_no)
        page_text = page.getText("blocks")
        text = [x for _, _, _, _, x, _, _ in page_text]
        text = ''.join(text)

        return text

    def process_document(self, document):
        text = ''
        for i in range(self.no_pages):
            text += self.process_page(document, i)

        return text

if __name__ == "__main__":
    pdf_parser = PDFParser('../../national-climate-plans/pdfs/AFG_Afghanistan_First_NDC_English.pdf')
    print(pdf_parser.doc_text)
