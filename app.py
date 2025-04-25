from shiny import App, reactive, render, ui
from homepage import homepage_ui, homepage_server
from gpu_job import gpu_job_ui, gpu_job_server
from mpi_job import mpi_job_ui, mpi_job_server
from omp_job import omp_job_ui, omp_job_server
from onep_job import oneP_job_ui, oneP_job_server 


# Import additional page logic if needed (e.g., GPU Job, MPI Job)
# from gpu_job import gpu_job_ui, gpu_job_server

app_ui = ui.page_fluid(
    ui.tags.div(
        ui.navset_bar(
            ui.nav_panel("All Jobs"),
            ui.nav_panel("GPU Job"),
            ui.nav_panel("MPI Job"),
            ui.nav_panel("OMP Job"),
            ui.nav_panel("1-p Job"),
            id="selected_navset_bar",
            title="Entry Job Analysis",
        ),
        id="nav-bar-content",
        style="background-color: #f8f9fa; padding: 10px; height: 75px;"
    ),
    ui.output_ui("page_content")
)

# def server(input, output, session):
#     current_page = reactive.Value("All Jobs")

#     @reactive.effect
#     def update_page():
#         current_page.set(input.selected_navset_bar())

#     # Dynamically render UI based on the current page
#     @output
#     @render.ui
#     def page_content():
#         if current_page.get() == "All Jobs":
#             return homepage_ui()
#         elif current_page.get() == "GPU Job":
#             return gpu_job_ui()
#         elif current_page.get() == "MPI Job":
#             return mpi_job_ui()
#         elif current_page.get() == "OMP Job":
#             return omp_job_ui()
#         elif current_page.get() == "1-p Job":
#             return oneP_job_ui()

#     # Dynamically call server logic based on the current page
#     @reactive.effect
#     def call_server():
#         if current_page.get() == "All Jobs":
#             homepage_server(input, output, session)
#         elif current_page.get() == "GPU Job":
#             gpu_job_server(input, output, session)
#         elif current_page.get() == "MPI Job":
#             mpi_job_server(input, output, session)
#         elif current_page.get() == "OMP Job":
#             omp_job_server(input, output, session)
#         elif current_page.get() == "1-p Job":
#             oneP_job_server(input, output, session)


# app = App(app_ui, server)

def server(input, output, session):
    current_page = reactive.Value("All Jobs")

    @reactive.effect
    def update_page():
        current_page.set(input.selected_navset_bar())

    # Initialize all server logic once
    homepage_server(input, output, session)
    gpu_job_server(input, output, session)
    mpi_job_server(input, output, session)
    omp_job_server(input, output, session)
    oneP_job_server(input, output, session)

    # Only show active page
    @output
    @render.ui
    def page_content():
        active = current_page.get()

        def visible(page_name):
            return "display: block;" if active == page_name else "display: none;"

        return ui.tags.div(
            ui.tags.div(homepage_ui(), id="all-jobs", style=visible("All Jobs")),
            ui.tags.div(gpu_job_ui(), id="gpu-job", style=visible("GPU Job")),
            ui.tags.div(mpi_job_ui(), id="mpi-job", style=visible("MPI Job")),
            ui.tags.div(omp_job_ui(), id="omp-job", style=visible("OMP Job")),
            ui.tags.div(oneP_job_ui(), id="onep-job", style=visible("1-p Job")),
        )


app = App(app_ui, server)