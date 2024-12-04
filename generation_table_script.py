import pandas as pd
from pathlib import Path
from generation_table_functions import generate_table



generate_table("persons")


table_name_list = [
    "persons"
    ]


print("Generating tables...")

if not Path("OMOP_data").exists():
    Path("OMOP_data").mkdir()


for table_name in table_name_list:
    table_df = generate_table(table_name)
    print(f"Table {table_name} generated successfully!")
    table_df.to_csv(f"OMOP_data/{table_name}.csv", index=False)
    




