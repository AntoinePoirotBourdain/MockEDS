import pandas as pd 
from pathlib import Path


def generate_concept_map(concept_list):

    print(concept_list)

    concept_map_total = pd.read_csv(Path("concept_map/" + concept_list[0] + ".csv"))

    print(concept_map_total.shape)

    for concept in concept_list[1:]:
        print(concept)
        concept_map = pd.read_csv(Path("concept_map/" + concept + ".csv"))
        print(concept_map_total.shape)


        concept_map_total = pd.concat([concept_map_total, concept_map], ignore_index=True)

        print(concept_map_total.shape)


    concept_map_total.to_csv(Path("concept_map/concept_map_total.csv"), index=False)

    return concept_map_total


concept_list = ["diagnoses","drug","drug_2","drug_3","gender","measurements","measurements_2","procedures_icd","procedures_2"]

concept_map_total = generate_concept_map(concept_list)

print(concept_map_total.shape)
