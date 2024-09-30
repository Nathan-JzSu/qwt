from shiny import App, reactive, render, ui
from homepage import homepage_ui, homepage_server
from gpu_job import gpu_job_ui, gpu_job_server

# Import additional page logic if needed (e.g., GPU Job, MPI Job)
# from gpu_job import gpu_job_ui, gpu_job_server

app_ui = ui.page_fluid(
    ui.tags.div(
        ui.navset_bar(
            ui.nav_panel("All Jobs"),
            ui.nav_panel("GPU Job"),
            ui.nav_panel("MPI Job"),
            ui.nav_panel("OMP Job"),
            id="selected_navset_bar",
            title="Job Type",
        ),
        id="nav-bar-content",
        style="background-color: #f8f9fa; padding: 10px; height: 75px;"
    ),
    ui.output_ui("page_content")
)

def server(input, output, session):
    current_page = reactive.Value("All Jobs")

    @reactive.effect
    def update_page():
        selected_page = input.selected_navset_bar()
        current_page.set(selected_page)

    # Dynamically render UI based on the current page
    @output
    @render.ui
    def page_content():
        if current_page.get() == "All Jobs":
            return homepage_ui()
        elif current_page.get() == "GPU Job":
            return gpu_job_ui()
        elif current_page.get() == "MPI Job":
            return ui.page_fluid("MPI Job Page (UI to be implemented)")
        elif current_page.get() == "OMP Job":
            return ui.page_fluid("OMP Job Page (UI to be implemented)")

    # Dynamically call server logic based on the current page
    @reactive.effect
    def call_server():
        if current_page.get() == "All Jobs":
            homepage_server(input, output, session)
        elif current_page.get() == "GPU Job":
            gpu_job_server(input, output, session)
        # Add logic here if you implement separate server logic for "MPI Job"
        # elif current_page.get() == "MPI Job":
        #     mpi_job_server(input, output, session)

app = App(app_ui, server)
