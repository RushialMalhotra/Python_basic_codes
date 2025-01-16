import pandas as pd
import logging

class DataFiltering:
    def __init__(self):
        pass

    def filter_data(self, df, filters=None, date_range=None):
        """
        Filters the data based on column values and an optional date range.

        :param df: DataFrame to filter.
        :param filters: Dictionary with column names as keys and values to filter by.
        :param date_range: Tuple containing start and end dates for filtering.
        :return: Filtered DataFrame.
        """
        # Apply column filters
        if filters:
            for col, value in filters.items():
                if col in df.columns:
                    df = df[df[col] == value]
                    logging.info(f"Filtered data by {col} == {value}.")

        # Apply date range filter
        if date_range:
            start_date, end_date = date_range
            if 'dates' in df.columns:
                df = df[(df['dates'] >= start_date) & (df['dates'] <= end_date)]
                logging.info(f"Filtered data between dates {start_date} and {end_date}.")

        return df

    def remove_outliers(self, df, columns, z_threshold=3):
        """
        Removes outliers from specified columns using Z-score method.

        :param df: DataFrame from which to remove outliers.
        :param columns: List of column names to check for outliers.
        :param z_threshold: Z-score threshold for identifying outliers.
        :return: DataFrame without outliers in specified columns.
        """
        from scipy import stats
        for col in columns:
            if col in df.columns:
                df['z_score'] = stats.zscore(df[col])
                df = df[df['z_score'].abs() <= z_threshold]
                df.drop(columns=['z_score'], inplace=True)
                logging.info(f"Removed outliers in column '{col}' using Z-score method with threshold {z_threshold}.")
        return df

    def create_flags(self, df):
        """
        Creates additional flags to help with analysis, like popularity scores.

        :param df: DataFrame for which to create flags.
        :return: DataFrame with additional flags.
        """
        # Popularity flag based on play and request counts
        if 'play_value' in df.columns and 'request_value' in df.columns:
            df['popularity_score'] = df['play_value'].fillna(0) + df['request_value'].fillna(0)
            df['is_popular'] = df['popularity_score'] > df['popularity_score'].mean()
            logging.info("Created 'popularity_score' and 'is_popular' columns based on play and request data.")
        return df

    def filter_popular_songs(self, df, min_popularity_score=None):
        """
        Filters songs that are popular based on a minimum popularity score.

        :param df: DataFrame to filter.
        :param min_popularity_score: Minimum score to consider a song popular.
        :return: Filtered DataFrame with only popular songs.
        """
        if 'popularity_score' in df.columns:
            if min_popularity_score is None:
                min_popularity_score = df['popularity_score'].mean()
            df = df[df['popularity_score'] >= min_popularity_score]
            logging.info(f"Filtered popular songs with popularity score >= {min_popularity_score}.")
        else:
            logging.warning("'popularity_score' column not found. Please create flags before filtering popular songs.")
        return df

    def remove_null_values(self, df, columns=None):
        """
        Removes rows with null values in specified columns.

        :param df: DataFrame from which to remove null values.
        :param columns: List of column names to check for null values. If None, all columns are checked.
        :return: DataFrame without null values in specified columns.
        """
        if columns is None:
            columns = df.columns
        original_count = len(df)
        df.dropna(subset=columns, inplace=True)
        logging.info(f"Removed {original_count - len(df)} rows with null values in columns {columns}.")
        return df

    def fill_missing_values(self, df, fill_values):
        """
        Fills missing values in specified columns with provided values.

        :param df: DataFrame in which to fill missing values.
        :param fill_values: Dictionary with column names as keys and fill values as values.
        :return: DataFrame with filled missing values.
        """
        for col, value in fill_values.items():
            if col in df.columns:
                df[col].fillna(value, inplace=True)
                logging.info(f"Filled missing values in column '{col}' with '{value}'.")
        return df

    def standardize_text_columns(self, df, columns):
        """
        Standardizes text columns by converting to lowercase and stripping whitespace.

        :param df: DataFrame with text columns to standardize.
        :param columns: List of column names to standardize.
        :return: DataFrame with standardized text columns.
        """
        for col in columns:
            if col in df.columns:
                df[col] = df[col].str.lower().str.strip()
                logging.info(f"Standardized text in column '{col}'.")
        return df

    def remove_duplicates(self, df, subset=None):
        """
        Removes duplicate rows from the DataFrame.

        :param df: DataFrame from which to remove duplicates.
        :param subset: Columns to consider when identifying duplicates. If None, all columns are considered.
        :return: DataFrame without duplicate rows.
        """
        original_count = len(df)
        df.drop_duplicates(subset=subset, inplace=True)
        logging.info(f"Removed {original_count - len(df)} duplicate rows based on columns {subset if subset else 'all columns'}.")
        return df
