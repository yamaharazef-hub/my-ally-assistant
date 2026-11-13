import img2pdf
from PIL import Image
import os
from plugin import plugin
from colorama import Fore


@plugin('image to pdf')
class ImageToPDF:
    """
    A tool to converrt images to pdf file
    """

    def __init__(self):
        # Path of the folder or image to be converted
        self.path = None
        self.image = None

    def __call__(self, ally, s):
        self.imgtopdf(ally)

    def imgtopdf(self, ally):
        ally.say('')
        ally.say('This tool will help you convert image to pdf')
        while True:

            self.available_options(ally)
            user_input = ally.input('Your choice: ')
            user_input = user_input.lower()

            if user_input == 'q' or user_input == 'quit' or user_input == '3':
                ally.say("See you next time :D", Fore.CYAN)
                break

            # For single image to be converted to pdf
            elif user_input == '1':
                while True:
                    image_path = ally.input(
                        'Enter the full path of the image: ')
                    if os.path.exists(image_path) and (image_path.endswith('.jpg') or image_path.endswith('.png')):
                        break
                    else:
                        ally.say(
                            'Opps! Looks like you entered an invalid path. Kindly Re-enter', Fore.RED)
                pdf_bytes = self.single_image_to_pdf(ally, image_path)

            # For multiple images in a folder to be converted to pdf
            elif user_input == '2':
                while True:
                    folder_path = ally.input(
                        'Enter the full path of the folder: ')
                    if os.path.exists(folder_path):
                        break
                    else:
                        ally.say(
                            'Opps! Looks like you entered an invalid path. Kindly Re-enter', Fore.RED)
                pdf_bytes = self.folder_to_pdf(ally, folder_path)

            # For an incorrectly entered option
            else:
                ally.incorrect_option()
                continue

            destination = ally.get_saving_directory(self.path)
            # Naming and saving the pdf file
            file_name = ally.input('What would you like to name your pdf? ')
            pdf_destination = destination + '/' + file_name + '.pdf'
            print('Final Destination ' + pdf_destination)
            self.save_pdf(ally, pdf_bytes, pdf_destination)

    def available_options(self, ally):
        """
        Message displayed to prompt the user about converting
        images to pdf
        """
        ally.say('Select one of the following options:')
        ally.say('1: Convert a single image')
        ally.say('2: Convert all images of the folder')
        ally.say('3: Quit')

    def single_image_to_pdf(self, ally, image_path):
        """
        This function is used to convert a single image
        with a given path to a pdf file.
        """
        self.path = image_path
        self.image = Image.open(image_path)
        pdf_bytes = img2pdf.convert(self.image.filename)
        self.image.close()
        return pdf_bytes

    def folder_to_pdf(self, ally, folder_path):
        """
        This function is used to convert all the images
        in a given folder path to a single PDF file
        """
        self.path = folder_path
        source_images = []
        os.chdir(self.path)
        for image in os.listdir(os.getcwd()):
            if image.endswith('.jpg') or image.endswith('.png'):
                source_images.append(image)
        pdf_bytes = img2pdf.convert(source_images)
        return pdf_bytes

    def save_pdf(self, ally, pdf_bytes, destination):
        """
        Save the pdf to the thus supplied location
        or prompt the user to choose a new location
        """
        pdf_file = open(destination, 'wb')
        pdf_file.write(pdf_bytes)
        pdf_file.close()
        ally.say('Your pdf is created successfully', Fore.GREEN)
