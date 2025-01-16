import os
import pandas as pd
import logging
from tkinter import messagebox

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class DataUpload:
    """
    This class is responsible for loading CSV files and ensuring proper structure.
    """
    def load_csv(self, file_path, required_columns):
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)

                # Check for required columns before renaming
                missing_columns = [col for col in required_columns if col not in df.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")
                
                # Log successful validation
                logging.info(f"{file_path} contains all required columns.")
                return df
            except Exception as e:
                logging.error(f"Error loading {file_path}: {e}")
                messagebox.showerror("Error", f"Error loading file: {e}")
                return None
        else:
            logging.error(f"File {file_path} not found.")
            messagebox.showerror("Error", f"File not found: {file_path}")
            return None

    def ensure_consistent_columns(self, df, column_renames):
        """
        This method ensures the given DataFrame has consistent column naming as per requirements.
        
        :param df: DataFrame to check.
        :param column_renames: A dictionary of columns to rename for consistency.
        """
        for old_name, new_name in column_renames.items():
            if old_name in df.columns:
                df.rename(columns={old_name: new_name}, inplace=True)
                logging.info(f"Renamed column '{old_name}' to '{new_name}' for consistency.")
        return df

    def load_and_prepare_csv(self, file_path, required_columns, column_renames):
        """
        Load and rename columns of a CSV file to make sure consistency is maintained.
        
        :param file_path: Path of the file to be loaded.
        :param required_columns: Required columns that the CSV file must contain.
        :param column_renames: Columns that need to be renamed.
        :return: Cleaned DataFrame or None if there is an issue.
        """
        df = self.load_csv(file_path, required_columns)
        if df is not None:
            df = self.ensure_consistent_columns(df, column_renames)
        return df
