from datasets import load_dataset, Dataset
import pandas as pd
import os

# SELECT license, count(*) as total FROM train group by license order by count(*) desc;
# License info:
#   none:       3,686
#   cc-by-4.0:  1,548
#   apache-2.0: 210
#   mit:        179
#   - :         91
data_set_name = "mlfoundations-dev/openthoughts_3_dedup_code"
data_set = load_dataset(data_set_name)
df_pandas = pd.DataFrame(data_set)
hugging_face_user = os.environ["HUGGINGFACE_USER"]

all_licenses_filtered = []
apache_licenses_filtered = []
for index, row in df_pandas.iterrows():
    if row["train"]["license"] in ["cc-by-4.0", "apache-2.0", "mit"]:
        all_licenses_filtered.append(row["train"])
    if row["train"]["license"] in ["apache-2.0"]:
        apache_licenses_filtered.append(row["train"])

df_pandas_all_licenses_filtered = pd.DataFrame(all_licenses_filtered)

df_pandas_apache_licenses_filtered = pd.DataFrame(apache_licenses_filtered)

target_hf_all_licenses_dataset = Dataset.from_pandas(df_pandas_all_licenses_filtered)
target_hf_apache_licenses_dataset = Dataset.from_pandas(
    df_pandas_apache_licenses_filtered
)

target_hf_all_licenses_dataset.push_to_hub(
    "jolson-ibm/openthoughts_3_dedup_code_licensed_only"
)

target_hf_apache_licenses_dataset.push_to_hub(
    "jolson-ibm/openthoughts_3_dedup_code_apache_license_only"
)
