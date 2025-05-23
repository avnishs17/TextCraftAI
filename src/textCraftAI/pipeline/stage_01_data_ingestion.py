from textCraftAI.config.configuration import ConfigurationManager
from textCraftAI.components.data_ingestion import DataIngestion
from textCraftAI.logging import logger


class DataIngestionTrainingPipeline:
    def __init__(self):
        pass

    def main(self):
        config = ConfigurationManager()
        data_ingestion_config = config.get_data_ingestion_config()
        data_ingestion = DataIngestion(config=data_ingestion_config)
        data_ingestion.load_and_save_dataset()