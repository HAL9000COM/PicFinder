# %%
import sqlite3
import sqlite_spellfix


# Connect to the database (creates a new database if it doesn't exist)
conn = sqlite3.connect("example.db")
conn.enable_load_extension(True)
conn.load_extension(sqlite_spellfix.extension_path())  # type:ignore

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Create a table if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        language TEXT,
        text TEXT
    )
"""
)

# Insert data into the table
cursor.executemany(
    "INSERT INTO notes (language, text) VALUES (?, ?)",
    [
        ("English", "Wikipedia the free encyclopedia"),
        ("Spanish", "Wikipedia la enciclopedia libre"),
        ("French", "Wikipédia l'encyclopédie libre"),
        ("German", "Wikipedia die freie Enzyklopädie"),
        ("Chinese (Simplified)", "维基百科，自由的百科全书"),
        ("Chinese (Traditional)", "維基百科，自由的百科全書"),
        ("Japanese", "ウィキペディア、自由な百科事典"),
        ("Arabic", "ويكيبيديا الموسوعة الحرة"),
        ("Russian", "Википедия свободная энциклопедия"),
        ("Hindi", "विकिपीडिया, एक मुक्त विज्ञानकोश"),
    ],
)

# Commit the changes to the database
conn.commit()


# %%
# Retrieve data from the table
def init_search(cursor):
    # Create a virtual table for full-text search
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS search_index USING fts5(content);
    """
    )

    # Populate the search index with data from the users table
    cursor.execute(
        """
        INSERT INTO search_index(content) SELECT text FROM notes;
    """
    )

    # Enable the spellfix1 extension
    cursor.execute(
        """
        CREATE VIRTUAL TABLE IF NOT EXISTS spellfix USING spellfix1;
    """
    )
    # add vocabulary to spellfix from search_index
    cursor.execute(
        """
        INSERT INTO spellfix(word) SELECT content FROM search_index;
    """
    )


init_search(cursor)
# Perform a spell correction query
# %%
cursor.execute(
    """
    SELECT word FROM spellfix WHERE word MATCH ?;
""",
    ("百科",),
)

# Retrieve the corrected word
corrected_word = cursor.fetchone()[0]

# Perform a full-text search query
cursor.execute(
    """
    SELECT * FROM notes WHERE id IN (
        SELECT rowid FROM search_index WHERE content MATCH ?
    );
""",
    (corrected_word,),
)

# Retrieve the search results
search_results = cursor.fetchall()

# Print the search results
for result in search_results:
    print(result)

# Close the cursor and the connection
cursor.close()
conn.close()
# %%
