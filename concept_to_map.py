import pandas as pd 
from pathlib import Path



def source_concepts_generation(concept_target,source_table_name, concept_source_code, concept_source_name,reference_table_name=None ):

    source_table = pd.read_csv(Path("MIMIC_data/" + source_table_name + ".csv"))

 

    if reference_table_name:
        reference_table = pd.read_csv(Path("MIMIC_data/" + reference_table_name + ".csv"))
        source_table = pd.merge(source_table, reference_table, on=concept_source_code, how="left")



    concept_table_for_usagi = source_table[[concept_source_code,concept_source_name]].groupby([concept_source_code,concept_source_name])
    concept_table_for_usagi = concept_table_for_usagi.size().reset_index(name='frequency')

    concept_table_for_usagi = concept_table_for_usagi.rename(columns={concept_source_code:"concept_code",concept_source_name:"concept_name"})
    concept_table_for_usagi.to_csv(Path("concepts_to_map/" + concept_target + ".csv"), index=False)



    return concept_table_for_usagi




#Conditions
source_concepts_generation(concept_target = "condition_concept",
                           source_table_name = "DIAGNOSES_ICD",
                           concept_source_code = "icd9_code",
                           concept_source_name = "long_title", 
                           reference_table_name = "D_ICD_DIAGNOSES")


# Procedures
source_concepts_generation(concept_target = "procedure_concept_icd",
                           source_table_name = "PROCEDURES_ICD",
                           concept_source_code = "icd9_code",
                           concept_source_name = "long_title", 
                           reference_table_name = "D_ICD_PROCEDURES")




read_table = pd.read_csv(Path("MIMIC_data/D_ITEMS.csv"))

# Drug
print("Generating drug concepts...")
source_concepts_generation(concept_target = "drug_concept",
                           source_table_name = "PRESCRIPTIONS",
                           concept_source_code = "ndc",
                           concept_source_name = "drug")

# Measurement
print("Generating measurement concepts...")
source_concepts_generation(concept_target = "measurement_concept",
                           source_table_name = "CHARTEVENTS",
                           concept_source_code = "itemid",
                           concept_source_name = "label", 
                           reference_table_name = "D_ITEMS")

print("Generating measurement concepts... 2")
source_concepts_generation(concept_target = "measurement_concept_2",
                           source_table_name = "LABEVENTS",
                           concept_source_code = "itemid",
                           concept_source_name = "label", 
                           reference_table_name = "D_LABITEMS")

print("Generating drug concepts... 2")
source_concepts_generation(concept_target = "drug_2",
                           source_table_name = "INPUTEVENTS_MV",
                           concept_source_code = "itemid",
                           concept_source_name = "label", 
                           reference_table_name = "D_ITEMS")

print("Generating drug concepts... 3")
source_concepts_generation(concept_target = "drug_3",
                           source_table_name = "INPUTEVENTS_CV",
                           concept_source_code = "itemid",
                           concept_source_name = "label", 
                           reference_table_name = "D_ITEMS")


print("Generating procedure concepts...2")
source_concepts_generation(concept_target = "procedure_2",
                           source_table_name = "PROCEDUREEVENTS_MV",
                           concept_source_code = "itemid",
                           concept_source_name = "label", 
                           reference_table_name = "D_ITEMS")








    