import pandas as pd


file_path = './Diseases_Symptoms.csv' 
df = pd.read_csv(file_path)


df['Treatments'].fillna("Unknown", inplace=True)

df.columns = df.columns.str.lower().str.replace(' ', '_')

df = df.drop_duplicates()

cleaned_file_path = 'Cleaned_Diseases_Symptoms.csv'
df.to_csv(cleaned_file_path, index=False)


print("Dataset cleaned and saved as:", cleaned_file_path)