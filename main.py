import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkcalendar import Calendar
from PIL import Image, ImageTk
import pandas as pd
from data_upload import DataUpload
from data_Preprocessing import DataPreprocessing
from data_filtering import DataFiltering
from data_Visualisation_plots import DataVisualisation
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.backends.backend_pdf import PdfPages
import pygame
import threading


class UkuleleTuesdayProgram:
    def __init__(self, root):
        self.root = root
        self.root.title("Ukulele Tuesday Data Analysis Program")
        self.root.geometry("800x600")
        self.root.configure(bg="#FFCC99")  # Set consistent theme color
        pygame.mixer.init()
        self.volume_level = 50
        self.play_background_music("music.mp3")
        # Initialize modules
        self.data_uploader = DataUpload()
        self.data_preprocessor = DataPreprocessing()
        self.data_filterer = DataFiltering()
        self.data_visualiser = DataVisualisation()

        # Initialize data
        self.tab_db = None
        self.play_db = None
        self.request_db = None
        self.combined_data = None
        self.generated_figures = []

        # Apply styles
        self.setup_styles()

        # Create Main Menu
        self.main_menu = None
        self.create_main_menu()
   
    def play_background_music(self, file_path):
        """Play background music using pygame."""
        def play_music():
            try:
                
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.play(-1)
                pygame.mixer.music.set_volume(self.volume_level / 100)  # Loop music indefinitely
            except Exception as e:
                print(f"Error playing music: {e}")

        # Run music in a background thread
        music_thread = threading.Thread(target=play_music, daemon=True)
        music_thread.start()
    
    def set_volume(self, volume):
        """Set the volume of the background music."""
        self.volume_level = float(volume)
        pygame.mixer.music.set_volume(self.volume_level / 100)  # Scale slider value to 0-1

    def setup_styles(self):
        """Configure styles for ttk widgets."""
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        style.configure('TButton', font=('Helvetica', 12), padding=10, background="#FF9933", foreground="white")
        style.configure('TLabel', font=('Helvetica', 14), background="#FFCC99", foreground="#333333")
        style.configure('TFrame', background="#FFCC99")

    def create_main_menu(self):
        """Creates the main menu UI."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.main_menu = ttk.Frame(self.root, style='TFrame')
        self.main_menu.pack(pady=20, fill="both", expand=True)
        
        ttk.Label(self.main_menu, text="Music Volume", font=("Helvetica", 12)).pack(pady=10)
        volume_slider = ttk.Scale(
            self.main_menu, from_=0, to=100, orient="horizontal",
            command=self.set_volume
        )
        volume_slider.pack(pady=5)
        
        # Set slider position and synchronize the music volume
        self.set_volume(self.volume_level)   # Synchronize volume
        volume_slider.set(self.volume_level)

        # Add header image
        try:
            img = Image.open("icon.png").resize((200, 100))  # Replace with your image path
            header_image = ImageTk.PhotoImage(img)
            header_label = tk.Label(self.main_menu, image=header_image, bg="#FFCC99")
            header_label.image = header_image  # Keep reference
            header_label.pack(pady=10)
        except Exception:
            pass  # If image loading fails, just skip

        tk.Label(self.main_menu, text="Ukulele Tuesday Data Analysis", font=("Helvetica", 18), bg="#FFCC99", fg="black").pack(pady=10)

        ttk.Button(self.main_menu, text="Upload Data", command=self.open_upload_window).pack(pady=5)
        ttk.Button(self.main_menu, text="Data Query", command=self.open_query_window).pack(pady=5)
        ttk.Button(self.main_menu, text="Generate Visualizations", command=self.open_visualisation_window).pack(pady=5)
        ttk.Button(self.main_menu, text="Exit", command=self.root.quit).pack(pady=5)

    def open_upload_window(self):
        """Window for uploading data."""
        self.main_menu.destroy()
        upload_window = tk.Frame(self.root, bg="#FFCC99")
        upload_window.pack(pady=20)

        tk.Label(upload_window, text="Upload Data Files", font=("Helvetica", 16), bg="#FFCC99", fg="black").pack(pady=10)

        def upload_tabdb():
            file_path = filedialog.askopenfilename(title="Select tabdb.csv")
            if file_path:
                try:
                    # Check if the file name matches 'tabdb.csv'
                    if not file_path.endswith("tabdb.csv"):
                        messagebox.showerror("Error", "Invalid file. Please upload the correct tabdb.csv file.")
                        return
                    self.tab_db = self.data_uploader.load_csv(file_path, required_columns=[
                        'song', 'artist', 'year', 'type', 'gender', 'duration',
                        'language', 'source', 'date', 'difficulty', 'specialbooks'
                    ])
                    if self.tab_db is not None:
                        # Rename columns after successful validation
                        column_renames = {
                            'specialbooks': 'special books',
                            'gender': 'type_of_performer'
                        }
                        self.tab_db = self.data_uploader.ensure_consistent_columns(self.tab_db, column_renames)
                        messagebox.showinfo("Success", "tabdb.csv loaded successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading file: {e}")

        def upload_playdb():
            file_path = filedialog.askopenfilename(title="Select playdb.csv")
            if file_path:
                try:
                    # Check if the file name matches 'playdb.csv'
                    if not file_path.endswith("playdb.csv"):
                        messagebox.showerror("Error", "Invalid file. Please upload the correct playdb.csv file.")
                        return
                    self.play_db = self.data_uploader.load_csv(file_path, required_columns=['song', 'artist'])
                    if self.play_db is not None:
                        messagebox.showinfo("Success", "playdb.csv loaded successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading file: {e}")

        def upload_requestdb():
            file_path = filedialog.askopenfilename(title="Select requestdb.csv")
            if file_path:
                try:
                    # Check if the file name matches 'requestdb.csv'
                    if not file_path.endswith("requestdb.csv"):
                        messagebox.showerror("Error", "Invalid file. Please upload the correct requestdb.csv file.")
                        return
                    self.request_db = self.data_uploader.load_csv(file_path, required_columns=['song', 'artist'])
                    if self.request_db is not None:
                        messagebox.showinfo("Success", "requestdb.csv loaded successfully.")
                except Exception as e:
                    messagebox.showerror("Error", f"Error loading file: {e}")

        ttk.Button(upload_window, text="Upload tabdb.csv", command=upload_tabdb).pack(pady=5)
        ttk.Button(upload_window, text="Upload playdb.csv", command=upload_playdb).pack(pady=5)
        ttk.Button(upload_window, text="Upload requestdb.csv", command=upload_requestdb).pack(pady=5)

        def validate_and_clean_data():
            """Validate uploaded files, preprocess the data, and export the cleaned CSV."""
            if self.tab_db is not None and self.play_db is not None and self.request_db is not None:
                try:
                    # Combine and preprocess the data
                    self.combined_data = self.data_preprocessor.preprocess_for_analysis(
                        tab_db=self.tab_db, play_db=self.play_db, request_db=self.request_db)

                    # Apply additional data cleaning on the combined dataset
                    self.combined_data = self.data_preprocessor.clean_data(self.combined_data)

                    # Export the combined and cleaned data
                    if self.combined_data is not None:
                        self.combined_data.to_csv('combined_data_cleaned.csv', index=False)
                        messagebox.showinfo("Success", "Data files successfully cleaned and combined. Exported to combined_data_cleaned.csv.")

                        # Save combined dataset to CSV
                        self.combined_data.to_csv('combined_dataset.csv', index=False)
                        messagebox.showinfo("Success", "Combined dataset saved to combined_dataset.csv.")
                    else:
                        messagebox.showerror("Error", "Preprocessing failed. Check your data files.")
                except Exception as e:
                    messagebox.showerror("Error", f"An error occurred during preprocessing: {e}")
            else:
                messagebox.showerror("Error", "Please upload all three data files before validating.")
                
        ttk.Button(upload_window, text="Validate and Preprocess Data", command=validate_and_clean_data).pack(pady=10)
        ttk.Button(upload_window, text="Back to Main Menu", command=lambda: [upload_window.destroy(), self.create_main_menu()]).pack(pady=5)

    def open_query_window(self):
        """Tkinter window for data query with proper center alignment, even on fullscreen."""
        self.main_menu.destroy()  # Hide main menu

        # Create the query window container
        query_window = tk.Frame(self.root, bg="#FFCC99")
        query_window.pack(expand=True, fill="both")

        if self.combined_data is None:
            messagebox.showerror("Error", "No data available. Please upload and preprocess data first.")
            self.create_main_menu()  # Return to main menu
            return

        # Scrollable Canvas Setup
        canvas = tk.Canvas(query_window, bg="#FFCC99", highlightthickness=0)
        scrollbar = ttk.Scrollbar(query_window, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#FFCC99")

        def update_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(window_id, width=canvas_width)

        # Bind the canvas to update dynamically
        canvas.bind("<Configure>", update_canvas_width)

        # Create the scrollable window
        window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

        # Configure scrollable frame to update scroll region
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", expand=True, fill="both")
        scrollbar.pack(side="right", fill="y")

        # Center container within scrollable_frame
        container = tk.Frame(scrollable_frame, bg="#FFCC99")
        container.grid(row=0, column=0, padx=20, pady=20)
        scrollable_frame.grid_columnconfigure(0, weight=1)

        # Add content to container with proper alignment
        tk.Label(container, text="Select Date Range for Query", font=("Helvetica", 16), bg="#FFCC99", fg="black").pack(pady=20)

        # Date selection container
        date_container = tk.Frame(container, bg="#FFCC99")
        date_container.pack(pady=10)

        # Start Date
        tk.Label(date_container, text="Start Date", font=("Helvetica", 12), bg="#FFCC99", fg="black").grid(row=0, column=0, padx=10, pady=5)
        start_calendar = Calendar(date_container)
        start_calendar.grid(row=1, column=0, padx=10)

        # End Date
        tk.Label(date_container, text="End Date", font=("Helvetica", 12), bg="#FFCC99", fg="black").grid(row=0, column=1, padx=10, pady=5)
        end_calendar = Calendar(date_container)
        end_calendar.grid(row=1, column=1, padx=10)
        
        # Columns selection
        ttk.Label(container, text="Select Columns for Query:", style='TLabel').pack(pady=20)
        columns = [col for col in self.combined_data.columns if col != "tabber"]  # Exclude 'tabber' column
        selected_columns = {column: tk.IntVar() for column in columns}

        # Checkbox container
        column_container = tk.Frame(container, bg="#FFCC99")
        column_container.pack(pady=10)

        for column, var in selected_columns.items():
            tk.Checkbutton(column_container, text=column, variable=var, bg="#FFCC99", fg="black").pack(anchor="w")

        # Action buttons container
        button_container = tk.Frame(container, bg="#FFCC99")
        button_container.pack(pady=30)

        def perform_query(self):
            """Perform query based on selected columns and date range."""
            try:
                start_date = pd.to_datetime(self.start_calendar.get_date())
                end_date = pd.to_datetime(self.end_calendar.get_date())

                if 'dates' not in self.combined_data.columns:
                    messagebox.showerror("Error", "The combined data does not contain a 'dates' column.")
                    return

                # Filter by date range
                filtered_data = self.combined_data[
                    (self.combined_data['dates'] >= start_date) & (self.combined_data['dates'] <= end_date)
                ]

                # Get selected columns
                selected_cols = [col for col, var in self.selected_columns.items() if var.get() == 1]
                if not selected_cols:
                    messagebox.showerror("Error", "Please select at least one column for query.")
                    return

                # Prepare DataFrame with selected columns and send to DataFiltering
                selected_df = filtered_data[selected_cols]
                filters = {}  # Add specific filtering conditions if required
                filtered_result = self.data_filterer.filter_data(selected_df, filters)

                # Update play_value column: set value to 1 where it's non-zero, otherwise 0
                if 'play_value' in filtered_result.columns:
                    filtered_result['play_value'] = filtered_result['play_value'].apply(lambda x: 1 if x != 0 else 0)

                # Add count column by grouping on 'song' and 'artist' and summing 'play_value'
                filtered_result['play_count'] = filtered_result.groupby(['song', 'artist'])['play_value'].transform('sum')

                # Drop duplicate rows for the final output (for readability)
                filtered_result = filtered_result.drop_duplicates(subset=['song', 'artist', 'dates'])

                # Store filtered result for saving as CSV
                self.query_result = filtered_result
                
                # Display the filtered result
                self.display_filtered_result(filtered_result)
                messagebox.showinfo("Success", "Query executed successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")

        # Save Query Result Button
        def save_query_result():
            """Save the query result to a CSV file."""
            if hasattr(self, 'query_result') and self.query_result is not None:
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv")],
                    title="Save Query Result as CSV"
                )
                if file_path:
                    self.query_result.to_csv(file_path, index=False)
                    messagebox.showinfo("Success", f"Query result saved to {file_path}")
            else:
                messagebox.showerror("Error", "No query result available to save.")

        ttk.Button(button_container, text="Perform Query", command=perform_query).pack(side="left", padx=10)
        ttk.Button(button_container, text="Save Query Result to CSV", command=save_query_result).pack(side="left", padx=10)
        ttk.Button(button_container, text="Back to Main Menu",
                command=lambda: [query_window.destroy(), self.create_main_menu()]
                ).pack(side="left", padx=10)

    def display_filtered_result(self, df):
        """Display the filtered result in a new window."""
        result_window = tk.Toplevel(self.root)
        result_window.title("Query Results")
        result_window.geometry("1000x600")

        tree = ttk.Treeview(result_window, columns=list(df.columns), show='headings')
        tree.pack(expand=True, fill='both')

        # Add columns to the Treeview
        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='center')

        # Add rows to the Treeview
        for _, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        ttk.Button(result_window, text="Close", command=result_window.destroy).pack(pady=10)

    def open_visualisation_window(self):
        """Window for generating visualizations with Basic and Advanced options."""
        self.main_menu.destroy()
        vis_window = tk.Frame(self.root, bg="#FFCC99")
        vis_window.pack(pady=20)

        if self.combined_data is None:
            messagebox.showerror("Error", "No data available for visualization. Please upload and preprocess data first.")
            vis_window.destroy()
            self.create_main_menu()
            return

        # Heading for the visualization window
        ttk.Label(vis_window, text="Please choose type of visualisation", font=("Helvetica", 16)).pack(pady=10)
        
        def configure_frame(frame):
            frame.configure(bg="#FFCC99")  # Set frame background
            for widget in frame.winfo_children():
                widget.configure(bg="#FFCC99")  # Update child widgets

        basic_frame = tk.Frame(vis_window, bg="#FFCC99")
        advanced_frame = tk.Frame(vis_window, bg="#FFCC99")

        # Frames for Basic and Advanced Charts
        #basic_frame = tk.Frame(vis_window)
        #advanced_frame = tk.Frame(vis_window)

        def show_basic_charts():
            advanced_frame.pack_forget()
            basic_frame.pack(pady=20, fill="both")
            create_basic_chart_options(basic_frame)

        def show_advanced_charts():
            basic_frame.pack_forget()
            advanced_frame.pack(pady=20, fill="both")
            create_advanced_chart_options(advanced_frame)

        ttk.Button(vis_window, text="Basic Charts (7 basic charts)", command=show_basic_charts).pack(pady=5)
        ttk.Button(vis_window, text="Advanced Charts (Choose your own charts)", command=show_advanced_charts).pack(pady=5)
        # Add Save to PDF functionality
        def save_to_pdf():
            if not self.generated_figures:
                messagebox.showerror("Error", "No visualizations available to save.")
                return

            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")],
                title="Save Visualizations as PDF"
            )

            if file_path:
                with PdfPages(file_path) as pdf:
                    for fig in self.generated_figures:
                        pdf.savefig(fig)
                messagebox.showinfo("Success", f"Visualizations saved to {file_path}")

        # Add Save to PDF button
        ttk.Button(vis_window, text="Save to PDF", command=save_to_pdf).pack(pady=10)

        # Clear previous figures
        self.generated_figures.clear()
        # Function to create basic chart options
        def create_basic_chart_options(frame):
            for widget in frame.winfo_children():
                widget.destroy()

            ttk.Label(frame, text="Select Visualizations to Generate", font=("Helvetica", 14)).pack(pady=10)

            style = ttk.Style()
            style.configure("TCheckbutton", background="#FFCC99")  # Match the background color

            visualizations = [
                ("Histogram of Songs by Difficulty Level", lambda fig: self.data_visualiser.plot_histogram(self.combined_data, 'difficulty', "Histogram of Songs by Difficulty Level", fig)),
                ("Histogram of Songs by Duration", lambda fig: self.data_visualiser.plot_histogram(self.combined_data, 'duration', "Histogram of Songs by Duration", fig)),
                ("Bar Chart of Songs by Language", lambda fig: self.data_visualiser.plot_bar_chart(self.combined_data, 'language', "Bar Chart of Songs by Language", fig)),
                ("Bar Chart of Songs by Source", lambda fig: self.data_visualiser.plot_bar_chart(self.combined_data, 'source', "Bar Chart of Songs by Source", fig)),
                ("Bar Chart of Songs by Decade", lambda fig: self.data_visualiser.plot_decade_bar(self.combined_data, fig)),
                ("Cumulative Line Chart of Songs Played Each Tuesday", lambda fig: self.data_visualiser.plot_cumulative_line(self.combined_data, fig)),
                ("Pie Chart of Songs by Type of Performer", lambda fig: self.data_visualiser.plot_pie_chart(self.combined_data, 'type_of_performer', "Pie Chart of Songs by Type of Performer", fig))
            ]

            selected_visualizations = {vis_name: tk.IntVar() for vis_name, _ in visualizations}

            for vis_name, _ in visualizations:
                ttk.Checkbutton(frame, text=vis_name, variable=selected_visualizations[vis_name]).pack(anchor="w")

            # Function to toggle between graphs
            def toggle_graph(canvas, figure_container, figures, index_var):
                """Toggle to the next graph in the list."""
                if not figures:
                    return  # No figures to toggle
                index_var.set((index_var.get() + 1) % len(figures))  # Move to the next figure index
                fig = figures[index_var.get()]  # Get the current figure
                for widget in figure_container.winfo_children():
                    widget.destroy()  # Clear previous graph
                canvas = FigureCanvasTkAgg(fig, master=figure_container)
                canvas_widget = canvas.get_tk_widget()
                canvas_widget.pack(fill='both', expand=True)
                canvas.draw()

            # Updated perform_visualisation
            def perform_visualisation():
                self.generated_figures.clear()  # Clear previous figures
                for vis_name, vis_function in visualizations:
                    if selected_visualizations[vis_name].get():
                        try:
                            fig = plt.figure()
                            vis_function(fig)
                            self.generated_figures.append(fig)
                        except Exception as e:
                            messagebox.showerror("Error", f"Could not generate {vis_name}: {e}")

                if not self.generated_figures:
                    messagebox.showinfo("Info", "No visualizations selected.")
                    return

                # Open a new window to display all figures
                vis_window = tk.Toplevel(self.root)
                vis_window.title("Generated Visualizations")
                vis_window.geometry("800x600")

                figure_container = tk.Frame(vis_window, bg="#FFCC99")
                figure_container.pack(fill="both", expand=True)

                # Variable to track the current figure index
                current_figure_index = tk.IntVar(value=0)

                # Display the first figure
                if self.generated_figures:
                    fig = self.generated_figures[current_figure_index.get()]
                    canvas = FigureCanvasTkAgg(fig, master=figure_container)
                    canvas_widget = canvas.get_tk_widget()
                    canvas_widget.pack(fill='both', expand=True)
                    canvas.draw()

                # Add Next Graph button
                next_button = ttk.Button(
                    vis_window,
                    text="Next Graph",
                    command=lambda: toggle_graph(canvas, figure_container, self.generated_figures, current_figure_index)
                )
                next_button.pack(pady=10)


            #def perform_visualisation():
            #    self.generated_figures.clear()
            #    for vis_name, vis_function in visualizations:
            #        if selected_visualizations[vis_name].get():
            #            try:
            #                fig = plt.figure()
            #                vis_function(fig)
            #                self.generated_figures.append(fig)
            #                plt.show()
            #            except Exception as e:
            #                messagebox.showerror("Error", f"Could not generate {vis_name}: {e}")

            ttk.Button(frame, text="Generate Visualizations", command=perform_visualisation).pack(pady=10)

        # Function to create advanced chart options
        def create_advanced_chart_options(frame):
            for widget in frame.winfo_children():
                widget.destroy()

            ttk.Label(frame, text="Advanced Chart Options", font=("Helvetica", 14)).pack(pady=10)

            categorical_columns = ['type', 'type_of_performer', 'language', 'source', 'Category']
            group_by_var = tk.StringVar()

            ttk.Label(frame, text="Group Data By (Categorical Column):").pack()
            group_by_dropdown = ttk.Combobox(frame, textvariable=group_by_var, values=categorical_columns)
            group_by_dropdown.pack(pady=5)

            chart_type = tk.StringVar()
            ttk.Label(frame, text="Select Chart Type:").pack()
            chart_type_dropdown = ttk.Combobox(frame, textvariable=chart_type, values=["Bar Chart", "Pie Chart", "Line Chart"])
            chart_type_dropdown.pack(pady=5)

            def generate_grouped_chart():
                group_by = group_by_var.get()
                chart = chart_type.get()
                if not group_by or not chart:
                    messagebox.showerror("Error", "Please select both grouping column and chart type.")
                    return

                try:
                    fig = plt.figure()
                    if chart == "Bar Chart":
                        self.data_visualiser.plot_bar_chart(self.combined_data, group_by, f"{chart} by {group_by}", fig)
                    elif chart == "Pie Chart":
                        self.data_visualiser.plot_pie_chart(self.combined_data, group_by, f"{chart} by {group_by}", fig)
                    elif chart == "Line Chart":
                        self.data_visualiser.plot_cumulative_line(self.combined_data, fig)
                    self.generated_figures.append(fig)
                    plt.show()
                except Exception as e:
                    messagebox.showerror("Error", f"Error generating {chart}: {e}")

            ttk.Button(frame, text="Generate Chart", command=generate_grouped_chart).pack(pady=10)

        ttk.Button(vis_window, text="Back to Main Menu", command=lambda: [vis_window.destroy(), self.create_main_menu()]).pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = UkuleleTuesdayProgram(root)
    root.mainloop()

