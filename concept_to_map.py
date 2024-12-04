import pandas as pd 
from pathlib import Path


def source_concepts_generation(concept_target,source_table_name, concept_source_code, concept_source_name,reference_table_name=None ):

    source_table = pd.read_csv(Path("MIMIC_data/" + source_table_name + ".csv"))
    

    if reference_table_name:
        reference_table = pd.read_csv(Path("MIMIC_data/" + reference_table_name + ".csv"))
        source_table = pd.merge(source_table, reference_table, on=concept_source_code, how="left")
        #source_table = source_table.rename(columns={"concept_id":concept_source_name})


    concept_table_for_usagi = source_table[[concept_source_code,concept_source_name]].groupby([concept_source_code,concept_source_name])
    concept_table_for_usagi = concept_table_for_usagi.size().reset_index(name='frequency')

    concept_table_for_usagi = concept_table_for_usagi.rename(columns={concept_source_code:"concept_code",concept_source_name:"concept_name"})
    concept_table_for_usagi.to_csv(Path("concepts_to_map/" + concept_target + ".csv"), index=False)



    return concept_table_for_usagi


source_concepts_generation("diagnoses","DIAGNOSES_ICD","icd9_code","long_title", "D_ICD_DIAGNOSES")

