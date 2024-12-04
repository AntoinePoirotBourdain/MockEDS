import pandas as pd
from pathlib import Path


TABLE_GENERATORS = {
    "persons": lambda: generate_persons_table(),
    # Add other table-specific generators here
}


########################### Specific table generation ###############################################################


def generate_persons_table():

    # Read all tables that are necessary to generate the persons table
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
    
    mapping_table = pd.read_csv(Path("mappings/" + concept_name + "_mapped.csv"))
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


