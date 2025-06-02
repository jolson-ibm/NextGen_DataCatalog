# Inlined from /metadata-ingestion/examples/library/delete_dataset.py
import logging
import os

from datahub.emitter.mce_builder import make_dataset_urn
from datahub.ingestion.graph.client import DatahubClientConfig, DataHubGraph

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

source_platform = "huggingface"
data_set_to_delete = "james-burton/wine_reviews"

graph = DataHubGraph(
    config=DatahubClientConfig(
        server=os.environ["LOCAL_DATAHUB_API_ENDPOINT"],
    )
)

dataset_urn = make_dataset_urn(name=data_set_to_delete, platform=source_platform)

# Hard-delete the dataset.
graph.delete_entity(urn=dataset_urn, hard=True)

log.info(f"Deleted dataset {dataset_urn}")
