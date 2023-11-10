import pandas as pd


def convert_file_to_quarto(file_path, book_name):
    print("Converting this book to Quarto", book_name)
    df = pd.read_csv(file_path)

    book_text = f"""# {book_name}\n\n"""

    grouped_by_chapter = df.groupby("chapter")

    for group_ch in grouped_by_chapter:
        chapter = group_ch[0]
        book_text = book_text + "## Chapter " + str(chapter) + "\n\n"

        grouped_by_verse = group_ch[1].groupby("verse")
        for group_vr in grouped_by_verse:
            verse = group_vr[0]
            book_text = book_text + "### Verse " + str(verse) + "\n\n"
            verse_dataframe = group_vr[1][["masoretic", "retroverted", "lxx"]]

            verse_dataframe.columns = [
                "Masoretic text (BHS)",
                "Tov's retroversion",
                "Rahlf's Septuagint",
            ]

            # Removing Tov's retroversion if no retroversion is present
            if verse_dataframe["Tov's retroversion"].isnull().all():
                verse_dataframe = verse_dataframe.drop(columns=["Tov's retroversion"])
                table_column_widths = '"[50,50]"'
            else:
                verse_dataframe["Tov's retroversion"] = verse_dataframe[
                    "Tov's retroversion"
                ].fillna("")
                table_column_widths = '"[35,30,35]"'

            verse_markdown = verse_dataframe.to_markdown(index=False)
            book_text = (
                book_text
                + verse_markdown
                + "\n: "
                + book_name
                + " chapter "
                + str(chapter)
                + ", verse "
                + str(verse)
                + " { .hover tbl-colwidths="
                + table_column_widths
                + "}\n\n"
            )

    with open("../collations/" + book_name + ".qmd", "w") as file:
        file.write(book_text)


book_names = [
    'Genesis',
    'Exodus',
    'Leviticus',
    'Numbers',
    'Deuteronomy',
    'Joshua (Vaticanus)',
    'Joshua (Alexandrinus)',
    'Judges (Vaticanus)',
    'Judges (Alexandrinus)',
    'Ruth',
    '1 Samuel',
    '2 Samuel',
    '1 Kings',
    '2 Kings',
    '1 Chronicles',
    '2 Chronicles',
    'Esther',
    'Ezra',
    'Nehemiah',
    'Psalms',
    'Proverbs',
    'Ecclesiastes',
    'Song of Songs',
    'Job',
    'Hosea',
    'Micah',
    'Amos',
    'Joel',
    'Jonah',
    'Obadiah',
    'Nahum',
    'Habakkuk',
    'Zephaniah',
    'Haggai',
    'Zechariah',
    'Malachi',
    'Isaiah',
    'Jeremiah',
    'Lamentations',
    'Ezekiel',
    'Daniel (Old Greek)',
    'Daniel (Theodotion)',   
]

for book in book_names:
    print("###################################################################################################################################################")
    convert_file_to_quarto("../csvs/" + book + ".csv", book)
