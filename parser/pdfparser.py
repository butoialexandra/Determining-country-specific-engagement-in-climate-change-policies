import fitz
import re
import glob
from tqdm import tqdm

class PDFParser():

    def __init__(self, dir):
        self.dir = dir
        self.docs = [f for f in glob.glob("{}/*.pdf".format(self.dir)) if f[f.rfind('_')+1:-4] == "English"]

    def save_text(self, doc):
        document = fitz.open(doc)
        no_pages = document.pageCount
        doc_texts = self.process_document(document, no_pages)
        for i, text in enumerate(doc_texts):
            file_name = '../txts' + doc[doc.rfind('/'):-4] + '_Paragraph{}'.format(i) + '.txt'
            with open(file_name, 'w') as out_file:
                out_file.write(text)


    def save_all(self):
        for doc in tqdm(self.docs):
            self.save_text(doc)

    def process_text(self, text):
        text = text.strip() # remove trailing spaces
        text = re.sub(r'<image:(.*)>', '', text)  # remove images
        text = re.sub(r'\n', '', text) # remove new line
        text = re.sub(' +', ' ', text).strip() # remove multiple spaces
        text = re.sub(r'[^a-zA-Z0-9 ,.;()\'"]', '', text) # remove anything that is not alphanumeric or punctuation

        return text

    def process_page(self, document, page_no):
        page = document.loadPage(page_no)
        page_text = page.getText("blocks")
        texts = [x for _, _, _, _, x, _, _ in page_text]
        texts = [self.process_text(text) for text in texts]
        texts = [text for text in texts if text != '' and len(text) >= 50]

        return texts

    def process_document(self, document, no_pages):
        texts = []
        for i in range(no_pages):
            texts.extend(self.process_page(document, i))

        return texts

if __name__ == "__main__":
    pdf_parser = PDFParser("../../national-climate-plans/pdfs")
    pdf_parser.save_all()
