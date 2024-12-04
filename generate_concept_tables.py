import pandas as pd
from pathlib import Path



# Concept table 

concept_list = [
    "gender",
]

default_mapping_table = pd.read_csv(Path("mappings/default.csv"))

for concept in default_mapping_table["concept_target"].unique():
    concept_list.append(concept)


domain_list = 


print(concept_list)

# Domain table







