
############################## first i import packages I need thorugh the project 

import pandas as pd
import os
import csv
import json
import re

import sys



##### NLP packages
import spacy
import spacy
from negspacy.negation import Negex 
from spacy import displacy
from scispacy.linking import EntityLinker













############################## here I load the structured(csv file) and messy data (narrative text):


# Set base path to your project data folder
base_data_dir = "/Users/rozhinmt/Desktop/DH-2026-02-clinical-data-harmonization/data"

# File paths
csv_path = os.path.join(base_data_dir, "structured", "patient_lab_results.csv")
txt_path = os.path.join(base_data_dir,"unstructured", "note_N204.txt")

# 1. Read Structured CSV Data
csv_records = []
with open(csv_path, mode="r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        csv_records.append(dict(row))

print("Loaded CSV Record:")
print(csv_records)

# 2. Read Narrative Text Note Data
with open(txt_path, mode="r", encoding="utf-8") as f:
    narrative_text = f.read()

print("\nLoaded Narrative Text Note:")
print(narrative_text)










############################## NOW load the config based on hospital :

base_dir = "/Users/rozhinmt/Desktop/DH-2026-02-clinical-data-harmonization"
config_path = os.path.join(base_dir, "config", "hospital_a_mappings.json")

# Load mapping dynamically from configuration file
with open(config_path, mode="r", encoding="utf-8") as f:
    LOCAL_MAPPING = json.load(f)

print("Loaded Mapping Config:")
print(LOCAL_MAPPING)








################################### Now I will use csv and the mapping to extract features.

def process_csv_record(record: dict, row_idx: int = 1, doc_id: str = "patient_lab_results.csv") -> dict:
    """
    Automates extracting a canonical record from a single CSV dictionary row.
    Safely handles missing fields without guessing.
    """
    # 1. Safely extract patient and encounter fields (default to None if missing)
    patient_id = record.get("patient_id") or None
    event_time = record.get("result_time") or None
    
    # 2. Terminology Mapping with Fallback
    local_code = record.get("test_code")
    test_name = record.get("test_name") or "Unknown Test"
    
    if local_code in LOCAL_MAPPING:
        concept = LOCAL_MAPPING[local_code]
        extraction_method = "dictionary"
    else:
        concept = {
            "system": "LOCAL_UNMAPPED",
            "code": local_code if local_code else "UNKNOWN",
            "display": test_name
        }
        extraction_method = "rule"

    # 3. Parse Numeric Value safely
    raw_val = record.get("result_value")
    try:
        val_number = float(raw_val) if raw_val is not None and raw_val != "" else None
    except ValueError:
        val_number = None

    # 4. Check for missing required information (No Guessing Rule - Gate G3)
    unit = record.get("result_unit") or None
    missing_required = []
    
    if val_number is None:
        missing_required.append("result_value")
    if not unit:
        missing_required.append("result_unit")
    if not event_time:
        missing_required.append("result_time")
    if local_code not in LOCAL_MAPPING:
        missing_required.append("unmapped_local_code")

    # If required information is missing, route to human review queue
    review_status = "needs_review" if missing_required else "accepted"

    # 5. Build Canonical Fact
    fact = {
        "category": "observation",
        "concept": concept,
        "value": {
            "number": val_number,
            "text": None,
            "unit": unit
        },
        "assertion": "present",
        "temporality": "current",
        "effective_time": event_time,
        "source_ref": {
            "document_id": doc_id,
            "field_path": f"row_{row_idx}:result_value",
            "text_span": None
        },
        "extraction_method": extraction_method,
        "review_status": review_status,
        "quality": {
            "missing_required": missing_required,
            "conflicts": [],
            "warnings": []
        }
    }

    # 6. Build Top-Level Canonical Record Structure
    return {
        "schema_version": "1.0",
        "patient": {
            "source_patient_id": patient_id,
            "birth_date": record.get("birth_date") or None
        },
        "encounter": {
            "source_encounter_id": record.get("encounter_id") or None,
            "event_time": event_time
        },
        "facts": [fact]
    }

# Now i would execute it on csv
canonical_output = process_csv_record(csv_records[0], row_idx=1)
# print(json.dumps(canonical_output, indent=2))










################################### for age detection : I did not use it as i dont have time to focus on details so i prefer left itjust here and test it over the narrative text :

def handling_patients_age(narrative_text):
    """
    Returns:
        int  -> patient's age if detected
        None -> if no age expression is found
    """

    text = narrative_text.lower()

  
    age_patterns = [

        # 45 years old
        r'\b(\d{1,3})\s+years?\s+old\b',

        # 45 year-old / 45-year-old
        r'\b(\d{1,3})\s*[-]?\s*years?\s*[-]?\s*old\b',

        # 45 years of age
        r'\b(\d{1,3})\s+years?\s+of\s+age\b',

        # 45 yo / 45 y.o. / 45yo
        r'\b(\d{1,3})\s*y\.?\s*o\.?\b',

        # 45 y/o
        r'\b(\d{1,3})\s*y\s*/\s*o\b',

        # 45 yr old / 45 yrs old
        r'\b(\d{1,3})\s*yrs?\.?\s+old\b',

        # age 45
        r'\bage\s*[:\-]?\s*(\d{1,3})\b',

        # aged 45
        r'\baged\s+(\d{1,3})\b',
    ]


    for pattern in age_patterns:

        match = re.search(pattern, text)

        if match:
            age = int(match.group(1))


            if 0 <= age <= 120:
                return age

    # No age found
    return None

a = handling_patients_age(narrative_text)
print(a)







###################################################################### the most time consuming part of the project (I mean narrative text analysis) :

# I PERSONALLY WANTED to use LLM approach and pre-trained approach to extract reliable features from the narrative text. (sort of majority voting approach) , getting started to find which LLM packages are free and usable for my task , I lost track of time so I rapidly made p of my mind and planned to just use the pre -trained model due to the tight deadline. also i did not put much effort on validation and setting manual rules. I mostly focused on the model , about how it works , what is its aim and how it is suitable for my data . Nice expeience !



#- first install packages required for pre-trained model



# !{sys.executable} -m pip install spacy scispacy
# !{sys.executable} -m pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.4/en_core_sci_sm-0.5.4.tar.gz




# ---------------------- THE goal is to get the negations from the narrative text : so I pass the text using the pre-trained model.>>> Clinical Entity & Negation Extraction

# sciSpacy biomedical pipeline
nlp = spacy.load("en_core_sci_sm")

doc = nlp(narrative_text)

# Extract and display entities
print(f"{'ENTITY':<30} | {'LABEL / TYPE':<15}")
print("-" * 50)
for ent in doc.ents:
    print(f"{ent.text:<30} | {ent.label_:<15}")





########################## we just now get medical entities but it doesnt detect the scope , I mean it doesnt classify the symptoms from drug or disease.>>>>  so we need to dive in to UMLS linking .



# import sys
# !{sys.executable} -m pip install negspacy

nlp = spacy.load("en_core_sci_sm")

nlp.add_pipe("negex", config={"ent_types": ["ENTITY"]})
doc = nlp(narrative_text)

# Display extracted entities and negation status
print(f"{'ENTITY':<35} | {'NEGATED?':<10}")
print("-" * 50)
for ent in doc.ents:
    is_negated = getattr(ent._, "negex", False)
    print(f"{ent.text:<35} | {str(is_negated):<10}")





# visualizing the entities
displacy.render(doc, style="ent", jupyter=True)

########################### as requested in the assignemtn , I need to declare where I found (which character) was negation .

results = []
for ent in doc.ents:
    results.append({
        "Entity": ent.text,
        "Start_Char": ent.start_char,
        "End_Char": ent.end_char,
        "Is_Negated": getattr(ent._, "negex", False)
    })

df = pd.DataFrame(results)
df#head(15)




###########################  but now we do need to understand the linking for each entity. so dive in to UMLS : how does it work!!?  UMLS try to match each entity whoch is coded in its starndard medical database, based on simlarity , so it is not an absoloute correct path :

# Medical Entity Linking to UMLS >>> this indeed took time . dont worry!!

# Load model and negation pipeline
nlp = spacy.load("en_core_sci_sm")

# Add UMLS linker (this resolves terms to medical concept IDs)
nlp.add_pipe(
    "scispacy_linker", 
    config={"resolve_abbreviations": True, "linker_name": "umls"}
)

doc = nlp(narrative_text)
linker = nlp.get_pipe("scispacy_linker")

# Extract canonical concept names and UMLS IDs
linked_data = []
for ent in doc.ents:
    cui_id, concept_name = "N/A", "N/A"
    if ent._.kb_ents:
        best_match = ent._.kb_ents[0] # Take highest-confidence match
        cui_id = best_match[0]
        concept_name = linker.kb.cui_to_entity[cui_id].canonical_name

    linked_data.append({
        "Entity": ent.text,
        "UMLS_CUI": cui_id,
        "Canonical_Name": concept_name
    })

pd.DataFrame(linked_data)#.head(10)



####################################################### the problem was that in the example the entity of flight had been converted to the  space flight which is not relevant. also we need to know which TUIs are needed, this could be provided by the hospital and be set in config file not here :>>> TARGET_TUIS = {"T047", "T121", "T184", "T201", "T033", "T059"}


# Cleaned Pipeline with Semantic Type Filtering

nlp = spacy.load("en_core_sci_sm")

if "negex" not in nlp.pipe_names:
    nlp.add_pipe("negex", config={"ent_types": ["ENTITY"]})

if "scispacy_linker" not in nlp.pipe_names:
    nlp.add_pipe("scispacy_linker", config={"resolve_abbreviations": True, "linker_name": "umls"})

doc = nlp(narrative_text)
linker = nlp.get_pipe("scispacy_linker")

# Define target clinical semantic types (TUI codes)  >>>>  T047: Disease/Syndrome, T121: Pharmacologic Substance, T184: Sign/Symptom, T201: Clinical Attribute
TARGET_TUIS = {"T047", "T121", "T184", "T201", "T033", "T059"}

cleaned_results = []

for ent in doc.ents:
    if ent._.kb_ents:
        cui_id, score = ent._.kb_ents[0]
        entity_obj = linker.kb.cui_to_entity[cui_id]
        
        # Check if concept matches standard clinical categories
        tuis = set(entity_obj.types)
        if tuis.intersection(TARGET_TUIS):
            cleaned_results.append({
                "Entity": ent.text,
                "Is_Negated": getattr(ent._, "negex", False),
                "UMLS_CUI": cui_id,
                "Canonical_Name": entity_obj.canonical_name,
                "Semantic_Types": list(tuis)
            })

df_clean = pd.DataFrame(cleaned_results)
df_clean


####################################################### UNFORTUNATELY the entity of shortness of breath was not detcted accurately. but i moved forward to define the output file.



match = re.search(r"Document\s+([A-Za-z0-9\-]+)", narrative_text)
document_id = match.group(1) if match else "unspecified_doc"
document_id

output_json_data = {
    "document_id":document_id , 
    "extracted_entities": df_clean.to_dict(orient="records")
}






import copy


def transform_and_merge_nlp(
    canonical_dict, nlp_dict, default_category="observation"
):
    """Dynamically converts NLP entities from nlp_dict into canonical fact objects

    and appends them to canonical_dict['facts'].
    """
    merged_data = copy.deepcopy(canonical_dict)
    doc_id = nlp_dict.get("document_id", "unspecified_doc")
    encounter_time = merged_data.get("encounter", {}).get("event_time")

    for entity in nlp_dict.get("extracted_entities", []):
        assertion_raw = str(entity.get("Assertion_Status", "Present")).lower()
        assertion_val = "absent" if assertion_raw == "absent" else "present"

        conf_score = entity.get("Confidence_Score", 1.0)
        warnings = (
            [f"Low confidence entity extraction ({conf_score})"]
            if conf_score < 0.85
            else []
        )

        fact = {
            "category": default_category,
            "concept": {
                "system": "UMLS",
                "code": entity.get("UMLS_CUI"),
                "display": entity.get("Canonical_Medical_Name"),
            },
            "value": {"number": None, "text": None, "unit": None},
            "assertion": assertion_val,
            "temporality": "current",
            "effective_time": encounter_time,
            "source_ref": {
                "document_id": doc_id,
                "field_path": "text",
                "text_span": entity.get("Extracted_Term"),
            },
            "extraction_method": "model",
            "review_status": (
                "accepted" if conf_score >= 0.85 else "needs_review"
            ),
            "quality": {
                "missing_required": [],
                "conflicts": [],
                "warnings": warnings,
            },
        }

        merged_data["facts"].append(fact)

    return merged_data


# Assuming your variable name for the NLP dict is `nlp_data`:
final_json_output = transform_and_merge_nlp(canonical_output, output_json_data)

final_json_output
