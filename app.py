from shiny import App, reactive, render, ui

# Import UI + server logic per page
from homepage import homepage_ui, homepage_server
from gpu_job import gpu_job_ui, gpu_job_server
from mpi_job import mpi_job_ui, mpi_job_server
from omp_job import omp_job_ui, omp_job_server
from onep_job import oneP_job_ui, oneP_job_server

# ----------------------------------------------------------------------
# UI: Main Layout with Navigation Bar
# ----------------------------------------------------------------------
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

# ----------------------------------------------------------------------
# Server: Reactive Page Switching + Initialization
# ----------------------------------------------------------------------
def server(input, output, session):
    current_page = reactive.Value("All Jobs")
    initialized_pages = set()

    @reactive.effect
    def update_page():
        current_page.set(input.selected_navset_bar())

    @output
    @render.ui
    def page_content():
        match current_page.get():
            case "All Jobs":
                return homepage_ui()
            case "GPU Job":
                return gpu_job_ui()
            case "MPI Job":
                return mpi_job_ui()
            case "OMP Job":
                return omp_job_ui()
            case "1-p Job":
                return oneP_job_ui()

    @reactive.effect
    def call_server():
        page = current_page.get()
        if page not in initialized_pages:
            initialized_pages.add(page)
            match page:
                case "All Jobs":
                    homepage_server(input, output, session)
                case "GPU Job":
                    gpu_job_server(input, output, session)
                case "MPI Job":
                    mpi_job_server(input, output, session)
                case "OMP Job":
                    omp_job_server(input, output, session)
                case "1-p Job":
                    oneP_job_server(input, output, session)

# ----------------------------------------------------------------------
# Launch the App
# ----------------------------------------------------------------------
app = App(app_ui, server)
