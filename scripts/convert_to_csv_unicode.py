import pandas as pd
import re
import json

file_path = "../raw_data/32.Jonah.par"

with open('annotation_equivalences_hebrew.json', 'r') as file:
    # Parse the JSON data into a dictionary
    annotation_equivalences_hebrew = json.load(file)
    
with open('annotation_equivalences_greek.json', 'r') as file:
    # Parse the JSON data into a dictionary
    annotation_equivalences_greek = json.load(file)

def convert_to_dataframe(file_path):
    """
    This function converts the raw .par files into Pandas DataFrames
    """

    # Open the file for reading
    with open(file_path, "r") as file:
        # Read the contents of the file into a string variable
        parallel_raw = file.read()

    # Splits the text into verses or 'paragraphs' (separated in the raw files by empty lines)
    paragraphs = re.split(r"\n\s*\n", parallel_raw.strip())

    # Below code converts the raw text into a Pandas DataFrame
    parallels_dataframe_list = []
    # Loop through the list of paragraphs and extract the first line of each paragraph
    for paragraph in paragraphs:
        # Split the paragraph by newline characters
        lines = paragraph.split("\n")
        if lines:
            first_line = lines[0]
            other_lines = lines[1:]  # Get the lines other than the first line

        parallel = pd.DataFrame(other_lines, columns=["words"])
        parallel["coords"] = first_line
        parallels_dataframe_list.append(parallel)

    parallel = pd.concat(parallels_dataframe_list)

    # Splitting the text so that we have the Masoretic and the LXX columns
    parallel[["masoretic", "lxx"]] = parallel["words"].str.split("\t", expand=True)
    parallel = parallel.drop(columns=["words"])

    # Adding the order by column
    parallel = parallel.reset_index()
    parallel = parallel.drop(columns=["index"])
    parallel = parallel.reset_index()
    parallel = parallel.rename(columns={"index": "orderby"})
    parallel["orderby"] = parallel["orderby"] + 1

    # Splitting the coordinates
    parallel[["book", "chapter_verse"]] = parallel["coords"].str.split(" ", expand=True)
    parallel = parallel.drop(columns=["coords"])

    parallel[["chapter", "verse"]] = parallel["chapter_verse"].str.split(
        ":", expand=True
    )
    parallel = parallel.drop(columns=["chapter_verse"])

    # Splitting the masoretic text
    parallel[["masoretic", "retroverted"]] = parallel["masoretic"].str.split("=", n=1, expand=True) # We add n=1 because there may be several = in the line. We split only with the first
    
    # Reordering the columns
    parallel = parallel[["book", "chapter", "verse", "orderby", "masoretic", "retroverted", "lxx"]]
    
    # Replacing nulls with empty strings
    parallel = parallel.fillna('')

    return parallel

parallel = convert_to_dataframe(file_path)

def protect_annotations(parallel):

    
    def enclose_annotation_word_hebrew(word):
        if word in annotation_equivalences_hebrew.keys():
            return "<" + word + ">"
        else:
            return word
    
    def enclose_annotation_word_greek(word):
        if word in annotation_equivalences_greek.keys():
            return "<" + word + ">"
        else:
            return word
    
    for column in ['masoretic', 'retroverted']:
        parallel[column] = parallel[column].apply(lambda x: ' '.join([enclose_annotation_word_hebrew(word) for word in x.split()]))
    
    return parallel


def convert_hebrew_to_unicode(parallel):
    # Open the JSON file for reading
    with open('hebrew_equivalences.json', 'r') as file:
        # Parse the JSON data into a dictionary
        hebrew_equivalences = json.load(file)    
    
    # Dictionary of non-final Hebrew letters and their final equivalents
    hebrew_final_equivalences = {
        'כ': 'ך',  # Kaf to final Kaf
        'מ': 'ם',  # Mem to final Mem
        'נ': 'ן',  # Nun to final Nun
        'פ': 'ף',  # Pe to final Pe
        'צ': 'ץ',  # Tsadi to final Tsadi
    }

    # Function to replace non-final Hebrew letters with their final equivalents
    def replace_final_in_word(word):
        word = word.replace(u'\u200e', '')
        if word[-1] in hebrew_final_equivalences:
            word = word[:-1] + hebrew_final_equivalences[word[-1]]
        return word

    # Replacing nulls with empty strings
    parallel = parallel.fillna('')

    # Function to replace with Unicode characters, except annotations
    def replace_with_unicode_except_annotations(text):
        words = text.split()
        
        words_list = []
        for word in words:
            if word.startswith('<') and word.endswith('>'):
                words_list.append(word)
            else:
                word_result = []
                for character in word:
                    word_result.append(hebrew_equivalences.get(character, character))
                words_list.append(''.join(word_result))
        return ' '.join(words_list)
        
    
    
    # Removing the / character and replacing with the Unicode letters
    for column in ['masoretic', 'retroverted']:
        parallel[column] = parallel[column].str.replace('/','')
        parallel[column] = parallel[column].apply(replace_with_unicode_except_annotations)
        parallel[column] = parallel[column].apply(lambda x: ' '.join([replace_final_in_word(word) for word in x.split()]))
   
    
    
    return parallel



def convert_greek_to_unicode(parallel):
    # Open the JSON file for reading
    with open('greek_equivalences.json', 'r') as file:
        # Parse the JSON data into a dictionary
        greek_equivalences = json.load(file)
    
    # Removing diacritics
    diacritics = [')', '(', '|', '/', '\\', '=', '+', '*']
    
    for diacritic in diacritics:
        parallel['lxx'] = parallel['lxx'].str.replace(diacritic,'')
    
    # Replacing the original value for koppa (#3) with a single letter, Ñ
    # This makes it easier to replace with the Greek Unicode
    parallel['lxx'] = parallel['lxx'].str.replace('#3','Ñ')
        
    # Replacing code with Unicode    
    parallel['lxx'] = parallel['lxx'].apply(lambda x: ''.join(greek_equivalences.get(c, c) for c in x))
    
    # Function to replace non-final sigma with its final equivalent
    def replace_final_sigma(word):
        if word[-1] == 'σ':
            word = word[:-1] + 'ς'
        return word
    
    parallel['lxx'] = parallel['lxx'].apply(lambda x: ' '.join([replace_final_sigma(word) for word in x.split()]))
    
    return parallel


def replace_annotations(parallel):
    def replace_these_annotations(text):
        words = text.split()
        
        words_list = []
        for word in words:
            if word.startswith('<') and word.endswith('>'):
                print(word)
                return annotation_equivalences_hebrew[word.replace('<','').replace('>','')]
            else:
                return word
    
    for column in ['masoretic', 'retroverted']:
        parallel[column] = parallel[column].apply(replace_these_annotations)
    
    return parallel


parallel = protect_annotations(parallel)
parallel = convert_hebrew_to_unicode(parallel)
parallel = convert_greek_to_unicode(parallel)
parallel = replace_annotations(parallel)
parallel.to_csv('test.csv', index=False)
print(parallel)

#for i in parallel['masoretic_unicode']:
#    print(i)
#ben = pd.DataFrame(parallel['masoretic_unicode'].str.split(expand=True)).iloc[676,1]
#for char in ben.replace(u'\u200e', ''):
#    print(char)
