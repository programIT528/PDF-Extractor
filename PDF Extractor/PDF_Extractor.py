
from FileManager import *
from Extractor import *
import time

# Global Variables
directory = None
output_file = None
file_manager = FileManager()

################################################################################
# Functions
################################################################################
def header():
    print("""
     ****************************************************************
     *                  Welcome to PDF Extractor                    *
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
    directory = input("Enter Directory to Scan for PDF files: ")
    
    if directory is None or directory == "" or os.path.isdir(directory) is False:
        directory = "C:\\Users\\jayde\\Documents\\Programs\\Python\\WaterQuality\\PDF Extractor\\PDF Extractor\\Tests"
    else:
        directory.replace("\\","\\\\")

    file_manager.set_directory(directory)

    for index, file in enumerate(file_manager.get_list_of_pdfs()):
        print(str(index + 1) + ". " + file)

def get_ouput_filename():
    file = input("Input an output filename: ")

    if os.path.isfile(file):       
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

    file_manager.set_output_file(output_file)

################################################################################
# Main
################################################################################
if __name__ == "__main__":
    again = 'y'
    while again == 'y':
        os.system("cls")
        header()
        get_directory()
        get_ouput_filename()

        print("Start scan of directory")
        start = time.time()

        for pdf_file in file_manager.get_list_of_pdfs():
            extractor = Extractor(file_manager, pdf_file)
            extractor.extract()

        for file in filter(lambda f: f.endswith(".png"), os.listdir(os.getcwd())):
            os.remove(file)

        os.system("start " + file_manager.get_output_file())
        print("\n\n\nFinished scanning directory.")
        print("Completed in: " + str(round((time.time() - start) / 60, 2)) + " minutes\n")
        again = input("Do you have another directory (y or n): ")
