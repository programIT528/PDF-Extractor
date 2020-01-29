# Programmer: Jayden P
# Program: PDF Extractor
# Description: Navigates throught pdf files scanned in a directory
#   and converts each page to a jpeg image. Then it reads the jpeg
#   jpeg file using OCR (Optical Character Recognition) to determine
#   best fit characters.
# File: PDFManager.py

import pytesseract
import cv2
import pdf2image
import PIL
import os
import numpy
import pandas as pd
import re
import tabula
from tabula import read_pdf
import subprocess
import camelot

class Extractor(object):
    """ Manages PDF File Conversions """
    protocol = ""

    def __init__(self, file_manager, pdf_file):
        self.__file_manager__ = file_manager
        self.__pdf_file__ = pdf_file
        self.__pdf_image_file__ = None
        self.__text__ = None
        self.pages = None
        self.page_index = 1
        self.found_data = {"file" : "", "data" : "", "lab" : "", "protocol" : self.protocol, "analyte" : "", "method" : "", "holding" : "", "turnAroundTime" : "", "cost" : ""}

        self.pdf_description()

    ################################################################################
    # Methods
    ################################################################################
    def pdf_description(self):
        try:
            self.pages = pdf2image.convert_from_path(pdf_path=self.__pdf_file__, dpi=300,jpegopt='quality')
        except Exception as e:
            print(str(e))
    
    def update_current_file(self):
        self.filename = self.__file_manager__.get_directory() + "\\" + self.__pdf_file__.replace(".pdf","") + "_page_" + str(self.page_index) + ".jpg"
        self.__pdf_image_file__ = self.filename

    def __OCR_file_reader__(self):
        print("Rescanning PDF File: " + self.__pdf_file__)
        page = self.pages[self.page_index]
        page.save(self.filename, 'JPEG')
        
        self.__OCR_extract__()

        if os.path.isfile(self.filename):
            os.remove(self.filename)

    def get_protocol_for_pdf_file(self):        
        for number, page in enumerate(self.pages):
            if self.protocol is None or self.protocol == "":
                patternProgram = "(?<=Program. )\w+| (?<=ogram. )\w+"
                patternProtocol = "(?<=Protocol. )\w+|(?<=Pratocol. )\w+|(?<=Protoco!. )\w+"

                regProgram = re.compile(patternProgram)
                regProtocol = re.compile(patternProtocol)
                
                text = str(pytesseract.image_to_string(page, lang = "eng"))
                try:
                    if self.protocol == "":
                        if bool(regProgram.search(text)) and bool(regProtocol.search(text)):
                            self.protocol = regProgram.search(text).group(0) + "_" + regProtocol.search(text).group(0)
                    elif bool(regProtocol.search(text)):
                        self.protocol = regProtocol.search(text).group(0)
                    else: 
                        pass
                except Exception as e:
                    print("Determine protocols in format text function error: " + str(e))
            else:
                break

        return self.protocol

    def format_text(self, text):
        """ Using OCR and Regex\n
        Extract Data using pre-defined regex patterns"""

        #patternProgram = "(?<=Program. )\w+| (?<=ogram. )\w+"
        #patternProtocol = "(?<=Protocol. )\w+|(?<=Pratocol. )\w+|(?<=Protoco!. )\w+"
        patternCurrency = "([\£\$\€]{1}[,\d]+.?\d*)|included|Included"
        patternMethod = "(EPA[0-9., ]+)|(EPA[0-9\w.,]+)|(SM[0-9.,\-A-Za-z]+)|(SM [0-9.,\-\w]+)|(PA[0-9,. ]+)"
        patternLab = "(^Water Quality Lab|^HALL|^WQL|^HEAL|^SLD)"
        patternAnalyte = "^[A-Za-z\[\(\) \-\.\,]+ "
        patternHolding = "[0-9]+( months| month|week| week|weeks| weeks| day|day|days| days|hrs| hrs|hours| hours|hour| hours|/yr|/yrs| year| years)"

        regCurrency = re.compile(patternCurrency)
        regMethod = re.compile(patternMethod)
        regLab = re.compile(patternLab)
        regAnalyte = re.compile(patternAnalyte)
        regHolding = re.compile(patternHolding)
        #regProgram = re.compile(patternProgram)
        #regProtocol = re.compile(patternProtocol)
        regTurnAroundTime = re.compile(patternHolding)

        #try:
        #    if self.protocol == "":
        #        if bool(regProgram.search(text)) and bool(regProtocol.search(text)):
        #            self.protocol = regProgram.search(text).group(0) + "_" + regProtocol.search(text).group(0)
        #        elif bool(regProtocol.search(text)):
        #            self.protocol = regProtocol.search(text).group(0)
        #        else: 
        #            pass
        #except Exception as e:
        #    print("Determine protocols in format text function error: " + str(e))

        list_words = []
        for line in text.splitlines():
            
            line = line.replace("|","")
            line = line.replace("§","S")
            line = line.replace(","," ")
            line = line.replace("[","")
            line = line.replace("]","")
            #print(line)

            if not line.isspace() and line != "":
                try:
                    patterns = {"file" : "", "data" : "", "lab" : "", "protocol" : self.protocol, "analyte" : "", "method" : "", "holding" : "", "turnAroundTime" : "", "cost" : ""}
                    patterns["file"] = self.__pdf_file__
                    patterns["data"] = line
                                        
                    if bool(regLab.search(line)):
                        patterns["lab"] = regLab.search(line).group(0)

                    if bool(regAnalyte.search(line)):
                        patterns["analyte"] = regAnalyte.search(line).group(0)

                    if bool(regMethod.search(line)):
                        patterns["method"] = regMethod.search(line).group(0)

                    if bool(regHolding.search(line)):
                        patterns["holding"] = regHolding.search(line).group(0)

                    if bool(regCurrency.search(line)):
                        patterns["cost"] = regCurrency.search(line).group(0)

                except Exception as e:
                    print("Gather data in regex error: " + str(e))

                list_words.append(patterns)
                

        df = pd.DataFrame(list_words)
        self.__text__ = df    
        
        #print("Formatted Text Method: " + str(type(self.__text__)))

    def pre_process_image(self, img, save_in_file, morph_size=(8, 8)):
        """Reference:  https://stackoverflow.com/questions/50829874/how-to-find-table-like-structure-in-image"""
        # get rid of the color
        pre = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Otsu threshold
        pre = cv2.threshold(pre, 250, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
        # dilate the text to make it solid spot
        cpy = pre.copy()
        struct = cv2.getStructuringElement(cv2.MORPH_RECT, morph_size)
        cpy = cv2.dilate(~cpy, struct, anchor=(-1, -1), iterations=1)
        pre = ~cpy

        if save_in_file is not None:
            cv2.imwrite(save_in_file, pre)
        return pre
    
    def write_df_to_csv(self):
        self.__file_manager__.write_df_to_csv(self.__text__, self.__pdf_image_file__)
        
    ################################################################################
    # Extraction Methods
    ################################################################################
    def extract(self):
        for self.page_index in range(0, len(self.pages)):            
            try:
                self.__tabula_extract__()
                self.update_current_file()
                print("Tabula extracted " + self.__pdf_image_file__)
            except TabulaError as te:
                print(str(te.message))                           
                try:
                    self.update_current_file()
                    self.__OCR_file_reader__()
                    print("OCR extracted " + self.__pdf_image_file__)
                    self.write_df_to_csv()
                except Exception as e:
                    print("After OCR Error: " + str(e))                    
                    self.update_current_file()
            except Exception as e:
                    print("Extract Method Error: " + str(e))
                    self.update_current_file()

    def __tabula_extract__(self):
        try:
           # df = read_pdf(self.__pdf_file__, format="CSV", pandas_options={'header' : 0}, pages = self.page_index, multiple_tables=True)
            df = read_pdf(self.__pdf_file__, output_format="dataframe", java_options="-Xmx256m", pages = self.page_index + 1, pandas_options={"header": 0}, multiple_tables=True)
        except FileNotFoundError as f:
            print(str(f))
        except ValueError as v:
            print(str(v))
        except tabula.errors.CSVParseError as csv:
            print(str(csv))
        except tabula.errors.JavaNotFoundError as j:
            print(str(j))
        except subprocess.CalledProcessError as se:
            print(str(se))
        except Exception as e:
            print("Tabula Extraction Error: " + str(e))
            raise TabulaError
        

        # read_pdfs will return a list of dataframes
        #   select and index of the list to return the dataframe structure
        if df == None or df == []:
            raise TabulaError
        else:
            for index, table in enumerate(df):
                new_df = pd.DataFrame(table)
                if new_df.empty:
                    raise TabulaError
                else:
                    new_df["protocol"] = self.protocol
                    cols = new_df.columns.tolist()
                    cols.insert(0, cols.pop(cols.index("protocol")))
                    new_df = new_df.reindex(columns = cols)
                    self.__text__ = new_df
                    self.write_df_to_csv()
                    #print(self.__text__)

    def __camelot_extract__(self):
        try:
            df = camelot.read_pdf(self.__pdf_file__)
        except Exception as e:
            print(str(e))
            raise CamelotError

        if df.n == None or df.n == [] or df.n == 0:
            raise CamelotError
        else:
            for index, df in enumerate(df._tables):
                new_df = pd.DataFrame(df)
                if new_df.empty:
                    raise CamelotError
                else:
                    new_df["protocol"] = self.protocol
                    cols = new_df.columns.tolist()
                    cols.insert(0, cols.pop(cols.index("protocol")))
                    new_df = new_df.reindex(columns = cols)
                    self.__text__ = new_df
                    #print(self.__text__)

    def __OCR_extract__(self):
        """ Convert Image to String using OCR (Optical Character Recognition) with Tesseract """
        try:            
            #image_data = str(pytesseract.image_to_string(self.__pdf_image_file__, lang = "eng"))
            #self.format_text(image_data)
            df = pytesseract.image_to_data(self.__pdf_image_file__, lang="eng", nice=0, output_type="data.frame", pandas_config={'header': 0})
            df = df.dropna()
            df = df.sort_values(by=['level', 'word_num'], ascending=True)
            df = df.pivot_table("text", index = ["level", "page_num", "line_num", "block_num"], columns = 'word_num', aggfunc=lambda x: ' '.join(x))
            df = df.dropna(axis=0, how='all')
            #df = df.drop(columns=['level','page_num', 'block_num', 'par_num', 'line_num','word_num'])
            
            df["protocol"] = self.protocol
            cols = df.columns.tolist()
            cols.insert(0, cols.pop(cols.index("protocol")))
            df = df.reindex(columns = cols)
            #print(df)
            self.__text__ = df
        except IOError as io:
            print("Error in 'image_to_string' IOError: " + str(io))
        except Exception as e:
            print("Error in 'image_to_string' method: " + str(e))

class TabulaError(Exception):
    """ Tabula Error """
    def __init__(self):
        self.message = "Tabula cannot read an image file."

class CamelotError(Exception):
    """ Camelot Error """
    def __init__(self):
        self.message = "Camelot could not read the file."