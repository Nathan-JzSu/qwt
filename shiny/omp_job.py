import faicons as fa
import pandas as pd
from shiny import ui, render, reactive
from shinywidgets import output_widget, render_plotly
import plotly.express as px
import plotly.graph_objects as go

# Load data and compute static values
from shared import dataset

dataset = dataset.dropna()
# Adjust the column to get the min and max waiting time
bill_rng = (dataset.first_job_waiting_time.min(), dataset.first_job_waiting_time.max())
# Ensure the 'year' column is of integer type
dataset['year'] = dataset['year'].astype(int)

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
dataset['month'] = pd.Categorical(dataset['month'], categories=month_order, ordered=True)
cpus = sorted(dataset[dataset.job_type == 'omp'].slots.unique().tolist())
groups = [
    (2, 4), (5, 8), (6, 15), (16, 16), (17, 27), (28, 28), (32, 32), (36, 36)
]
grouped_cpus = []
for group in groups:
    start, end = group
    grouped_cpus.extend([cpu for cpu in cpus if start <= cpu <= end])
cpu_ranges = {
    "2-4": [2, 3, 4],
    "5-8": [5, 6, 7, 8],
    "6-15": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "16": [16],
    "17-27": [17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
    "28": [28],
    "32": [32],
    "36": [36],
    "other": []
}
cpu_ranges["other"].extend([int(cpu) for cpu in cpus if cpu > 36])
# print(cpu_ranges)
cpu_range_labels = list(cpu_ranges.keys())
ICONS = {
    "min": fa.icon_svg("arrow-down"),
    "max": fa.icon_svg("arrow-up"),
    "mean": fa.icon_svg("users"),
    "median": fa.icon_svg("battery-half"),
    "currency-dollar": fa.icon_svg("dollar-sign"),
    "ellipsis": fa.icon_svg("ellipsis"),
    "clock": fa.icon_svg("clock"),
    "speed": fa.icon_svg("gauge"),
    "chart-bar": fa.icon_svg("chart-bar"),
    "calendar": fa.icon_svg("calendar"),
    "comment": fa.icon_svg("comment"),
    "bell": fa.icon_svg("bell"),
    "camera": fa.icon_svg("camera"),
    "heart": fa.icon_svg("heart"),
    "count": fa.icon_svg("list"),
}

# UI for the OMP Job page
def omp_job_ui():
    return ui.page_fluid(
        ui.input_checkbox_group(
            "years",  # ID should be "years"
            "Select Year(s)",
            list(range(2013, 2025)),  # Year range from 2013 to 2024
            selected=[2024],  # Default to selecting the year 2024
            inline=True  # Arrange checkboxes horizontally
        ),
        ui.input_checkbox_group(
            "months",  # ID should be "years"
            "Select Month(s)",
            month_order,  # Year range from 2013 to 2024
            selected=['Jan'],  # Default to selecting the year 2024
            inline=True  # Arrange checkboxes horizontally
        ),
        ui.input_checkbox_group(
            "cpus",  
            "Select CPU Cores",
            cpu_range_labels,  
            selected=cpus,
            inline=True  
        ),
        ui.input_action_button("select_all_cpus", "Select All", class_="btn btn-primary"),
        ui.input_action_button("unselect_all_cpus", "Unselect All", class_="btn btn-secondary"),
        ui.layout_columns(
            ui.value_box(
                "Min Waiting Time", ui.output_text("min_waiting_time"), showcase=ICONS["min"]
            ),
            ui.value_box(
                "Max Waiting Time", ui.output_text("max_waiting_time"), showcase=ICONS["max"]
            ),
            ui.value_box(
                "Mean Waiting Time", ui.output_text("mean_waiting_time"), showcase=ICONS["speed"]
            ),
            ui.value_box(
                "Median Waiting Time", ui.output_text("median_waiting_time"), showcase=ICONS["median"]
            ),
            ui.value_box(
                "Number of Jobs", ui.output_text("job_count"), showcase=ICONS["count"]  # New box for row count
            ),
            fill=False,
        ),
       
        ui.layout_columns(
            ui.card(
                ui.card_header("Dataset Data"),
                ui.output_data_frame("displayTable"),  # Display the table rendered by the render function
                full_screen=True
            ),
            ui.card(
                ui.card_header(
                    "Waiting Time vs Job Type",
                    ui.popover(
                        ICONS["ellipsis"],
                        ui.input_radio_buttons(
                            "scatter_color",
                            None,
                            ["job_type", "none"],
                            inline=True,
                        ),
                        title="Add a color variable",
                        placement="top",
                    ),
                    class_="d-flex justify-content-between align-items-center",
                ),
                output_widget("barplot"),  # Display the barplot rendered by the render function
                full_screen=True
            ),
            ui.card(
                ui.card_header(
                    "Box Plot of Job Waiting Time by Month & Year",
                    class_="d-flex justify-content-between align-items-center"
                ),
                output_widget("job_waiting_time_by_month"),  # Display the box plot rendered by the render function
                full_screen=True
            ),
            col_widths=[6, 6, 6]  # Adjust column widths as needed
        ),
        fillable=True,
    )

# Server logic for the OMP Job page
def omp_job_server(input, output, session):
    print("OMP Job server function called")

    @reactive.calc
    def dataset_data():
        print("dataset_data function called for OMP Job")
        years = input.years()
        months = input.months()
        cpus_selected = input.cpus()
        print(f"Input Years: {years}", f"input months: {months}")

        # Convert selected years to integers
        years = list(map(int, years))
        # convert selected cpus cores from string to integer
        expanded_cpus_selected = []
        if cpus_selected:
            for cpu_label in cpus_selected:
                if cpu_label in cpu_ranges:
                    expanded_cpus_selected.extend(cpu_ranges[cpu_label])
            # Remove duplicates if any, just in case
            expanded_cpus_selected = list(set(expanded_cpus_selected))
        else:
            expanded_cpus_selected = []  # No CPUs selected, handle accordingly

        idx2 = dataset.job_type.str.contains("omp")  # Assuming 'job_type' column contains GPU jobs
        idx3 = dataset.year.isin(years) if years else True  # Check for selected years if any
        idx4 = dataset.month.isin(months) if months else True
        idx5 = dataset.slots.isin(expanded_cpus_selected) if expanded_cpus_selected else True  # Filter for selected CPUs

        filtered_data = dataset[idx2 & idx3 & idx4 & idx5]
        # print(f"Filtered Data for OMP Job: {filtered_data}")  # Debugging print
        return filtered_data

    @output
    @render.data_frame
    def displayTable():
        data = dataset_data().copy()  # Get the data from the reactive dataset function

        data['first_job_waiting_time'] = data['first_job_waiting_time'].apply(
            # lambda x: f"{x / 3600:.1f} (hr)" if x > 3600 else f"{x / 60:.1f} (min)"
            lambda x: f"{x / 60:.1f}"
        )

        # Sort the data by 'job_number' (Job ID) in ascending order
        data = data.sort_values(by='job_number', ascending=True)

        # Rename columns only for display purposes
        data_renamed = data.rename(columns={
            'job_type': 'Job Type',
            'first_job_waiting_time': 'Waiting Time (min)',
            'month': 'Month',
            'job_number': 'Job Number',
            'year': 'Year',
            'slots': 'CPU Cores'
        })

        return data_renamed

    # Define the rendering logic for the waiting times
    @render.text
    def min_waiting_time():
        d = dataset_data()
        if d.shape[0] > 0:
            min_waiting_time = d.first_job_waiting_time.min() / 60
            if min_waiting_time > 60:
                return f"{min_waiting_time / 60:.1f} hours"
            else:
                return f"{min_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def max_waiting_time():
        d = dataset_data()
        if d.shape[0] > 0:
            max_waiting_time = d.first_job_waiting_time.max() / 60
            if max_waiting_time > 60:
                return f"{max_waiting_time / 60:.1f} hours"
            else:
                return f"{max_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def mean_waiting_time():
        d = dataset_data()
        if d.shape[0] > 0:
            mean_waiting_time = d.first_job_waiting_time.mean() / 60
            if mean_waiting_time > 60:
                return f"{mean_waiting_time / 60:.1f} hours"
            else:
                return f"{mean_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def median_waiting_time():
        d = dataset_data()
        if d.shape[0] > 0:
            med_waiting_time = d.first_job_waiting_time.median() / 60
            if med_waiting_time > 60:
                return f"{med_waiting_time / 60:.1f} hours"
            else:
                return f"{med_waiting_time:.1f} min"
        return "No data available"
    
    @render.text
    def job_count():
        d = dataset_data()
        return f"{d.shape[0]}"

    @render.data_frame
    def table():
        df = dataset_data()
        df_modified = df.copy()
        df_modified['first_job_waiting_time'] = (df_modified['first_job_waiting_time'] / 60).round(2)  # Convert waiting time from seconds to minutes
        df_modified.rename(columns={'first_job_waiting_time': 'first_job_waiting_time (min)'}, inplace=True)
        return render.DataGrid(df_modified)

    @render_plotly
    def barplot():
        data = dataset_data().copy()
        if data.empty:
            print("No data available for bar plot in OMP Job")  # Debugging print
            return go.Figure()  # Return an empty figure

        # Filter and preprocess the data
        filtered_data = data[data["first_job_waiting_time"] >= 0]
        filtered_data['first_job_waiting_time'] = (filtered_data['first_job_waiting_time'] / 60).round(2)

        # Create a column for grouping slots based on CPU ranges
        def get_cpu_range(slot):
            for key, cpu_range in cpu_ranges.items():
                if slot in cpu_range:
                    return key
            return "other"  # Default group

        filtered_data['cpu_group'] = filtered_data['slots'].apply(get_cpu_range)

        # Group by 'cpu_group' and calculate the median waiting time
        grouped_data = filtered_data.groupby("cpu_group")["first_job_waiting_time"].median().reset_index()

        # Sort the groups to maintain the correct order
        group_order = list(cpu_ranges.keys())
        grouped_data['cpu_group'] = pd.Categorical(grouped_data['cpu_group'], categories=group_order, ordered=True)
        grouped_data = grouped_data.sort_values('cpu_group')

        # Create the bar plot
        fig = px.bar(
            grouped_data,
            x="cpu_group",
            y="first_job_waiting_time",
            labels={
                "first_job_waiting_time": "Median Waiting Time (min)",
                "cpu_group": "CPU Groups"
            },
            text_auto='.1f'  # Display the values on top of bars
        )

        return fig



    @render_plotly
    def job_waiting_time_by_month():
        data = dataset_data().copy()
        if data.empty:
            print("No data available for Job Waiting Time by Month")  # Debugging print
            return go.Figure()  # Return an empty figure

        # Filter data by selected years
        data = data[data['year'].isin(map(int, input.years()))]

        # Convert waiting time from seconds to hours
        data['job_waiting_time (hours)'] = data['first_job_waiting_time'] / 3600

        # Create a column for grouping slots based on CPU ranges
        def get_cpu_range(slot):
            for key, cpu_range in cpu_ranges.items():
                if slot in cpu_range:
                    return key
            return "other"  # Default group

        data['cpu_group'] = data['slots'].apply(get_cpu_range)

        # Ensure consistent month order
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data['month'] = pd.Categorical(data['month'], categories=month_order, ordered=True)

        # Create box plot
        fig = px.box(
            data,
            x='month',
            y='job_waiting_time (hours)',
            color='year',
            facet_col='cpu_group',  # Use grouped CPU ranges as facets
            title="Job Waiting Time by Month and CPU Group (Box Plot in Hours)",
            labels={
                "job_waiting_time (hours)": "Job Waiting Time (hours)",
                "cpu_group": "CPU Group"
            }
        )

        # Update layout for better visualization
        fig.update_layout(
            yaxis=dict(range=[0, 20]),  # Adjust Y-axis to focus on lower range
            boxmode='group',  # Group boxes for better comparison
            title=None,  # Remove the main title
            showlegend=True  # Show legend for better understanding
        )

        # Set the title of each facet column using the values in 'cpu_group'
        for i, group in enumerate(data['cpu_group'].unique(), start=1):
            subplot_title = f"{group}"
            fig.layout.annotations[i - 1]['text'] = subplot_title

        # Remove x-axis title for all subplots
        for axis in fig.layout:
            if axis.startswith('xaxis'):
                fig.layout[axis].title.text = None

        # Update traces to include jittered points without overriding colors assigned by `color='year'`
        fig.update_traces(
            marker=dict(
                size=6,  # Adjust marker size
                opacity=0.7,  # Adjust marker opacity
                line=dict(width=1, color='white')  # Add a white outline for further contrast
            ),
            boxpoints='all',  # Show all points
            jitter=0.3,  # Add jitter for better visibility
            pointpos=0  # Position the points within the box
        )

        return fig


    @reactive.effect
    @reactive.event(input.select_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[job for job in dataset.job_type.unique() if "OMP" in job])

    @reactive.effect
    @reactive.event(input.unselect_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[])

    @reactive.effect
    @reactive.event(input.cpus)
    def _():
        selected_cpus = input.cpus()  # Get selected CPUs
        # Example: Filter dataset or update UI components based on selected CPUs
        filtered_jobs = dataset[dataset['slots'].isin(selected_cpus)]

    @reactive.effect
    @reactive.event(input.select_all_cpus)
    def _():
        # Select all CPU cores when "Select All" button is clicked
        cpus = sorted(dataset.slots.unique().tolist())
        selected_labels = []
        # Find range labels with at least one CPU present in the list
        for label, cpu_list in cpu_ranges.items():
            if any(cpu in cpus for cpu in cpu_list): # Check if any CPU in the range is present
                selected_labels.append(label)
        ui.update_checkbox_group("cpus", selected=selected_labels)

    @reactive.effect
    @reactive.event(input.unselect_all_cpus)
    def _():
        # Unselect all CPU cores when "Unselect All" button is clicked
        ui.update_checkbox_group("cpus", selected=[])