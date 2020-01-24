
from FileManager import *
import time

# Global Variables
directory = None
output_file = None
file_manager = None

if __name__ == "__main__":
    again = 'y'
    while again == 'y':
        os.system("cls")
        header()
        get_directory()
        get_ouput_filename()
        file_manager = FileManager(directory,output_file)


################################################################################
# Functions
################################################################################
def header():
    print("""
     ****************************************************************
     *                  Welcome to PDF Creeper                      *
     * This application will scan a specific directory using the    *
     * absolute path. It can also scan just a file after a path has *
     * been specified.                                              *
     *                                                              *
     *                       -- IMPORTANT --                        *
     *      This program will delete any .png files within the      *
     *    path directory. Ensure no .png files exist in directory   *
     ****************************************************************
    """)

def get_directory():
    file_manager = FileManager()
    
    directory = input("Enter Directory to Scan for PDF files: ")
    
    if directory is None or directory == "" or os.path.isdir(directory) is False:
        directory = "C:\\Users\\jayde\\Documents\\Programs\\Python\\WaterQuality\\PDF Extractor\\PDF Extractor\\Tests"
    else:
        directory.replace("\\","\\\\")

def get_ouput_filename():
    print("Existing Excel Files: ")
    [print(index + ". " + f) for index,f in enumerate(os.listdir(os.getcwd())) if f.endswith(".csv")]
    file = input("Input an output filename: ")

    if directory.isfile(file):       
        if file.endswith(".csv"):
            output_file = file
        else:
            output_file = file + str(".csv")
    elif file == None or file == "":
        output_file = "consolidated_file.csv"
    else:
        if file.endswith(".csv"):
            output_file = file
        else:
            output_file = file + str(".csv")