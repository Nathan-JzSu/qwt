import faicons as fa
import pandas as pd
from shiny import ui, render, reactive
from shinywidgets import output_widget, render_plotly
import plotly.express as px

# Load data and compute static values
from shared import dataset

# Adjust the column to get the min and max waiting time
bill_rng = (dataset.first_job_waiting_time.min(), dataset.first_job_waiting_time.max())
# Ensure the 'year' column is of integer type
dataset['year'] = dataset['year'].astype(int)

month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
dataset['month'] = pd.Categorical(dataset['month'], categories=month_order, ordered=True)

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

# UI for the GPU Job page
def gpu_job_ui():
    return ui.page_fluid(
        ui.input_checkbox_group(
            "years",  # ID should be "years"
            "Select Year(s)",
            list(range(2013, 2025)),  # Year range from 2013 to 2024
            selected=[2024],  # Default to selecting the year 2024
            inline=True  # Arrange checkboxes horizontally
        ),
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

# Server logic for the GPU Job page
def gpu_job_server(input, output, session):
    print("GPU Job server function called")

    @reactive.calc
    def dataset_data():
        print("dataset_data function called for GPU Job")
        years = input.years()
        
        print(f"Input Years: {years}")

        # Convert selected years to integers
        years = list(map(int, years))
        
        idx2 = dataset.job_type.str.contains("GPU")  # Assuming 'job_type' column contains GPU jobs
        idx3 = dataset.year.isin(years) if years else True  # Check for selected years if any

        filtered_data = dataset[idx2 & idx3]
        filtered_data = filtered_data.drop_duplicates(subset=['job_number'])
        print(f"Filtered Data for GPU Job: {filtered_data}")  # Debugging print
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
        color = input.scatter_color()
        data = dataset_data().copy()
        if data.empty:
            print("No data available for bar plot in GPU Job")  # Debugging print
            return go.Figure()  # Return an empty figure
        
        # data['job_type'] = data['job_type'].str.replace('GPU job ', '', regex=False)

        # Filter and preprocess the data
        filtered_data = data[data["first_job_waiting_time"] >= 0]
        filtered_data['first_job_waiting_time'] = (filtered_data['first_job_waiting_time'] / 60).round(2)

        # Group the data by 'job_type' and calculate the median waiting time
        grouped_data = filtered_data.groupby("job_type")["first_job_waiting_time"].median().reset_index()
        
        # Create the bar plot
        fig = px.bar(
            grouped_data,
            x="job_type",
            y="first_job_waiting_time",
            color=None if color == "none" else color,
            labels={
                "first_job_waiting_time": "Median Waiting Time (min)",
                "job_type": "Job Type"
            },
            text_auto='.1f'  # Display the values on top of bars
        )

        return fig


    @render_plotly
    def job_waiting_time_by_month():
        data = dataset_data()
        # Filter data for job types and years
        data = data[data['job_type'].str.contains("GPU")]  # Filter only GPU jobs
        data = data[data['year'].isin(map(int, input.years()))]
        # Convert waiting time from seconds to hours
        data['job_waiting_time (hours)'] = data['first_job_waiting_time'] / 3600
        # Create box plot
        fig = px.box(
            data,
            x='month',
            y='job_waiting_time (hours)',
            color='year',
            facet_col='job_type',
            title="GPU Job Waiting Time by Month and Year (Box Plot in Hours)",
            labels={
                "job_waiting_time (hours)": "Job Waiting Time (hours)"
            }
        )
        # Update layout for better visualization
        fig.update_layout(
            yaxis=dict(range=[0, 20]),  # Adjust Y-axis to focus on lower range
            boxmode='group',  # Group boxes for better comparison
            title=None,  # Remove the main title
            showlegend=True  # Show legend for better understanding
        )

        # Remove the subplot (facet) titles
        for annotation in list(fig['layout']['annotations']):
            annotation['text'] = annotation['text'][9:]
        
        # Remove x-axis title for all subplots
        for axis in fig.layout:
            if axis.startswith('xaxis'):
                fig.layout[axis].title.text = None

        # Update traces to include jittered points with a distinct color
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
        
        # Ensure consistent month order
        fig.update_xaxes(categoryorder='array', categoryarray=month_order)

        return fig

    @reactive.effect
    @reactive.event(input.select_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[job for job in dataset.job_type.unique() if "GPU" in job])

    @reactive.effect
    @reactive.event(input.unselect_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[])

