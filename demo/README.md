# Next Generation Data Catalog Demo

The purpose of this directory is to house code and documentation for setting up and executing the NextGen Data Catalog demo. This demo is based on the open source data catalog [DataHub](https://datahub.com/). This is to demonstrate the prnciples advocated by [The AI Alliance's](https://thealliance.ai/) [Open and Trusted Data Initiative](https://the-ai-alliance.github.io/open-trusted-data-initiative/) (OTDI).

This demo is designed to run on a local machine, 

## Setup

1. Follow the [DataHub Quickstart Guide](https://docs.datahub.com/docs/quickstart) to install and run DataHub locally.
2. Once installed, use `./src/load.py` to load the initial test set. Two variables will need to be modified here`: the URL to tha API endpoint of DataHub, and the location of the test data to load.