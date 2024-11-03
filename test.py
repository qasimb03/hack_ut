# %% [markdown]
# # Helpful links:
# Database connection:
# https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=BPYNAT_pyapi
# 
# SQL:
# https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=RSQL_createtable
# 
# Data Types:
# https://docs.intersystems.com/irislatest/csp/docbook/DocBook.UI.Page.cls?KEY=RSQL_datatype

# %% [markdown]
# # Loading the data to a dataframe
# This tutorial covers how to use IRIS as a vector database. 
# 
# For this tutorial, we will use a dataset of 2.2k online reviews of scotch (
# dataset from https://www.kaggle.com/datasets/koki25ando/22000-scotch-whisky-reviews) . With our latest vector database functionality, we can leverage the latest embedding models to run semantic search on the online reviews of scotch whiskeys. In addition, we'll be able to apply filters on columns with structured data. For example, we will be able to search for whiskeys that are priced under $100, and are 'earthy, smooth, and easy to drink'. Let's find our perfect whiskey!

# %%
# Import statements
import pandas as pd
import iris
import time
import json
import os
from sentence_transformers import SentenceTransformer



#def main():
# Load the CSV file
diseases_symptoms_df = pd.read_csv('data/Diseases_Symptoms.csv')

# View the data
diseases_symptoms_df.head()

# View cleaned data
diseases_symptoms_df.head()


# Database connection
username = 'demo'
password = 'demo'
hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
port = '1972' 
namespace = 'USER'
CONNECTION_STRING = f"{hostname}:{port}/{namespace}"

# Note: Ideally conn and cursor should be used with context manager or with try-execpt-finally 
conn = iris.connect(CONNECTION_STRING, username, password)
cursor = conn.cursor()

# Load a pre-trained sentence transformer model. This model's output vectors are of size 384
model = SentenceTransformer('all-MiniLM-L6-v2')

# Generate embeddings for all descriptions at once. Batch processing makes it faster
embeddings = model.encode(diseases_symptoms_df['Symptoms'].tolist(), normalize_embeddings=True)

# Add the embeddings to the DataFrame
diseases_symptoms_df['Symptoms_Vector'] = embeddings.tolist()

count_nausea = diseases_symptoms_df['Symptoms'].str.contains('nausea', case=False, na=False).sum()
print(f"Number of rows with 'nausea': {count_nausea}")


tableName = "HackUT.testTable"
try:
    cursor.execute(f"DROP TABLE {tableName}")  
except:
    pass

tableName = "HackUT.testTable"
tableDefinition = "(code INT, name VARCHAR(255), symptoms LONGTEXT, treatments LONGTEXT, symptoms_vector VECTOR(DOUBLE, 384))"
cursor.execute(f"CREATE TABLE {tableName} {tableDefinition}")

##looping through dataframe and adding all the data to IRIS table
sql = f"Insert into {tableName} (code, name, symptoms, treatments, symptoms_vector) values (?,?,?,?, TO_VECTOR(?))"
start_time = time.time()
for index,row in diseases_symptoms_df.iterrows():
    data = (row['Code'], row['Name'], row['Symptoms'], row['Treatments'], str(row['Symptoms_Vector']))
    cursor.execute(sql, data)
end_time = time.time()
print(f"time taken to add {len(diseases_symptoms_df)} entries: {end_time-start_time} seconds")


# This is our search phrase


def prompt(searchPhrase):
    # searchPhrase = input("Enter your symptoms or E to exit: ")

    # Convert search phrase into a vector
    searchVector = model.encode(searchPhrase, normalize_embeddings=True).tolist() 

    # Define the SQL query with placeholders for the vector and limit
    sql = f"""
        SELECT TOP ? name
        FROM {tableName}
        ORDER BY VECTOR_DOT_PRODUCT(symptoms_vector, TO_VECTOR(?)) DESC
    """

    numberOfResults = 5

    # Execute the query with the number of results and search vector as parameters
    cursor.execute(sql, [numberOfResults, str(searchVector)])

    # Fetch all results
    results = cursor.fetchall()
    formatted_results = {f"Disease {i + 1}": result[0] for i, result in enumerate(results)}
        
    print(formatted_results)
    return formatted_results  # Returning as a dictionary


if __name__ == '__main__':
    prompt()

    