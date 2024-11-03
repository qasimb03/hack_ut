# Import statements
import pandas as pd
import iris
import time
import json
import os
from sentence_transformers import SentenceTransformer


db_cursor = None
model = None
table_name = None

def load_data():
    return pd.read_csv('data/Diseases_Symptoms.csv')

def connect_to_db():
    username = 'demo'
    password = 'demo'
    hostname = os.getenv('IRIS_HOSTNAME', 'localhost')
    port = '1972'
    namespace = 'USER'
    CONNECTION_STRING = f"{hostname}:{port}/{namespace}"

    # Note: Ideally conn and cursor should be used with context manager or with try-execpt-finally 
    conn = iris.connect(CONNECTION_STRING, username, password)
    cursor = conn.cursor()
    global db_cursor
    db_cursor = cursor

def create_table():
    global db_cursor
    tableName = "HackUT.testTable"
    tableDefinition = "(code INT, name VARCHAR(255), symptoms LONGTEXT, treatments LONGTEXT, symptoms_vector VECTOR(DOUBLE, 384))"
    try:
        db_cursor.execute(f"DROP TABLE {tableName}")  
    except:
        pass
    db_cursor.execute(f"CREATE TABLE {tableName} {tableDefinition}")
    global table_name
    table_name = tableName


def create_embeddings(dataframe):
    global model
    # Generate embeddings for all descriptions at once. Batch processing makes it faster
    embeddings = model.encode(dataframe['Symptoms'].tolist(), normalize_embeddings=True)
    dataframe['Symptoms_Vector'] = embeddings.tolist()

def add_dataframe_to_db(dataframe):
    global table_name
    global db_cursor
    ##looping through dataframe and adding all the data to IRIS table
    sql = f"Insert into {table_name} (code, name, symptoms, treatments, symptoms_vector) values (?,?,?,?, TO_VECTOR(?))"
    start_time = time.time()
    for index,row in dataframe.iterrows():
        data = (row['Code'], row['Name'], row['Symptoms'], row['Treatments'], str(row['Symptoms_Vector']))
        db_cursor.execute(sql, data)
    end_time = time.time()
    print(f"time taken to add {len(dataframe)} entries: {end_time-start_time} seconds")


def create_model(model_name = "all-MiniLM-L6-v2"):
    global model
    model = SentenceTransformer(model_name)
    

def prompt(search_phrase):
    global model
    # Convert search phrase into a vector
    search_vector = model.encode(search_phrase, normalize_embeddings=True).tolist() 
    results = handle_prompt(search_vector)
    return results

def handle_prompt(search_vector):
    global db_cursor
    global table_name
    # Define the SQL query with placeholders for the vector and limit
    sql = f"""
        SELECT TOP ? name
        FROM {table_name}
        ORDER BY VECTOR_DOT_PRODUCT(symptoms_vector, TO_VECTOR(?)) DESC
    """

    numberOfResults = 5

    # Execute the query with the number of results and search vector as parameters
    db_cursor.execute(sql, [numberOfResults, str(search_vector)])

    # Fetch all results
    results = db_cursor.fetchall()
    formatted_results = {f"Disease {i + 1}": result[0] for i, result in enumerate(results)}
        
    print(formatted_results)
    return formatted_results  # Returning as a dictionary

def initialize_app():
    dataframe = load_data()
    create_model()
    connect_to_db()
    create_table()
    create_embeddings(dataframe)
    add_dataframe_to_db(dataframe)
    

if __name__ == '__main__':
    initialize_app()
    prompt()

    