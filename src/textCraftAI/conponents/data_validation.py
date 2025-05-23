import os
from textCraftAI.logging import logger
from textCraftAI.entity.config_entity import DataValidationConfig


class DataValidation:
    def __init__(self, config: DataValidationConfig):
        self.config = config

    def validate_all_files_exist(self) -> bool:
        try:
            dataset_path = os.path.join("artifacts", "data_ingestion", "dialogsum_dataset")
            present_files = os.listdir(dataset_path)

            missing_files = [
                required for required in self.config.ALL_REQUIRED_FILES
                if required not in present_files
            ]

            validation_status = len(missing_files) == 0

            with open(self.config.STATUS_FILE, 'w') as f:
                if validation_status:
                    f.write("Validation status: True\nAll required files are present.")
                else:
                    f.write(f"Validation status: False\nMissing files: {missing_files}")

            logger.info(f"Data validation status: {validation_status}")
            return validation_status

        except Exception as e:
            raise e
