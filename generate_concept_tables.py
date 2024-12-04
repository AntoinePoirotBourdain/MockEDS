import pandas as pd
from pathlib import Path



# Concept table 

concept_list = [
    "gender",
]

default_mapping_table = pd.read_csv(Path("mappings/default.csv"))

for concept in default_mapping_table["concept_target"].unique():
    concept_list.append(concept)


#domain_list = 


print(concept_list)




def generate_concept_table():

    concept_table = pd.DataFrame({
        "concept_id":concept_id_list,
        "concept_name":None,
        "domain_id":None,
        "vocabulary_id":None,
        "concept_class_id":None,
        "standard_concept":None,
        "concept_code":None,
        "valid_start_date":None,
        "valid_end_date":None,
        "invalid_reason":None
    })





# Domain table







