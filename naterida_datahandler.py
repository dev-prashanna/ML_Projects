import tkinter as tk
from tkinter import Frame, Label, Button, filedialog, ttk
import requests
import pandas as pd
import time
from datetime import datetime
import logging
import threading
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np  # For mean, median, and standard deviation calculations
from statsmodels.tsa.arima.model import ARIMA
import seaborn as sns

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SensorInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sensor Interface")
        self.root.geometry("1000x600")
        self.root.configure(bg="black")

        # Outer Frame for black border effect
        outer_frame = Frame(self.root, bg="black", padx=3, pady=3)
        outer_frame.pack(fill="both", expand=True)

        # Main Frame with a light blue background
        self.main_frame = Frame(outer_frame, bg="#87CEEB")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # IP Address Input Section
        self.ip_frame = Frame(self.main_frame, bg="#87CEEB")
        self.ip_frame.pack(fill="x", padx=10, pady=10)

        Label(self.ip_frame, text="ESP32 IP Address:", bg="#87CEEB").pack(side="left", padx=5)
        self.ip_entry = tk.Entry(self.ip_frame, width=20)
        self.ip_entry.insert(0, "192.168.1.80")  # Default IP address
        self.ip_entry.pack(side="left", padx=5)

        # Top Section (Sensor Data)
        top_frame = Frame(self.main_frame, bg="#87CEEB")
        top_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Live Sensor Value Section
        sensor_frame = Frame(top_frame, bg="black", width=850, height=400)
        sensor_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)

        sensor_label = Label(sensor_frame, text="LIVE SENSOR VALUES", font=("Arial", 14, "bold"), fg="black", bg="#87CEEB")
        sensor_label.pack(side="top", pady=5)

        # Treeview Table for Sensor Data
        self.columns = ["LIGHT INTENSITY", "GAS VALUE", "HUMIDITY", "TEMPERATURE", "PITCH", "ROLL", "YAW", "TIMESTAMP"]
        self.tree = ttk.Treeview(sensor_frame, columns=self.columns, show="headings", height=15)
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar for Table
        scrollbar = ttk.Scrollbar(sensor_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscroll=scrollbar.set)

        # Define Column Headings
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        # Bottom Section (Buttons)
        bottom_frame = Frame(self.main_frame, bg="#87CEEB")
        bottom_frame.pack(fill="x", padx=10, pady=10)

        # Style for Buttons
        style = ttk.Style()
        style.configure("TButton", width=12, font=("Arial", 10, "bold"), padding=6)
        style.map("TButton", background=[("active", "yellowgreen")])

        buttons = ["SAVE", "DELETE", "DATA ANALYST", "PLOT", "BOOKMARK", "FORECAST", "DATA SORTER"]
        self.button_refs = {}

        for btn_text in buttons:
            btn = ttk.Button(bottom_frame, text=btn_text, style="TButton")
            btn.pack(side="left", padx=10)
            self.button_refs[btn_text] = btn

        self.button_refs["SAVE"].config(command=self.save_file)
        self.button_refs["DELETE"].config(command=self.delete_data)
        self.button_refs["DATA ANALYST"].config(command=self.data_analyst_menu)
        self.button_refs["PLOT"].config(command=self.plot_menu)
        self.button_refs["FORECAST"].config(command=self.forecast_menu)
        self.button_refs["DATA SORTER"].config(command=self.data_sorter_menu)

        # Create an empty DataFrame to store sensor data
        self.data = pd.DataFrame(columns=self.columns)

        # Start the data fetching thread
        self.fetch_data_thread = threading.Thread(target=self.fetch_data_continuously, daemon=True)
        self.fetch_data_thread.start()

        self.root.mainloop()

    def save_file(self):
        """Save the current data to an Excel file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", 
                                                    filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")])
        if file_path:
            try:
                with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
                    self.data.to_excel(writer, index=False, sheet_name="Sensor Data")
                    workbook = writer.book
                    worksheet = writer.sheets["Sensor Data"]
                    for i, col in enumerate(self.data.columns):
                        max_length = max(self.data[col].astype(str).map(len).max(), len(col)) + 2
                        worksheet.set_column(i, i, max_length)
                logging.info(f"Data saved successfully to {file_path}")
            except Exception as e:
                logging.error(f"Error saving file: {e}")

    def delete_data(self):
        """Delete all entries from the tree view and reset the data DataFrame."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.data = pd.DataFrame(columns=self.columns)

    def data_sorter_menu(self):
        """Open a menu for sorting data based on sensor value range."""
        sorter_window = tk.Toplevel(self.root)
        sorter_window.title("Data Sorter")
        sorter_window.geometry("400x300")

        # Select Sensor
        Label(sorter_window, text="Select Sensor:").pack(pady=10)
        sensor_selection = ttk.Combobox(sorter_window, values=self.columns[:-1])  # Exclude TIMESTAMP
        sensor_selection.pack(pady=10)

        # Minimum Value
        Label(sorter_window, text="Min Value:").pack(pady=5)
        min_value_entry = tk.Entry(sorter_window)
        min_value_entry.pack(pady=5)

        # Maximum Value
        Label(sorter_window, text="Max Value:").pack(pady=5)
        max_value_entry = tk.Entry(sorter_window)
        max_value_entry.pack(pady=5)

        # Button to Filter Data
        Button(sorter_window, text="Filter Data", command=lambda: self.filter_data(sensor_selection.get(), min_value_entry.get(), max_value_entry.get())).pack(pady=20)

    def filter_data(self, sensor, min_value, max_value):
        """Filter data based on the selected sensor and value range."""
        try:
            min_value = float(min_value)
            max_value = float(max_value)
        except ValueError:
            logging.error("Invalid input for min or max value.")
            return

        filtered_data = self.data[(self.data[sensor] >= min_value) & (self.data[sensor] <= max_value)]

        if filtered_data.empty:
            logging.info("No data found in the specified range.")
            return
        
        self.show_filtered_data(filtered_data)

    def show_filtered_data(self, filtered_data):
        """Display the filtered data in a new window."""
        filtered_window = tk.Toplevel(self.root)
        filtered_window.title("Filtered Data")
        filtered_window.geometry("600x400")

        tree = ttk.Treeview(filtered_window, columns=self.columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Scrollbar for Filtered Data Table
        scrollbar = ttk.Scrollbar(filtered_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscroll=scrollbar.set)

        # Define Column Headings
        for col in self.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=120)

        # Insert filtered data into the Treeview
        for index, row in filtered_data.iterrows():
            tree.insert("", "end", values=list(row))

    def data_analyst_menu(self):
        """Open a menu for selecting a sensor for data analysis."""
        data_analyst_window = tk.Toplevel(self.root)
        data_analyst_window.title("Select Sensor for Data Analysis")
        data_analyst_window.geometry("300x200")

        Button(data_analyst_window, text="TEMPERATURE", width=20, height=2, command=lambda: self.show_data_analysis(data_analyst_window, "TEMPERATURE")).pack(pady=10)
        Button(data_analyst_window, text="HUMIDITY", width=20, height=2, command=lambda: self.show_data_analysis(data_analyst_window, "HUMIDITY")).pack(pady=10)
        Button(data_analyst_window, text="LIGHT INTENSITY", width=20, height=2, command=lambda: self.show_data_analysis(data_analyst_window, "LIGHT INTENSITY")).pack(pady=10)
        Button(data_analyst_window, text="GAS VALUE", width=20, height=2, command=lambda: self.show_data_analysis(data_analyst_window, "GAS VALUE")).pack(pady=10)

    def show_data_analysis(self, parent_window, sensor):
        """Display statistical analysis for the selected sensor."""
        sensor_data = self.data[sensor]
        mean = np.mean(sensor_data)
        median = np.median(sensor_data)
        std_dev = np.std(sensor_data)

        analysis_text = f"Mean: {mean:.2f}\nMedian: {median:.2f}\nStandard Deviation: {std_dev:.2f}"
        
        analysis_label = Label(parent_window, text=analysis_text, font=("Arial", 12), fg="black", bg="#87CEEB")
        analysis_label.pack(pady=10)

    def fetch_data_continuously(self):
        """Continuously fetch sensor data from the ESP32."""
        while True:
            esp32_url = self.ip_entry.get()
            sensor_data = self.fetch_sensor_data(f"http://{esp32_url}/getSensorData")
            if sensor_data:
                new_row = self.process_sensor_data(sensor_data)
                self.data.loc[len(self.data)] = new_row
                self.root.after(0, self.update_sensor_display, new_row)
            time.sleep(2)

    def fetch_sensor_data(self, url):
        """Fetch sensor data from the specified URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error("Error fetching data: %s", e)
            return None

    def process_sensor_data(self, sensor_data):
        """Process the raw sensor data and return it in a structured format."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Adjust timezone if needed
        return {
            "LIGHT INTENSITY": sensor_data["ldrValue"],
            "GAS VALUE": sensor_data["mq2Value"],
            "HUMIDITY": sensor_data["humidity"],
            "TEMPERATURE": sensor_data["temperature"],
            "PITCH": sensor_data["pitch"],
            "ROLL": sensor_data["roll"],
            "YAW": sensor_data["yaw"],
            "TIMESTAMP": timestamp,
        }

    def update_sensor_display(self, new_row):
        """Update the tree view with the latest sensor data."""
        self.tree.insert("", "end", values=list(new_row.values()))

    def plot_menu(self):
        """Open a menu to choose plotting options."""
        plot_window = tk.Toplevel(self.root)
        plot_window.title("Select Plot Type")
        plot_window.geometry("300x200")

        Button(plot_window, text="Live Graph Plotter", width=20, height=2, command=lambda: self.live_graph_plotter(plot_window)).pack(pady=10)
        Button(plot_window, text="Live Bar Chart", width=20, height=2, command=lambda: self.live_bar_chart(plot_window)).pack(pady=10)
        Button(plot_window, text="Sensor Heatmap", width=20, height=2, command=lambda: self.generate_heatmap(plot_window)).pack(pady=10)

    def live_graph_plotter(self, parent_window):
        """Create a live graph plotter for sensor data."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Live Graph Plotter")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Sensor Values")

        time_data = []
        gas_values = []
        ldr_values = []
        humidity_values = []
        temp_values = []

        def update_graph():
            """Update the graph with new data continuously."""
            while True:
                current_time = time.time()
                time_data.append(current_time)
                gas_values.append(self.data["GAS VALUE"].iloc[-1])
                ldr_values.append(self.data["LIGHT INTENSITY"].iloc[-1])
                humidity_values.append(self.data["HUMIDITY"].iloc[-1])
                temp_values.append(self.data["TEMPERATURE"].iloc[-1])

                ax.clear()
                ax.plot(time_data, gas_values, label="Gas Value", color="red")
                ax.plot(time_data, ldr_values, label="LDR", color="blue")
                ax.plot(time_data, humidity_values, label="Humidity", color="green")
                ax.plot(time_data, temp_values, label="Temperature", color="orange")

                ax.set_title("Live Graph Plotter")
                ax.set_xlabel("Time (seconds)")
                ax.set_ylabel("Sensor Values")
                ax.legend(loc="upper left")

                canvas.draw()
                time.sleep(1)

        canvas = FigureCanvasTkAgg(fig, master=parent_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Button to save the graph as a PDF
        save_button = Button(parent_window, text="Save Graph as PDF", command=lambda: self.save_graph_as_pdf(fig))
        save_button.pack(pady=10)

        # Close button for the plot window
        close_button = Button(parent_window, text="Close", command=parent_window.destroy)
        close_button.pack(pady=10)

        threading.Thread(target=update_graph, daemon=True).start()

    def save_graph_as_pdf(self, fig):
        """Save the current graph as a PDF file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            fig.savefig(file_path)
            logging.info(f"Graph saved successfully to {file_path}")

    def live_bar_chart(self, parent_window):
        """Create a live bar chart for sensor data."""
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Live Bar Chart")
        ax.set_xlabel("Sensor Type")
        ax.set_ylabel("Value")

        def update_bar_chart():
            """Update the bar chart with new data continuously."""
            while True:
                ax.clear()
                if not self.data.empty:
                    ax.bar(["Gas Value", "LDR", "Humidity", "Temperature"], [
                        self.data["GAS VALUE"].iloc[-1],
                        self.data["LIGHT INTENSITY"].iloc[-1],
                        self.data["HUMIDITY"].iloc[-1],
                        self.data["TEMPERATURE"].iloc[-1]
                    ], color=["red", "blue", "green", "orange"])

                ax.set_title("Live Bar Chart")
                ax.set_xlabel("Sensor Type")
                ax.set_ylabel("Value")

                canvas.draw()
                time.sleep(1)

        canvas = FigureCanvasTkAgg(fig, master=parent_window)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Close button for the plot window
        close_button = Button(parent_window, text="Close", command=parent_window.destroy)
        close_button.pack(pady=10)

        threading.Thread(target=update_bar_chart, daemon=True).start()

    def generate_heatmap(self, parent_window):
        """Generate a heatmap for selected sensor data."""
        if self.data.empty:
            logging.warning("No data available for heatmap.")
            return

        # Select a sensor for the heatmap
        sensor_selection_window = tk.Toplevel(parent_window)
        sensor_selection_window.title("Select Sensor for Heatmap")
        
        sensors = ["GAS VALUE", "HUMIDITY", "TEMPERATURE", "LIGHT INTENSITY"]
        
        # Create a dropdown to select sensor
        selected_sensor = tk.StringVar(value=sensors[0])
        sensor_menu = ttk.Combobox(sensor_selection_window, textvariable=selected_sensor, values=sensors)
        sensor_menu.pack(pady=10)

        Button(sensor_selection_window, text="Generate Heatmap",
               command=lambda: self.display_heatmap(selected_sensor.get())).pack(pady=20)

    def display_heatmap(self, sensor):
        """Display a heatmap for the selected sensor and provide save functionality."""
        if self.data.empty or sensor not in self.data.columns:
            logging.warning(f"No data available for {sensor} heatmap.")
            return

        # Create a pivot table for heatmap
        heatmap_data = self.data.pivot_table(index='TIMESTAMP', values=sensor)

        # Create a figure for the heatmap
        plt.figure(figsize=(10, 6))

        # Define a color palette for heatmap
        cmap = sns.color_palette("RdYlGn_r", as_cmap=True)  # Red for high, Orange for mid, Green for low

        sns.heatmap(heatmap_data, cmap=cmap, cbar=True)
        plt.title(f"Heatmap for {sensor}")
        plt.xlabel("Time")
        plt.ylabel(sensor)
        plt.xticks(rotation=45)

        # Save button for the heatmap
        save_button = Button(plt.gcf().canvas.manager.window, text="Save Heatmap as PDF",
                             command=lambda: self.save_heatmap_as_pdf(plt.gcf()))
        save_button.pack(pady=10)

        plt.show()

    def save_heatmap_as_pdf(self, fig):
        """Save the current heatmap as a PDF file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", 
                                                   filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")])
        if file_path:
            fig.savefig(file_path)
            logging.info(f"Heatmap saved successfully to {file_path}")

    def forecast_menu(self):
        """Open a menu for setting up forecast options."""
        forecast_window = tk.Toplevel(self.root)
        forecast_window.title("Forecast Settings")
        forecast_window.geometry("300x200")

        # Time interval input
        Label(forecast_window, text="Forecast Time Interval (seconds):").pack(pady=10)
        self.interval_var = tk.DoubleVar(value=10)  # Default value
        interval_entry = tk.Entry(forecast_window, textvariable=self.interval_var)
        interval_entry.pack(pady=5)

        # Execute Forecast button
        execute_button = Button(forecast_window, text="EXECUTE FORECAST", command=self.execute_forecast)
        execute_button.pack(pady=20)

    def execute_forecast(self):
        """Execute the forecast based on the given time interval."""
        interval = int(self.interval_var.get())
        forecasted_values = self.forecast_sensor_values(interval)

        # Plotting the forecasted values
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.set_title("Forecasted Sensor Values")
        ax.set_xlabel("Time (seconds)")
        ax.set_ylabel("Values")

        time_points = np.arange(1, len(forecasted_values[0]) + 1) * interval

        ax.plot(time_points, forecasted_values[0], label="Gas Value", color="red")
        ax.plot(time_points, forecasted_values[1], label="Humidity", color="green")
        ax.plot(time_points, forecasted_values[2], label="Temperature", color="orange")
        ax.plot(time_points, forecasted_values[3], label="Light Intensity", color="blue")

        ax.legend()
        plt.show()

    def forecast_sensor_values(self, interval):
        """Forecast sensor values using ARIMA for the last available data."""
        gas_values = self.forecast_with_arima("GAS VALUE", interval)
        humidity_values = self.forecast_with_arima("HUMIDITY", interval)
        temperature_values = self.forecast_with_arima("TEMPERATURE", interval)
        ldr_values = self.forecast_with_arima("LIGHT INTENSITY", interval)  # Include LDR

        return gas_values, humidity_values, temperature_values, ldr_values  # Return LDR values

    def forecast_with_arima(self, sensor, interval):
        """Fit an ARIMA model and forecast future values for a given sensor."""
        series = self.data[sensor].dropna()  # Ensure no NaN values
        model = ARIMA(series, order=(1, 1, 1))  # Adjust (p, d, q) as necessary
        model_fit = model.fit()

        # Forecast the next values
        forecast = model_fit.forecast(steps=interval)
        
        return forecast

# Create the main application
if __name__ == "__main__":
    app = SensorInterface()
