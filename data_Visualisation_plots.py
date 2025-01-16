import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

class DataVisualisation:
    def plot_histogram(self, df, column, title, fig):
        """Plots a histogram."""
        if column in df.columns:
            plt.figure(fig.number)  # Set the current figure
            sns.histplot(df[column].dropna(), bins=10, color='skyblue', edgecolor='black')
            plt.title(title)
            plt.xlabel(column)
            plt.ylabel('Frequency')
            plt.xticks(rotation=90)
        else:
            print(f"Error: Column '{column}' not found in DataFrame.")

    def plot_bar_chart(self, df, column, title, fig):
        """Plots a bar chart."""
        if column in df.columns:
            plt.figure(fig.number)  # Set the current figure
            sns.countplot(x=column, data=df, color='skyblue', edgecolor='black')
            plt.title(title)
            plt.xlabel(column)
            plt.ylabel('Count')
            plt.xticks(rotation=90)
        else:
            print(f"Error: Column '{column}' not found in DataFrame.")

    def plot_pie_chart(self, df, column, title, fig):
        """Plots a pie chart."""
        if column in df.columns:
            plt.figure(fig.number)  # Set the current figure
            df[column].value_counts().plot(kind='pie', autopct='%1.1f%%', startangle=90)
            plt.title(title)
            plt.ylabel('')  # Hide y-axis label for pie charts
        else:
            print(f"Error: Column '{column}' not found in DataFrame.")

    def plot_decade_bar(self, df, fig):
        """Plots a bar chart of songs by decade."""
        if 'year' in df.columns:
            plt.figure(fig.number)  # Set the current figure
            df['decade'] = (df['year'] // 10) * 10
            df['decade'] = df['decade'].fillna('Unknown')
            df['decade'].value_counts().sort_index().plot(kind='bar', title='Songs by Decade')
            plt.xlabel('Decade')
            plt.ylabel('Count')
            plt.xticks(rotation=90)
        else:
            print(f"Error: Column 'year' not found in DataFrame.")

    def plot_cumulative_line(self, df, fig):
        """Plots a cumulative line chart of songs played."""
        if 'dates' in df.columns:
            plt.figure(fig.number)  # Set the current figure
            df['week'] = df['dates'].dt.to_period('W')
            weekly_counts = df.groupby('week').size()
            weekly_counts.cumsum().plot(kind='line', title='Cumulative Songs Played')
            plt.xlabel('Week')
            plt.ylabel('Cumulative Songs Played')
            plt.xticks(rotation=90)
        else:
            print(f"Error: Column 'dates' not found in DataFrame.")

    def plot_grouped_bar_chart(self, df, categorical_column, group_column, title, fig):
        """Plots a grouped bar chart."""
        if categorical_column in df.columns and group_column in df.columns:
            plt.figure(fig.number)  # Set the current figure
            grouped = df.groupby([group_column, categorical_column]).size().unstack(fill_value=0)
            grouped.plot(kind="bar", stacked=True, figsize=(10, 6), title=title)
            plt.xlabel(group_column)
            plt.ylabel('Count')
            plt.xticks(rotation=90)
        else:
            print(f"Error: Columns '{categorical_column}' or '{group_column}' not found in DataFrame.")
