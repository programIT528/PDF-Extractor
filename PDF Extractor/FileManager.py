# Programmer: Jayden P
# Program: PDF Extractor
# Description: Navigates throught pdf files scanned in a directory
#   and converts each page to a jpeg image. Then it reads the jpeg
#   jpeg file using OCR (Optical Character Recognition) to determine
#   best fit characters.
# File: FileManager.py

import os
import csv
import pandas as pd


class FileManager(object):
    """Manages files and directory locations for local systems"""
    def __init__(self, directory = os.getcwd(), output_file = "consolidated_file.csv"):
        self.__directory__ = directory
        self.__output_file__ = output_file
        self.__list_of_pdfs__ = ()
        self.initialize_outputfile()
        

    ################################################################################
    # Methods
    ################################################################################
    def __initialize_pdf_list__(self):
        """Initialize the list of pdf files found in directory"""
        if os.getcwd() != self.__directory__ and os.path.isdir(self.__directory__):
            os.chdir(self.__directory__)

        self.__list_of_pdfs__ = tuple(filter(lambda file: file.endswith(".pdf"), os.listdir(os.getcwd())))

    def initialize_outputfile(self):
        try:
            if os.path.exists(self.__output_file__):
                os.remove(self.__output_file__)
        except IOError as io:
            print("Error with " + self.__output_file__ + "\n" + str(io))
        except Exception as e:
            print(str(e))

    def write_df_to_csv(self, dictionary, file):
        try:
            dictionary.to_csv(self.__output_file__, mode="a+", header=True)
            print("Writing Data to " + self.__output_file__)
        except IOError as io:
            print("Error in method dict_to_csv_file: " + str(io))
        except Exception as e:
            print("Error has occured in dict_to_csv_file: " + str(e))

    ################################################################################
    # Setters and Getters
    ################################################################################
    def set_directory(self, directory):
        """ Moves the os path to the param: directory """
        if os.path.isdir(directory) and directory != None:
            self.__directory__ = directory
            self.__initialize_pdf_list__()
        self.initialize_outputfile()

    def get_directory(self):
        """ Gets the current working directory """
        return self.__directory__

    def set_output_file(self, filename):
        """ Automatically checks and determines if file exists
                Formats file to specific requirements (adds .csv to end of file)

            If File doesn't exist, create a blank file with param: filename)"""
        if self.__directory__.isfile(filename):
            if filename.endswith(".csv"):
                self.__output_file__ = filename
            else:
                self.__output_file__ = filename + str(".csv")
        else:
            f = open(filename, "w+")
            f.close()
            self.__output_file__ = f.name()

    def get_output_file(self):
        """ Returns the output filename for converted pdf files """
        return self.__output_file__

    def get_list_of_pdfs(self):
        """ Returns the list of pdf files in directory """
        return self.__list_of_pdfs__