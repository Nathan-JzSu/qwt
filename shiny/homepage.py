import faicons as fa
import pandas as pd
from shiny import ui, render, reactive
from shinywidgets import output_widget, render_plotly
import plotly.express as px
import plotly.graph_objects as go

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

# def format_time_range(value_range):
#     """Helper function to format time in appropriate units."""
#     min_time, max_time = value_range
#     if max_time >= 3600:   
#         return (int(min_time / 3600), int(max_time / 3600)), "Hours"
#     elif max_time >= 60:   
#         return (int(min_time / 60), int(max_time / 60)), "Minutes"
#     else:   
#         return (int(min_time), int(max_time)), "Seconds"
        
# formatted_range, unit_label = format_time_range(bill_rng)

# UI for the homepage
def homepage_ui():
    return ui.page_sidebar(
        ui.sidebar(
            ui.output_ui("dynamic_slider"),  # Dynamically render slider
            ui.input_checkbox_group(
                "job_type",
                "Job Type",
                list(dataset.job_type.unique()),
                selected=list(dataset.job_type.unique()),
                inline=True,
            ),
            ui.input_action_button("select_all", "Select All"),
            ui.input_action_button("unselect_all", "Unselect All"),
            open="desktop",
        ),
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
                "Number of Jobs", ui.output_text("job_count"), showcase=ICONS["count"]
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
            ui.card(
                ui.card_header(
                    "3D Bubble Chart of Average Job Waiting Time by Year & Job Type",
                    class_="d-flex justify-content-between align-items-center"
                ),
                output_widget("job_waiting_time_3d"),  # Display the 3D bubble chart rendered by the render function
                full_screen=True
            ),
            col_widths=[6, 6, 6, 6]
        ),
        fillable=True,
    )

# Server logic for the homepage
def homepage_server(input, output, session):
    print("Homepage server function called")

    @reactive.calc
    def filtered_dataset():
        """Filter dataset based on selected years."""
        years = list(map(int, input.years()))
        return dataset[dataset.year.isin(years)]

    @reactive.calc
    def formatted_range():
        """Calculate and format the range for the slider."""
        filtered_data = filtered_dataset()
        min_time, max_time = filtered_data.first_job_waiting_time.min(), filtered_data.first_job_waiting_time.max()
        if max_time >= 3600:   
            return (int(min_time / 3600), int(max_time / 3600)+1), "Hours"
        elif max_time >= 60:   
            return (int(min_time / 60), int(max_time / 60)+1), "Minutes"
        else:   
            return (int(min_time), int(max_time)+1), "Seconds"

    @output
    @render.ui
    def dynamic_slider():
        """Dynamically render the slider UI."""
        range_values, unit_label = formatted_range()
        return ui.input_slider(
            "first_job_waiting_time",
            f"Waiting Time ({unit_label})",
            min=max(0, range_values[0]),  # Ensure minimum is >= 0
            max=range_values[1],
            value=(max(0, range_values[0]), range_values[1]),
        )

    @reactive.calc
    def dataset_data():
        print("dataset_data function called")
        print(input.first_job_waiting_time())
        print(input.years())
        bill = input.first_job_waiting_time()
        years = input.years()
        
        print(f"Input Waiting Time: {bill}")  # Debugging print
        print(f"Input Years: {years}")

        # Convert selected years to integers
        years = list(map(int, years))
        
        idx1 = dataset.first_job_waiting_time.between(bill[0] * 3600, bill[1] * 3600)
        idx2 = dataset.job_type.isin(input.job_type())
        idx3 = dataset.year.isin(years) if years else True  # Check for selected years if any

        filtered_data = dataset[idx1 & idx2 & idx3]
        
        print(f"Filtered Data: {filtered_data}")  # Debugging print
        # return filtered_data
        return filtered_data[['job_type', 'first_job_waiting_time', 'month', 'job_number', 'year', 'slots']]

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
        d = dataset_data()  # Replace with your data fetching logic
        print(f"Min Waiting Time Data Shape: {d.shape}")
        if d.shape[0] > 0:
            min_waiting_time = d.first_job_waiting_time.min() / 60
            if min_waiting_time > 60:
                return f"{min_waiting_time / 60:.1f} hours"
            else:
                return f"{min_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def max_waiting_time():
        d = dataset_data()  # Replace with your data fetching logic
        if d.shape[0] > 0:
            max_waiting_time = d.first_job_waiting_time.max() / 60
            if max_waiting_time > 60:
                return f"{max_waiting_time / 60:.1f} hours"
            else:
                return f"{max_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def mean_waiting_time():
        d = dataset_data()  # Replace with your data fetching logic
        if d.shape[0] > 0:
            mean_waiting_time = d.first_job_waiting_time.mean() / 60
            if mean_waiting_time > 60:
                return f"{mean_waiting_time / 60:.1f} hours"
            else:
                return f"{mean_waiting_time:.1f} min"
        return "No data available"

    @render.text
    def median_waiting_time():
        d = dataset_data()  # Replace with your data fetching logic
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
        df = dataset_data()  # Replace with your data fetching logic
        df_modified = df.copy()
        df_modified['first_job_waiting_time'] = (df_modified['first_job_waiting_time'] / 60).round(2)  # Convert waiting time from seconds to minutes
        df_modified.rename(columns={'first_job_waiting_time': 'first_job_waiting_time (min)'}, inplace=True)            
        return render.DataGrid(df_modified)

    @render_plotly

    def barplot():
        color = input.scatter_color()
        data = dataset_data()
        if data.empty:
            print("No data available for bar plot")  # Debugging print
            return go.Figure()  # Return an empty figure
        
        # Filter and preprocess the data
        filtered_data = data[data["first_job_waiting_time"] >= 0]
        filtered_data['first_job_waiting_time'] = (filtered_data['first_job_waiting_time'] / 60).round(2)
        
        # Separate job types
        oneP = filtered_data[filtered_data["job_type"] == "1-p"]
        GPU = filtered_data[filtered_data["job_type"].isin(["GPU > 1", "GPU = 1"])]
        GPU["job_type"] = "GPU"
        MPI = filtered_data[filtered_data["job_type"].isin(
            ["MPI job a", "MPI job budge", "MPI job as", "MPI job z", "MPI job 4"]
        )]
        MPI["job_type"] = "MPI"
        OMP = filtered_data[filtered_data["job_type"] == "omp"]
        
        # Concatenate and group data
        grouped_data = pd.concat([oneP, GPU, MPI, OMP])
        grouped_data = grouped_data.groupby("job_type")["first_job_waiting_time"].median().reset_index()

        # Create a bar plot
        fig = px.bar(
            grouped_data,
            x="job_type",
            y="first_job_waiting_time",
            color=None if color == "none" else color,
            labels={
                "first_job_waiting_time": "Median Waiting Time (min)",
                "job_type": "Job Type"
            },
            text_auto='.1f'  # Automatically show values on top of bars
        )

        return fig


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

    @render_plotly
    def job_waiting_time_3d():
        data = dataset_data()
        # Filter data for job types and years
        data = data[data['job_type'].isin(input.job_type())]
        data = data[data['year'].isin(map(int, input.years()))]
        # Aggregate waiting time by month, year, and job_type
        data = data.groupby(['year', 'month', 'job_type'])['first_job_waiting_time'].mean().reset_index()
        # Convert waiting time from seconds to hours
        data['first_job_waiting_time (hours)'] = data['first_job_waiting_time'] / 3600
        # Check for and handle NaN values
        data['first_job_waiting_time (hours)'].fillna(0, inplace=True)  # Replace NaNs with 0
        # Ensure 'month' is categorical and ordered correctly
        month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        data['month'] = pd.Categorical(data['month'], categories=month_order, ordered=True)
        # Create 3D scatter plot
        fig = px.scatter_3d(
            data, 
            x='month', 
            y='job_type', 
            z='first_job_waiting_time (hours)', 
            size='first_job_waiting_time (hours)', 
            color='month', 
            hover_data=['year', 'job_type'],
            title="3D Bubble Chart of Job Waiting Time by Month & Job Type"
        )
        # Update layout to ensure all months are displayed
        fig.update_layout(
            scene=dict(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(12)),
                    ticktext=month_order
                )
            ),
            scene_zaxis_type="linear"  # Set z-axis to linear scale
        )
        return fig

    @reactive.effect
    @reactive.event(input.select_all)
    def _():
        ui.update_checkbox_group("job_type", selected=list(dataset.job_type.unique()))

    @reactive.effect
    @reactive.event(input.unselect_all)
    def _():
        ui.update_checkbox_group("job_type", selected=[])




