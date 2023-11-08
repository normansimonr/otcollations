import pandas as pd
import re
import json

file_path = "../raw_data/32.Jonah.par"


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
    parallel['retroverted'] = parallel['retroverted'].fillna('')
    
    # Reordering the columns
    parallel = parallel[["book", "chapter", "verse", "orderby", "masoretic", "retroverted", "lxx"]]

    return parallel

parallel = convert_to_dataframe(file_path)

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

    
    # Removing the / character and replacing with the Unicode letters
    for column in ['masoretic', 'retroverted']:
        parallel[column] = parallel[column].str.replace('/','')
        parallel[column] = parallel[column].apply(lambda x: ''.join(hebrew_equivalences.get(c, c) for c in x))
        parallel[column] = parallel[column].apply(lambda x: ' '.join([replace_final_in_word(word) for word in x.split()]))
   
    return parallel

parallel = convert_hebrew_to_unicode(parallel)
parallel.to_csv('test.csv', index=False)
print(parallel)

#for i in parallel['masoretic_unicode']:
#    print(i)
#ben = pd.DataFrame(parallel['masoretic_unicode'].str.split(expand=True)).iloc[676,1]
#for char in ben.replace(u'\u200e', ''):
#    print(char)
