import pandas as pd
from pathlib import Path
import numpy as np


# difference entre table de réfe
TABLE_GENERATORS = {
    "persons": lambda: generate_persons_table(),
    "observation_period": lambda: generate_observation_period_table(),
    "death": lambda: generate_death_table(),
    "visit_occurence": lambda: generate_visit_occurence_table(),
    "condition_occurence": lambda: generate_condition_occurence_table(),
    "procedure_occurence": lambda: generate_procedure_occurence_table(),
    "measurements": lambda: generate_measurement_table(),
    "drug_exposure": lambda: generate_drug_exposure_table(),
    "cdm_source": lambda: generate_cdm_source_table(),
    #"locations": lambda: generate_Location_table(),
    #"vocabularys": lambda: generate_Vocabulary_table(),
    #"domains": lambda: generate_Domain_table(),
    #"cohorts": lambda: generate_Cohort_table(),
    #"cohort_definitions": lambda: generate_Cohort_definition_table(),
    # Add other table-specific generators here
}


# def generate_concept_map(concept_list):

#     concept_map_total = pd.read_csv(Path("concept_map/" + concept_list[0] + ".csv"))
#     print(concept_map_total)
#     #for concept in concept_list:
#     #    map 



########################### Specific table generation ###############################################################


# Person
def generate_persons_table():
    # Read all tables that are necessary to generate the table
    PATIENTS = read_table("PATIENTS")
    concept_map = get_mapping_table()

    # apply the different mappings to the columns

    person_table = pd.DataFrame({
        "person_id" : PATIENTS["subject_id"],
        "gender_concept_id" : apply_mapping(PATIENTS["gender"]),
        "year_of_birth" : pd.to_datetime(PATIENTS["dob"]).dt.year,
        "race_concept_id" : PATIENTS.shape[0] * [None],
        "ethnicity_concept_id" : PATIENTS.shape[0] * [None]
    })


    return person_table

# Observation_Period
def generate_observation_period_table():
    # Dot it with admission and discharge time
    ADMISSIONS = read_table("ADMISSIONS")
    observation_period_table = pd.DataFrame({
        "person_id" : ADMISSIONS["subject_id"],
        "observation_period_id" : ADMISSIONS["hadm_id"],
        "observation_period_start_date" : ADMISSIONS["admittime"],
        "observation_period_end_date" : ADMISSIONS["dischtime"]
    })

    return observation_period_table

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
        "visit_occurrence_id" : ADMISSIONS["hadm_id"].astype("str"),
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
    ADMISSIONS = read_table("ADMISSIONS")
    concept_map = get_mapping_table()

    DIAGNOSES_ICD = read_table("DIAGNOSES_ICD")


    conditions_start_date = dates_from_hadm_id(DIAGNOSES_ICD["hadm_id"])

    mapping_dict = get_mapping_table()
    #conditions_start_date.shape



    # apply the different mappings to the columns
    Condition_occurence_table = pd.DataFrame({
        "person_id" : DIAGNOSES_ICD["subject_id"],
        "condition_occurrence_id" : DIAGNOSES_ICD["hadm_id"], 
        "condition_start_date" : conditions_start_date,
        "condition_concept_id" : apply_mapping(DIAGNOSES_ICD["icd9_code"]),
    })
    return Condition_occurence_table

def generate_measurement_table():

    CHARTEVENTS = read_table("CHARTEVENTS")
    concept_map = get_mapping_table()


    # apply the different mappings to the columns
    Measurement_table_1 = pd.DataFrame({
        "measurement_id" : CHARTEVENTS["row_id"],
        "person_id" : CHARTEVENTS["subject_id"],
        "visit_occurrence_id" : CHARTEVENTS["hadm_id"].astype("str"),
        "measurement_concept_id" : apply_mapping(CHARTEVENTS["itemid"]),
        "measurement_date" : CHARTEVENTS["charttime"],
        "measurement_type_concept_id" : np.repeat(32817, CHARTEVENTS.shape[0]),  # Example concept ID
        "value_as_number" : CHARTEVENTS["valuenum"],
        "unit_source_value" : CHARTEVENTS["valueuom"]})
    
    # get measurement table 2 from labevents

    LABEVENTS = read_table("LABEVENTS")

    measurement_table_2 = pd.DataFrame({
        "measurement_id" : LABEVENTS["row_id"],
        "person_id" : LABEVENTS["subject_id"],
        "visit_occurrence_id" : LABEVENTS["hadm_id"].astype("str"),
        "measurement_concept_id" : ["toto"]* LABEVENTS.shape[0],
        "measurement_date" : LABEVENTS["charttime"],
        "measurement_type_concept_id" : np.repeat(32817, LABEVENTS.shape[0]),  # Example concept ID
        "value_as_number" : LABEVENTS["valuenum"],
        "unit_source_value" : LABEVENTS["valueuom"]})
    
    Measurement_table = pd.concat([Measurement_table_1, measurement_table_2])



    

    return Measurement_table


def generate_drug_exposure_table():
    # Read all tables that are necessary to generate the table
    PRESCRIPTIONS = read_table("PRESCRIPTIONS")

    
    concept_map = get_mapping_table()


    drug_exposure_table = pd.DataFrame({
        "drug_exposure_id" : PRESCRIPTIONS["row_id"],
        "person_id" : PRESCRIPTIONS["subject_id"],
        "visit_occurrence_id" : PRESCRIPTIONS["hadm_id"].astype("str"),
        "drug_concept_id" : apply_mapping(PRESCRIPTIONS["ndc"]),
        "drug_exposure_start_date" : PRESCRIPTIONS["startdate"],
        "drug_exposure_end_date" : PRESCRIPTIONS["enddate"],
        "drug_type_concept_id" : np.repeat(32817, PRESCRIPTIONS.shape[0]),  # Example concept ID
        "quantity" : PRESCRIPTIONS["dose_val_rx"]
    })

    return drug_exposure_table


def generate_procedure_occurence_table():
    # Read all tables that are necessary to generate the table
    PROCEDURES_ICD = read_table("PROCEDURES_ICD")
    
    ADMISSION = read_table("ADMISSIONS")
    

    admission_times = dates_from_hadm_id(PROCEDURES_ICD["hadm_id"])



    # apply the different mappings to the columns
    Procedure_occurence_table = pd.DataFrame({
        "person_id" : PROCEDURES_ICD["subject_id"],
        "visit_occurrence_id" : PROCEDURES_ICD["hadm_id"].astype("str"),
        "procedure_occurrence_id" : PROCEDURES_ICD["row_id"],	
        "procedure_date" : admission_times,
        "procedure_concept_id" : apply_mapping(PROCEDURES_ICD["icd9_code"]),
        "procedure_type_concept_id" : np.repeat(32817, PROCEDURES_ICD.shape[0]),  # Example concept ID
        })
    
    return Procedure_occurence_table







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
    
def get_mapping_table():
    
    concept_map = pd.read_csv(Path("concept_map/concept_map_total.csv"))
    mapping_dict = dict(zip(concept_map['source_code'], concept_map['target_concept_id']))


    return mapping_dict


def apply_mapping(serie_source):
    
        mapping_dict = get_mapping_table()
        serie_target = serie_source.astype("str").map(mapping_dict).astype("str")
            
        return serie_target
    



    

def dates_from_hadm_id(hadm_ids):
    ADMISSIONS = pd.read_csv("MIMIC_data/ADMISSIONS.csv")
    return hadm_ids.map(ADMISSIONS.set_index("hadm_id")["admittime"])


def generate_empty_tables():
    
    # Device_exposure
    device_exposure_table = pd.DataFrame({
        "device_exposure_id" : [],
        "person_id" : [],
        "device_concept_id" : [],
        "device_exposure_start_date" : [],
        "device_exposure_end_date" : [],
        "device_type_concept_id" : [],
    })

    device_exposure_table.to_csv("OMOP_data/device_exposure.csv", index=False)


    Visit_detail_table = pd.DataFrame({
        "visit_detail_id" : [],
        "visit_occurrence_id" : [],
        "visit_detail_concept_id" : [],
        "visit_detail_start_date" : [],
        "visit_detail_end_date" : [],
        "visit_detail_type_concept_id" : []
    })

    Visit_detail_table.to_csv("OMOP_data/visit_detail.csv", index=False)

    observation_table = pd.DataFrame({
        "observation_id" : [],
        "person_id" : [],
        "observation_concept_id" : [],
        "observation_date" : [],
        "observation_type_concept_id" : [],
        "value_as_number" : [],
        "unit_source_value" : []
    })

    observation_table.to_csv("OMOP_data/observation.csv", index=False)

    Note_table = pd.DataFrame({
        "note_id" : [],
        "person_id" : [],
        "note_date" : [],
        "note_concept_id" : [],
        "note_type_concept_id" : [],
        "note_text" : []
    })

    Note_table.to_csv("OMOP_data/note.csv", index=False)

    Note_NLP_table = pd.DataFrame({
        "note_nlp_id" : [],
        "note_id" : [],
        "section_concept_id" : [],
        "snippet" : [],
        "offset" : [],
        "lexical_variant" : [],
        "note_nlp_concept_id" : []
    })

    Episode_table = pd.DataFrame({
        "episode_id" : [],
        "person_id" : [],
        "episode_concept_id" : [],
        "episode_start_date" : [],
        "episode_end_date" : [],
        "episode_type_concept_id" : []
    })

    Episode_table.to_csv("OMOP_data/episode.csv", index=False)

    Episode_event_table = pd.DataFrame({
        "episode_event_id" : [],
        "episode_id" : [],
        "episode_event_concept_id" : [],
        "episode_event_date" : [],
        "episode_event_type_concept_id" : []
    })

    Episode_event_table.to_csv("OMOP_data/episode_event.csv", index=False)

    Specimen_table = pd.DataFrame({
        "specimen_id" : [],
        "person_id" : [],
        "specimen_concept_id" : [],
        "specimen_date" : [],
        "specimen_type_concept_id" : []
    })

    Fact_relationship_table = pd.DataFrame({
        "domain_concept_id_1" : [],
        "fact_id_1" : [],
        "domain_concept_id_2" : [],
        "fact_id_2" : [],
        "relationship_concept_id" : []
    })

    Fact_relationship_table.to_csv("OMOP_data/fact_relationship.csv", index=False)


    Location_table = pd.DataFrame({
        "location_id" : [],
        "location_concept_id" : [],
        "location_start_date" : [],
        "location_end_date" : [],
        "location_type_concept_id" : []
    })

    Location_table.to_csv("OMOP_data/location.csv", index=False)

    Cost_table = pd.DataFrame({
        "cost_id" : [],
        "cost_concept_id" : [],
        "cost_date" : [],
        "cost_type_concept_id" : [],
        "value_as_number" : [],
        "currency_concept_id" : []
    })

    Cost_table.to_csv("OMOP_data/cost.csv", index=False)

    Payer_plan_period_table = pd.DataFrame({
        "payer_plan_period_id" : [],
        "person_id" : [],
        "payer_plan_period_start_date" : [],
        "payer_plan_period_end_date" : [],
        "payer_source_value" : [],
        "plan_source_value" : [],
        "family_source_value" : [],
        "payer_plan_period_type_concept_id" : []
    })

    Payer_plan_period_table.to_csv("OMOP_data/payer_plan_period.csv", index=False)

    condition_era_table = pd.DataFrame({
        "condition_era_id" : [],
        "person_id" : [],
        "condition_concept_id" : [],
        "condition_era_start_date" : [],
        "condition_era_end_date" : [],
        "condition_occurrence_count" : []
    })

    condition_era_table.to_csv("OMOP_data/condition_era.csv", index=False)

    Drug_Era_table = pd.DataFrame({
        "drug_era_id" : [],
        "person_id" : [],
        "drug_concept_id" : [],
        "drug_era_start_date" : [],
        "drug_era_end_date" : [],
        "drug_exposure_count" : []
    })

    Drug_Era_table.to_csv("OMOP_data/drug_era.csv", index=False)

    Dose_era_table = pd.DataFrame({
        "dose_era_id" : [],
        "person_id" : [],
        "unit_concept_id" : [],
        "dose_value" : [],
        "dose_era_start_date" : [],
        "dose_era_end_date" : []
    })

    Dose_era_table.to_csv("OMOP_data/dose_era.csv", index=False)

    Cohort_table = pd.DataFrame({
        "cohort_id" : [],
        "subject_id" : [],
        "cohort_start_date" : [],
        "cohort_end_date" : [],
        "stop_reason" : []
    })

    Cohort_table.to_csv("OMOP_data/cohort.csv", index=False)

    Cohort_defintion_table = pd.DataFrame({
        "cohort_definition_id" : [],
        "cohort_id" : [],
        "cohort_definition_name" : [],
        "cohort_definition_description" : [],
        "cohort_definition_type_concept_id" : []
    })

    Cohort_defintion_table.to_csv("OMOP_data/cohort_definition.csv", index=False)


    Metadata_table = pd.DataFrame({
        "metadata_id" : [],
        "metadata_concept_id" : [],
        "metadata_date" : [],
        "metadata_type_concept_id" : [],
        "metadata_value" : []
    })

    Metadata_table.to_csv("OMOP_data/metadata.csv", index=False)




