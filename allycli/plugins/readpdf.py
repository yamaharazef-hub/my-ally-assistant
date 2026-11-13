# importing the modules
import PyPDF2
import pyttsx3
from plugin import plugin

"""
A tool for reading out the pdf files using the ally.Uses PyPDF2 and pyttsx3 libraries
"""


@plugin('readpdf')
class readpdfally():

    def __init__(self):
        self.path = None

    def __call__(self, ally, s):
        self.read_pdf(ally)

    def read_pdf(self, ally):
        filename = ally.input("Enter your file path with '/' separations:")
        pdf = open(filename, 'rb')
        pdfRead = PyPDF2.PdfFileReader(pdf)
        for i in range(pdfRead.getNumPages()):
            page = pdfRead.getPage(i)
            ally.say("Page No: " + str(1 + pdfRead.getPageNumber(page)))
            pageContent = page.extractText()
            ally.say(pageContent)
        speak = pyttsx3.init()
        speak.say(pageContent)
        speak.runAndWait()
