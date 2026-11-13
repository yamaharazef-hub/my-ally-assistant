from plugin import plugin
import os
import pdfkit
import markdown
from colorama import Fore
from urllib.parse import urljoin

@plugin('markdown to pdf')
class MarkdownToPDF:
    """
    A tool to convert Markdown files to PDF with images. Allows conversion from anywhere as long as an absolute path is provided
    Usage: 'markdown to pdf'
    """

    def __call__(self, ally, s):
        self.md_to_pdf(ally)

    def md_to_pdf(self, ally):
        ally.say('')
        ally.say('This option will help you convert Markdown files to PDF')
        while True:
            md_file = ally.input('Enter the full path of the Markdown file (or type "quit" to exit): ').strip()
            if md_file.lower() in ['q', 'quit', 'exit']:
                ally.say("Goodbye!", Fore.CYAN)
                break

            if not os.path.isfile(md_file):
                ally.say('The file does not exist. Please try again.', Fore.RED)
                continue

            if not md_file.lower().endswith('.md'):
                ally.say('The file must be a Markdown (.md) file.', Fore.RED)
                continue

            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    md_content = f.read()

                # Convert Markdown to HTML 
                html_content = markdown.markdown(md_content, extensions=['fenced_code', 'tables', 'toc'])

                # Process HTML to convert relative image paths to absolute paths
                html_content = self.convert_image_paths(html_content, os.path.dirname(os.path.abspath(md_file)))

                pdf_file = os.path.splitext(md_file)[0] + '.pdf'
                
                options = {
                    'enable-local-file-access': None,
                }
                config = pdfkit.configuration()

                # Convert HTML to PDF 
                pdfkit.from_string(html_content, pdf_file, options=options, configuration=config)

                ally.say(f"Converted '{md_file}' to '{pdf_file}'.", Fore.GREEN)
            except Exception as e:
                ally.say(f"An error occurred: {e}", Fore.RED)
            break

    def convert_image_paths(self, html_content, base_path):
        """
        Converts relative image paths in HTML to absolute paths.
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')
        images = soup.find_all('img')
        for img in images:
            src = img.get('src', '')
            if not src.startswith(('http://', 'https://', 'data:')):
                abs_path = os.path.abspath(os.path.join(base_path, src))
                img['src'] = urljoin('file:', abs_path)
        return str(soup)