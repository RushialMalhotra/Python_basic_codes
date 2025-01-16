import pandas as pd
import logging

class DataPreprocessing:
    def __init__(self):
        pass

    def clean_data(self, df):
        """Clean the input dataframe."""
        replace_dict = {
            'A': 'Audience', 'A.': 'Audience', 'S': 'Audience', 'P': 'Audience',
            'G': 'Group', 'Group': 'Group', '?': 'Unknown', 'nan': 'Unknown'
        }

        # Rename 'request_value' to 'requested_by' and replace values accordingly
        if 'request_value' in df.columns:
            df.rename(columns={'request_value': 'requested_by'}, inplace=True)
            df['requested_by'] = df['requested_by'].replace(replace_dict)
            logging.info("Renamed 'request_value' to 'requested_by' and updated labels.")
        
        if 'date' in df.columns:
            try:
                # Rename the column
                df.rename(columns={'date': 'first_play_date'}, inplace=True)
                logging.info("Renamed 'date' to 'first_play_date'.")

                # Handle blanks and ensure proper conversion
                df['first_play_date'] = df['first_play_date'].replace(' ', None)  # Replace blanks with None/NaN
                df['first_play_date'] = pd.to_datetime(
                    df['first_play_date'], 
                    format='%Y%m%d', 
                    errors='coerce'  # Coerce invalid formats to NaT
                )
                df.dropna(subset=['first_play_date'], inplace=True)  # Remove rows with NaT (invalid dates)
                
                df['first_play_date'] = df['first_play_date'].dt.date
                logging.info("Converted 'first_play_date' to date-only format successfully.")
            except Exception as e:
                logging.error(f"Error processing 'first_play_date': {e}")

    # Replace audience type codes with descriptive labels
        if 'audience_type' in df.columns:
            df['audience_type'] = df['audience_type'].replace(replace_dict)
            logging.info("Replaced 'audience_type' codes with proper labels.")

        # Handle dynamic date columns
        date_columns = [col for col in df.columns if col.isdigit()]
        for col in date_columns:
            if col in df.columns:
            # Ensure consistent formatting and remove whitespace
                df[col] = df[col].astype(str).str.strip()
                df[col] = df[col].replace(replace_dict)
                logging.info(f"Replaced values in date column '{col}' using replace_dict.")

        return df

        # Replace type column values
        if 'type' in df.columns:
            df['type'] = df['type'].replace(replace_dict)
            logging.info("Replaced 'type' column codes with proper labels.")

        # Rename 'gender' to 'type_of_performer'
        if 'gender' in df.columns:
            df.rename(columns={'gender': 'type_of_performer'}, inplace=True)
            logging.info("Renamed 'gender' to 'type_of_performer'.")

        

        # Drop unnecessary columns
        unnecessary_columns = ['tabber', 'extra_column']
        columns_to_drop = [col for col in unnecessary_columns if col in df.columns]
        if columns_to_drop:
            df.drop(columns=columns_to_drop, inplace=True)
            logging.info(f"Dropped unnecessary columns: {columns_to_drop}")

        # Ensure numeric columns have proper data types
        numeric_columns = df.select_dtypes(include=['number']).columns
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            logging.info(f"Cleaned numeric data in column '{col}'.")

        # Convert duration from string to seconds for easier analysis
        #if 'duration' in df.columns:
            #try:
                # Convert to seconds
                #df['duration_seconds'] = pd.to_timedelta(df['duration'], errors='coerce').dt.total_seconds()
                #df.dropna(subset=['duration_seconds'], inplace=True)  # Drop rows with invalid durations
                #logging.info("Successfully converted 'duration' to 'duration_seconds'.")
            #except Exception as e:
                #logging.error(f"Error converting 'duration' to 'duration_seconds': {e}")


        # Convert ratings column to whole number scale of 5
        if 'difficulty' in df.columns:
            df['difficulty'] = df['difficulty'].round().clip(lower=1, upper=5)
            logging.info("Rounded 'difficulty' to nearest whole number on a scale of 5.")

        # Split columns into multiple rows based on delimiter
        for col in ['language', 'specialbooks']:
            if col in df.columns:
                df = df.drop(col, axis=1).join(df[col].str.split(',', expand=True).stack()
                                              .reset_index(level=1, drop=True).rename(col)).reset_index(drop=True)
                logging.info(f"Split '{col}' column into multiple rows based on delimiter.")

        # Drop duplicates and fill missing values
        original_count = len(df)
        df.drop_duplicates(inplace=True)
        logging.info(f"Dropped {original_count - len(df)} duplicate rows.")

        df.fillna('Unknown', inplace=True)
        logging.info("Filled missing values with 'Unknown'.")

        # Ensure 'dates' column is in datetime format
        if 'dates' in df.columns:
            df['dates'] = pd.to_datetime(df['dates'], errors='coerce')
            df.dropna(subset=['dates'], inplace=True)
            logging.info("Converted 'dates' column to datetime and removed invalid entries.")

        return df

        
        
        
    def preprocess_for_analysis(self, play_db, request_db, tab_db):
        """
        Preprocess the data for analysis by cleaning and merging datasets.

        :param play_db: DataFrame for play database.
        :param request_db: DataFrame for request database.
        :param tab_db: DataFrame for tab database.
        :return: Combined and cleaned DataFrame ready for analysis.
        """
        # Clean individual datasets
        play_db = self.clean_data(play_db)
        request_db = self.clean_data(request_db)
        tab_db = self.clean_data(tab_db)

        # Melt datasets to create a 'dates' column
        play_db_melted = self._reshape_db(play_db, 'play')
        request_db_melted = self._reshape_db(request_db, 'requested')

        # Merge play_db and request_db on song, artist, and dates
        combined_play_request = pd.merge(
            play_db_melted, request_db_melted, on=['song', 'artist', 'dates'], how='outer'
        )
        logging.info("Combined play and request datasets.")

        # Merge the combined play/request data with tab_db
        combined_data = pd.merge(
            combined_play_request, tab_db, on=['song', 'artist'], how='left'
        )
        logging.info("Merged combined play/request dataset with tab data.")

        # Add additional features for visualization
        if 'year' in combined_data.columns:
            combined_data['year'] = combined_data['year'].astype('Int64')
            combined_data['decade'] = (combined_data['year'] // 10) * 10
            logging.info("Converted 'year' to integer and added 'decade' column based on 'year'.")

        return combined_data


    def _reshape_db(self, db, db_name):
        """Reshapes the play or request database for merging."""
        melted_db = pd.melt(db, id_vars=['song', 'artist'], var_name='dates', value_name=f'{db_name}_value')
        melted_db.dropna(subset=['dates'], inplace=True)
        melted_db['dates'] = pd.to_datetime(melted_db['dates'], format='%Y%m%d', errors='coerce')
        melted_db.dropna(subset=['dates'], inplace=True)
        logging.info(f"Reshaped '{db_name}' dataset for merging.")
        return melted_db

