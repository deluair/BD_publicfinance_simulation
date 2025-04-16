import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define commonly used variables for plotting
KEY_VARIABLES = {
    'GDP': {'title': 'Nominal GDP', 'ylabel': 'Value (Local Currency)'},
    'GDP_Growth': {'title': 'Nominal GDP Growth Rate', 'ylabel': 'Growth Rate (%)', 'format': '%', 'multiplier': 100},
    'Inflation': {'title': 'Inflation Rate', 'ylabel': 'Rate (%)', 'format': '%', 'multiplier': 100},
    'Debt_Stock_GDP': {'title': 'Total Debt Stock to GDP Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'Debt_Stock_Domestic': {'title': 'Domestic Debt Stock', 'ylabel': 'Value (Local Currency)', 'combined_plot': 'Debt_Comparison'},
    'Debt_Stock_External': {'title': 'External Debt Stock', 'ylabel': 'Value (Local Currency)', 'combined_plot': 'Debt_Comparison'},
    'Overall_Deficit_GDP': {'title': 'Overall Fiscal Deficit to GDP Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'Revenue_GDP': {'title': 'Total Revenue to GDP Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'Expenditure_GDP': {'title': 'Total Expenditure to GDP Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'NPL_Ratio': {'title': 'Non-Performing Loan Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'CAR_Ratio': {'title': 'Capital Adequacy Ratio', 'ylabel': 'Ratio (%)', 'format': '%', 'multiplier': 100},
    'Financial_Stability_Index': {'title': 'Financial Stability Index', 'ylabel': 'Index Value'},
    'Governance_Index': {'title': 'Overall Governance Index', 'ylabel': 'Index Value'},
    'FX_Reserves_Months': {'title': 'FX Reserves', 'ylabel': 'Months of Imports'},
}

def generate_plots(results_df: pd.DataFrame, output_dir: Path):
    """Generates and saves plots for key simulation variables.

    Args:
        results_df: DataFrame containing the simulation results, indexed by year.
        output_dir: Path object for the directory to save plots.

    Returns:
        A dictionary mapping variable names to their relative plot file paths.
    """
    plot_files = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    logging.info(f"Saving plots to: {output_dir}")

    combined_plots_done = set()

    for var, details in KEY_VARIABLES.items():
        if var not in results_df.columns:
            logging.warning(f"Variable '{var}' not found in results. Skipping plot.")
            continue

        # Check if column has numeric data and is not all NaN
        if pd.api.types.is_numeric_dtype(results_df[var]) and not results_df[var].isnull().all():
            # Handle combined plots
            combined_plot_id = details.get('combined_plot')
            if combined_plot_id and combined_plot_id in combined_plots_done:
                continue # Already plotted as part of a combined chart
            if combined_plot_id and combined_plot_id not in combined_plots_done:
                plt.figure(figsize=(10, 6))
                ax = plt.gca()
                plot_filename = f"{combined_plot_id}.png"
                plot_title = f"Debt Stock Comparison"
                ylabel = ''

                vars_in_combo = [v for v, d in KEY_VARIABLES.items() if d.get('combined_plot') == combined_plot_id]
                for combo_var in vars_in_combo:
                    if combo_var in results_df.columns and pd.api.types.is_numeric_dtype(results_df[combo_var]) and not results_df[combo_var].isnull().all():
                        data_to_plot = results_df[combo_var]
                        multiplier = KEY_VARIABLES[combo_var].get('multiplier', 1)
                        label = KEY_VARIABLES[combo_var].get('title', combo_var)
                        plt.plot(results_df.index, data_to_plot * multiplier, label=label)
                        # Use the ylabel from the first variable in the combo
                        if not ylabel:
                            ylabel = KEY_VARIABLES[combo_var].get('ylabel', 'Value')
                plt.title(plot_title)
                plt.xlabel("Year")
                plt.ylabel(ylabel)
                ax.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
                ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))
                plt.legend()
                plt.grid(True, linestyle='--', alpha=0.6)
                plt.tight_layout()

                plot_path = output_dir / plot_filename
                plt.savefig(plot_path)
                plt.close()

                plot_files[combined_plot_id] = f"plots/{plot_filename}"
                logging.info(f"Generated combined plot: {plot_filename}")
                combined_plots_done.add(combined_plot_id)
                continue # Move to next variable after handling combined plot

            # --- Regular plotting logic for non-combined variables ---
            try:
                plt.figure(figsize=(10, 6))
                data_to_plot = results_df[var]
                multiplier = details.get('multiplier', 1)

                plt.plot(results_df.index, data_to_plot * multiplier)

                plt.title(details['title'])
                plt.xlabel("Year")
                plt.ylabel(details['ylabel'])

                # Format Y-axis
                ax = plt.gca()
                if details.get('format') == '%':
                    ax.yaxis.set_major_formatter(mticker.PercentFormatter())
                else:
                    # Use ScalarFormatter with simplified scientific notation if numbers are large
                    ax.yaxis.set_major_formatter(mticker.ScalarFormatter(useMathText=True))
                    ax.ticklabel_format(style='sci', axis='y', scilimits=(0,0))

                plt.grid(True, linestyle='--', alpha=0.6)
                plt.tight_layout()

                # Use Path object for saving
                plot_filename = f"{var}.png"
                plot_path = output_dir / plot_filename
                plt.savefig(plot_path)
                plt.close() # Close the figure to free memory

                # Store relative path for HTML report
                plot_files[var] = f"plots/{plot_filename}" # Relative path from where HTML will be
                logging.info(f"Generated plot: {plot_filename}")

            except Exception as e:
                logging.error(f"Failed to generate plot for '{var}': {e}")
        else:
            logging.warning(f"Skipping plot for '{var}' due to non-numeric data or all NaN values.")

    return plot_files
