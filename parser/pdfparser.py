import fitz
import re
import glob
from tqdm import tqdm

class PDFParser():

    def __init__(self, dir):
        self.dir = dir
        self.docs = [f for f in glob.glob("{}/*.pdf".format(self.dir))]

    def save_text(self, doc):
        try:
            document = fitz.open(doc)
            no_pages = document.pageCount
            doc_text = self.process_document(document, no_pages)
            file_name = '../txts' + doc[doc.rfind('/'):-4] + '.txt'
            with open(file_name, 'w') as f:
                f.write(doc_text)
        except:
            print(doc)


    def save_all(self):
        for doc in tqdm(self.docs):
            self.save_text(doc)

    def process_text(self, text):
        text = text.strip() # remove trailing spaces
        text = re.sub(r'\n', '', text) # remove new line
        text = re.sub(' +', ' ', text).strip() # remove multiple spaces
        text = re.sub(r'[^a-zA-Z0-9 ,.;()\'"]', '', text) # remove anything that is not alphanumeric or punctuation

        return text

    def process_page(self, document, page_no):
        page = document.loadPage(page_no)
        page_text = page.getText("blocks")
        text = [x for _, _, _, _, x, _, _ in page_text]
        text = ''.join(text)
        text = self.process_text(text)

        return text

    def process_document(self, document, no_pages):
        text = ''
        for i in range(no_pages):
            text += self.process_page(document, i)

        return text

if __name__ == "__main__":
    pdf_parser = PDFParser("../../national-climate-plans/pdfs")
    pdf_parser.save_all()
