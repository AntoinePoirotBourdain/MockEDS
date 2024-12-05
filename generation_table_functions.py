import pandas as pd
from pathlib import Path
import numpy as np


# difference entre table de réfe
TABLE_GENERATORS = {
    "persons": lambda: generate_persons_table(),
   # "observation_Periods": lambda: generate_observation_period_table(),
    "death": lambda: generate_death_table(),
    "visit_occurence": lambda: generate_visit_occurence_table(),
    "condition_occurence": lambda: generate_condition_occurence_table(),
    "procedure_occurence": lambda: generate_procedure_occurence_table(),
   # "measurements: lambda": generate_measurement_table(),
    #"CDM_sources": lambda: generate_CDM_source_table(),
    #"locations": lambda: generate_Location_table(),
    #"vocabularys": lambda: generate_Vocabulary_table(),
    #"domains": lambda: generate_Domain_table(),
    #"cohorts": lambda: generate_Cohort_table(),
    #"cohort_definitions": lambda: generate_Cohort_definition_table(),
    # Add other table-specific generators here
}


########################### Specific table generation ###############################################################


# Person
def generate_persons_table():
    # Read all tables that are necessary to generate the table
    PATIENTS = read_table("PATIENTS")
    # apply the different mappings to the columns
    person_table = pd.DataFrame({
        "person_id" : PATIENTS["subject_id"],
        "gender_concept_id" : apply_mapping(PATIENTS["gender"], "gender"),
        "year_of_birth" : pd.to_datetime(PATIENTS["dob"]).dt.year,
        "race_concept_id" : default_mapping("race_concept_id", len(PATIENTS["subject_id"])),
        "ethnicity_concept_id" : default_mapping("ethnicity_concept_id", len(PATIENTS["subject_id"]))
    })

    return person_table

# Death
def generate_death_table():
    # Read all tables that are necessary to generate the table
    PATIENTS = read_table("PATIENTS")

    # death can be from 3 different sources 

    dod_hosp = PATIENTS["dod_hosp"]
    dod_ssn = PATIENTS["dod_ssn"]


    death_date = dod_hosp.fillna(dod_ssn)
    death_date = death_date.where(~death_date.isna(), None)

    ehr_death__type_concept_id = dod_hosp.apply(lambda x: 32817 if pd.notnull(x) else None)
    ssn_death_type_concept_id = dod_ssn.apply(lambda x: 32885 if pd.notnull(x) else None)

    death_type_conept_id = ehr_death__type_concept_id.fillna(ssn_death_type_concept_id)


    # apply the different mappings to the columns
    death_table = pd.DataFrame({
        "person_id" : PATIENTS["subject_id"],
        "death_date": death_date,
    })
    return death_table


# Visit_occurence
def generate_visit_occurence_table():
    # Read all tables that are necessary to generate the table
    ADMISSIONS = read_table("ADMISSIONS")

    # apply the different mappings to the columns
    Visit_occurence_table = pd.DataFrame({
        "visit_occurrence_id" : ADMISSIONS["hadm_id"],	
        "person_id" : ADMISSIONS["subject_id"],
        "visit_concept_id" : np.repeat("9203",ADMISSIONS.shape[0]), # all emergency room
        #https://athena.ohdsi.org/search-terms/terms?domain=Visit&standardConcept=Standard&page=1&pageSize=15&query=emergency&boosts
        "visit_start_date" : ADMISSIONS["admittime"],
        "visit_end_date" : ADMISSIONS["dischtime"],
        "visit_type_concept_id" : np.repeat("32817",ADMISSIONS.shape[0])
    })
    return Visit_occurence_table

# Condition_occurence
def generate_condition_occurence_table():
    # Read all tables that are necessary to generate the table
    CO = read_table("DEATH")

    # apply the different mappings to the columns
    Condition_occurence_table = pd.DataFrame({
        "person_id" : PO["subject_id"],
        "condition_occurrence_id" : "",
        "condition_concept_id" : "",
    })
    return Condition_occurence_table

# Procedure_occurence
def generate_procedure_occurence_table():
    # Read all tables that are necessary to generate the table
    PO = read_table("PROCEDUREEVENTS_MV")

    # apply the different mappings to the columns
    Procedure_occurence_table = pd.DataFrame({
        "person_id" : PO["subject_id"],
        "procedure_date" : PO["starttime"],
        "procedure_occurrence_id" : PO["icustay_id"],	
        "procedure_concept_id" : "",
        "procedure_type_concept_id" : "",
        })
    return Procedure_occurence_table

# Measurement
def generate_measurement_table():
    # Read all tables that are necessary to generate the table
    MM = read_table("LABEVENTS")

    # apply the different mappings to the columns
    Measurement_table = pd.DataFrame({
        "measurement_id" : "integer",
        "person_id" : MM["subject_id"],
        #A foreign key identifier to the Person about whom the measurement was recorded. The demographic details of that Person are stored in the PERSON table.
        "measurement_concept_id" : "integer",
        #A foreign key to the standard measurement concept identifier in the Standardized Vocabularies.
        "measurement_date" : "date",
        #The date of the Measurement.
        "measurement_type_concept_id" : "integer",
        #A foreign key to the predefined Concept in the Standardized Vocabularies reflecting the provenance from where the Measurement record was recorded.
        })
    return Measurement_table



# CDM_source
def generate_cdm_source_table():
    # apply the different mappings to the columns
    cdm_source_table = pd.DataFrame({
        "cdm_source_name" : ["MIMIC III"],
        "cdm_etl_reference" : ["https://github.com/AntoinePoirotBourdain/MockEDS"]
    })
    	
    return cdm_source_table


######################## Source code ####################################################################

DATA_PATH = Path("MIMIC_data")

def generate_table(table_name):
    """Generate a table dynamically based on its name."""
    try:
        if table_name in TABLE_GENERATORS:
            return TABLE_GENERATORS[table_name]()
        else:
            raise ValueError(f"No generator defined for table: {table_name}")
        
    except Exception as e:
        print(f"Error generating table: {e}")
        return None
    

def read_table(table_name):
    """Read a table from a CSV file dynamically."""
    file_path = DATA_PATH / f"{table_name}.csv"
    try:
        if file_path.exists():
            return pd.read_csv(file_path)
        else:
            raise FileNotFoundError(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading table: {e}")
        return None
    
def get_mapping_table(concept_name):
    
    mapping_table = pd.read_csv(Path("mappings/" + concept_name + ".csv"))
    mapping_dict = dict(zip(mapping_table['sourceCode'], mapping_table['conceptId']))


    return mapping_dict
    

def apply_mapping(serie_source,concept_source):

    mapping_dict = get_mapping_table(concept_source)
    serie_target = serie_source.map(mapping_dict)
        
    return serie_target

def default_mapping(concept_target, n_rows):
    
    try:
        default_mapping_table = pd.read_csv(Path("mappings/default.csv"))

        default_mapping_concept = default_mapping_table[default_mapping_table["concept_target"] == concept_target]["conceptId"].values[0]

        return [default_mapping_concept] * n_rows
    
    except FileNotFoundError:
        print(f"Error: File not found: mappings/default.csv")
        return None
    except IndexError:
        print(f"Error: Concept target '{concept_target}' not found in default mapping table")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None



    


default_mapping("race_concept_id",10)


