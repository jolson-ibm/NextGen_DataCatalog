import datahub.emitter.mce_builder as builder
from datahub.emitter.mce_builder import make_tag_urn, make_user_urn
from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.metadata.schema_classes import (
    GlobalTagsClass,
    TagAssociationClass,
    EditableDatasetPropertiesClass,
)
from datahub.metadata.schema_classes import (
    SchemaMetadataClass,
    SchemaFieldClass,
    SchemaFieldDataTypeClass,
    StringTypeClass,
    NumberTypeClass,
    DateTypeClass,
    AuditStampClass,
    OtherSchemaClass,
    OwnerClass,
    OwnershipTypeClass,
)
from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.specific.dataset import DatasetPatchBuilder

import pandas as pd
import json
import time
import os


def current_milli_time():
    return round(time.time() * 1000)


emitter = DatahubRestEmitter(gms_server=os.environ["LOCAL_DATAHUB_API_ENDPOINT"])
sample_data_set = "james-burton/wine_reviews"
source_platform = "huggingface"

current_time_millis = current_milli_time()

df_all = pd.read_parquet("../data")
df = df_all.query(f"dataset == '{sample_data_set}'")
for index, row in df.iterrows():
    if row["response"] not in [400, 401]:
        croissant_dict = json.loads(row["croissant"])
        datahub_dict = {}
        datahub_dict["name"] = row["dataset"]
        print(f"""Processing: {datahub_dict["name"]}""")

        datahub_dict["license"] = "N/A"
        if "license" in croissant_dict:
            datahub_dict["license"] = (
                croissant_dict["license"]
                .replace("https://choosealicense.com/licenses/", "")
                .replace("/", "")
            )
        datahub_dict["description"] = "N/A"
        if "description" in croissant_dict:
            datahub_dict["description"] = croissant_dict["description"]
        datahub_dict["keywords"] = []
        if "keywords" in croissant_dict:
            datahub_dict["keywords"] = croissant_dict["keywords"]
        if "creator" in croissant_dict:
            datahub_dict["creator"] = croissant_dict["creator"]
        for record in croissant_dict["recordSet"]:
            if "name" in record:
                if record["name"] == "default":
                    datahub_dict["fields"] = []
                    for each_field in record["field"]:
                        if "dataType" in each_field:
                            this_field = {}
                            this_field["name"] = each_field["name"].replace(
                                "default/", ""
                            )
                            if this_field["name"] != "split":
                                this_field["native_type"] = each_field[
                                    "dataType"
                                ].replace("sc:", "")
                                this_field["description"] = each_field["description"]
                                datahub_dict["fields"].append(this_field)
                        else:
                            print("\t\tNo dataType found!")
            else:
                print("\tName not found!")
        print(f"""Datahub record: {json.dumps(datahub_dict, indent=3)}""")
        print("----------------")

        # Define the dataset URN
        dataset_urn = builder.make_dataset_urn(
            platform=source_platform, name=datahub_dict["name"], env="PROD"
        )

        schema_fields = []
        if "fields" in datahub_dict:
            for field in datahub_dict["fields"]:
                native_data_type = field["native_type"]
                if native_data_type == "Text":
                    type = SchemaFieldDataTypeClass(type=StringTypeClass())
                elif native_data_type == "Float" or native_data_type == "Integer":
                    type = SchemaFieldDataTypeClass(type=NumberTypeClass())
                # TODO: Fix this...What are all the types available?
                else:
                    type = SchemaFieldDataTypeClass(type=StringTypeClass())

                this_schema_field = SchemaFieldClass(
                    fieldPath=field["name"],
                    type=type,
                    nativeDataType=native_data_type,
                    description=each_field["description"],
                    lastModified=AuditStampClass(
                        time=current_time_millis, actor="urn:li:corpuser:ingestion"
                    ),
                )
                schema_fields.append(this_schema_field)

        schema_metadata = SchemaMetadataClass(
            schemaName="customer",
            platform=builder.make_data_platform_urn(source_platform),
            version=0,
            hash="",
            platformSchema=OtherSchemaClass(rawSchema="__insert raw schema here__"),
            fields=schema_fields,
            lastModified=AuditStampClass(
                time=current_time_millis, actor="urn:li:corpuser:ingestion"
            ),
        )

        # Create a MetadataChangeProposalWrapper object
        mcp = MetadataChangeProposalWrapper(
            entityUrn=dataset_urn, aspect=schema_metadata
        )

        # Emit the metadata
        emitter.emit(mcp)

        if "keywords" in datahub_dict:
            tags = []
            for keyword in datahub_dict["keywords"]:
                tags.append(make_tag_urn(keyword))
            global_tags = GlobalTagsClass(
                tags=[TagAssociationClass(tag) for tag in tags]
            )
            mcp2 = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn, aspect=global_tags
            )
            emitter.emit(mcp2)

        if "creator" in datahub_dict:
            owner_string = f"""{datahub_dict["creator"]["name"]}: {datahub_dict["creator"]["url"]}"""

            patch_builder = DatasetPatchBuilder(dataset_urn)
            patch_builder.add_owner(
                OwnerClass(
                    make_user_urn(owner_string), OwnershipTypeClass.TECHNICAL_OWNER
                )
            )
            patch_mcps = patch_builder.build()
            for patch_mcp in patch_mcps:
                emitter.emit(patch_mcp)

        if "description" in datahub_dict:
            current_timestamp = AuditStampClass(
                time=current_time_millis, actor="urn:li:corpuser:ingestion"
            )
            current_editable_properties = EditableDatasetPropertiesClass(
                created=current_timestamp, description=datahub_dict["description"]
            )
            mcp4 = MetadataChangeProposalWrapper(
                entityUrn=dataset_urn, aspect=current_editable_properties
            )
            emitter.emit(mcp4)
