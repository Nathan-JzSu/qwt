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

# UI for the 1p Job page
def oneP_job_ui():
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
                    "Box Plot of Job Waiting Time by Month & Year",
                    class_="d-flex justify-content-between align-items-center"
                ),
                output_widget("job_waiting_time_by_month"),  # Display the box plot rendered by the render function
                full_screen=True
            ),
            col_widths=[6, 6]  # Adjust column widths as needed
        ),
        fillable=True,
    )

# Server logic for the 1p Job page
def oneP_job_server(input, output, session):
    print("1P Job server function called")

    @reactive.calc
    def dataset_data():
        print("dataset_data function called for 1P Job")
        years = input.years()
        months = input.months()
        print(f"Input Years: {years}", f"input months: {months}")

        # Convert selected years to integers
        years = list(map(int, years))

        idx2 = dataset.job_type.str.contains("1-p")  # Assuming 'job_type' column contains GPU jobs
        idx3 = dataset.year.isin(years) if years else True  # Check for selected years if any
        idx4 = dataset.month.isin(months) if months else True

        filtered_data = dataset[idx2 & idx3 & idx4]
        print(f"Filtered Data for 1P Job: {filtered_data}")  # Debugging print
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
    def job_waiting_time_by_month():
        data = dataset_data()
        # Filter data for job types and years
        data = data[data['job_type'].isin(input.job_type())]
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
            title="Job Waiting Time by Month and Year (Box Plot in Hours)",
            labels={
                "job_waiting_time (hours)": "Job Waiting Time (hours)"
            },
        )

        # Update layout for better visualization
        fig.update_layout(
            yaxis=dict(range=[0, 20]),  # Adjust Y-axis to focus on lower range
            boxmode='group',  # Group boxes for better comparison
            title=None,  # Remove the main title
            showlegend=True,  # Show legend for better understanding
        )

        # Remove the subplot (facet) titles
        for annotation in list(fig['layout']['annotations']):
            annotation['text'] = annotation['text'][9:]

        # Remove x-axis title for all subplots
        for axis in fig.layout:
            if axis.startswith('xaxis'):
                fig.layout[axis].title.text = None

        # Add jittered points for each year with a dark color
        for year in data['year'].unique():
            jitter_data = data[data['year'] == year]
            fig.add_scatter(
                x=jitter_data['month'],
                y=jitter_data['job_waiting_time (hours)'],
                mode='markers',
                name=f'Year {year} Jittered Points',
                marker=dict(
                    size=6,
                    opacity=0.7,
                    color='rgba(50, 50, 50, 0.7)',  # Dark color for jittered points
                    line=dict(width=1, color='white'),
                ),
                legendgroup=f'Year {year}',  # Group legend entries
                showlegend=False,  # Hide extra legend entries for jittered points
            )

        # Ensure consistent month order
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        fig.update_xaxes(categoryorder='array', categoryarray=month_order)

        return fig

        

    @reactive.effect
    @reactive.event(input.select_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[job for job in dataset.job_type.unique() if "OMP" in job])

    @reactive.effect
    @reactive.event(input.unselect_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[])