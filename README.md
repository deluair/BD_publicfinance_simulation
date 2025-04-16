# Bangladesh Public Finance Simulation Model

## Overview

This project implements a dynamic simulation model of Bangladesh's public finance system. It aims to project key fiscal and economic variables from a specified start year (e.g., 2025) to an end year (e.g., 2050), capturing interactions between various sectors.

The model incorporates modules for:

* Revenue Mobilization
* Expenditure Management
* Debt Dynamics & Sustainability
* Financial Sector Stability
* Monetary Policy Interaction
* Governance & Institutional Factors
* State-Owned Enterprises (SOEs)
* External Sector (Trade, FX Reserves)
* Fiscal Federalism
* Development Finance
* Policy Coordination

## Project Structure

```text
BD_publicfinance_simulation/
├── config/
│   └── config.yaml        # Simulation parameters and initial conditions
├── data/                  # Placeholder for input data files
├── notebooks/             # Jupyter notebooks for analysis and experimentation
├── results/
│   ├── plots/             # Directory where output plots are saved
│   ├── simulation_output.csv # Raw simulation results
│   └── simulation_report.html # Formatted HTML report with summaries and plots
├── src/
│   ├── __init__.py
│   ├── models/            # Core simulation model components
│   │   ├── __init__.py
│   │   ├── debt.py
│   │   ├── expenditure.py
│   │   ├── revenue.py
│   │   └── ... (other model files)
│   ├── analysis/          # Scripts for analyzing results (if needed)
│   ├── data_handlers/     # Scripts for loading/processing data (if needed)
│   ├── utils/             # Utility functions
│   ├── simulation.py      # Main simulation orchestrator class
│   ├── visualization.py   # Script to generate plots from results
│   └── reporting.py       # Script to generate the HTML report
├── templates/
│   └── report_template.html # Jinja2 template for the HTML report
├── tests/                 # Unit and integration tests (placeholder)
├── .gitignore             # Specifies intentionally untracked files
├── requirements.txt       # Project dependencies
└── README.md              # This file
```

## Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/deluair/BD_publicfinance_simulation.git
    cd BD_publicfinance_simulation
    ```

2.  **Create a virtual environment (recommended):**

    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The simulation's behavior is primarily controlled by the `config/config.yaml` file. This file contains:

*  Simulation time frame (`start_year`, `end_year`).
*  Initial economic conditions (GDP, inflation, debt levels, etc.).
*  Parameters for each model module (e.g., tax buoyancy, expenditure efficiency factors, NPL recovery rates).

You can modify this file to run different scenarios or update initial assumptions.

## Usage

To run the full simulation, execute the `simulation.py` script as a module from the project's root directory:

```bash
python -m src.simulation
```

This command will:

1.  Initialize the simulation based on `config/config.yaml`.
2.  Run the simulation year by year from `start_year` to `end_year`.
3.  Save the detailed results to `results/simulation_output.csv`.
4.  Generate plots for key variables and save them in `results/plots/`.
5.  Generate a summary HTML report at `results/simulation_report.html`.

Open `results/simulation_report.html` in a web browser to view the summary and visualizations.

## Outputs

*  **`results/simulation_output.csv`**: A CSV file containing the time series data for all tracked variables for each year of the simulation.
*  **`results/plots/`**: Contains PNG images of plots for key indicators (GDP, Debt/GDP, Inflation, etc.).
*  **`results/simulation_report.html`**: An HTML file summarizing the final year's results and embedding the generated plots for easy viewing.

## Current Status & Future Work

*  The core simulation loop is functional.
*  Visualization and HTML reporting are implemented.
*  **TODO:** Several model outputs currently result in `NaN` (e.g., Revenue/Expenditure GDP ratios, Financial Stability Index, FX Reserves). The logic within the respective model files (`revenue.py`, `expenditure.py`, `financial_sector.py`, `external_sector.py`) needs to be completed or connected correctly to populate these variables.
*  **TODO:** Add unit tests for individual model components.
*  **TODO:** Enhance model realism and add more sophisticated interactions.
*  **TODO:** Allow for easier scenario definition and comparison.

## Dependencies

Key Python libraries used:

*  `pandas`
*  `numpy`
*  `PyYAML`
*  `matplotlib`
*  `Jinja2`

See `requirements.txt` for the full list.
