from datasets import load_dataset
from textCraftAI.logging import logger
from textCraftAI.entity.config_entity import DataIngestionConfig

class DataIngestion:
    def __init__(self, config: DataIngestionConfig):
        self.config = config

    def load_and_save_dataset(self):
        # Load dataset from Hugging Face Hub
        dataset = load_dataset(self.config.dataset_name)

        # Save it to disk so it can be reused offline
        dataset.save_to_disk(str(self.config.save_path))

        logger.info(f"Dataset '{self.config.dataset_name}' downloaded and saved to {self.config.save_path}")
