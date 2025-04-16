import pandas as pd
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import datetime
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Custom filter for Jinja2 to format numbers nicely
def format_number(value):
    if isinstance(value, (int, float)):
        if np.isnan(value):
            return 'N/A'
        if abs(value) < 0.01 and abs(value) > 0: # Small numbers in sci notation
            return f"{value:.2e}"
        if abs(value) >= 1e6: # Large numbers in sci notation
             return f"{value:.2e}"
        if isinstance(value, float):
            return f"{value:,.3f}" # Floats with 3 decimal places
        return f"{value:,}" # Integers with commas
    return value # Return as is if not a number

def generate_html_report(results_df: pd.DataFrame,
                         plot_files: dict,
                         plot_titles: dict,
                         template_dir: Path,
                         template_name: str,
                         output_path: Path):
    """Generates an HTML report from simulation results and plots.

    Args:
        results_df: DataFrame containing the simulation results.
        plot_files: Dictionary mapping variable names to plot file paths (relative).
        plot_titles: Dictionary mapping variable names to reader-friendly titles.
        template_dir: Path object for the directory containing the Jinja2 template.
        template_name: Filename of the Jinja2 template.
        output_path: Path object for the output HTML report file.
    """
    logging.info(f"Generating HTML report at: {output_path}")

    env = Environment(loader=FileSystemLoader(template_dir))
    env.filters['format_number'] = format_number # Add custom filter
    template = env.get_template(template_name)

    # Prepare data for the template
    start_year = results_df.index.min()
    end_year = results_df.index.max()

    # Get summary for the final year, handling potential NaNs
    final_year_summary = results_df.loc[end_year].fillna('N/A').to_dict()

    context = {
        'start_year': start_year,
        'end_year': end_year,
        'final_year_summary': final_year_summary,
        'plot_files': plot_files,
        'plot_titles': plot_titles,
        'generation_date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }

    # Render the template
    try:
        html_content = template.render(context)

        # Save the rendered HTML
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info("HTML report generated successfully.")

    except Exception as e:
        logging.error(f"Failed to generate HTML report: {e}")

# Example usage (if run directly, assuming results exist)
if __name__ == '__main__':
    # This is placeholder logic for testing the reporting script directly
    # In practice, this will be called by the main simulation script
    project_root = Path(__file__).parent.parent
    results_file = project_root / 'results' / 'simulation_output.csv'
    template_dir = project_root / 'templates'
    output_html = project_root / 'results' / 'simulation_report.html'
    plots_dir = project_root / 'results' / 'plots'

    if results_file.exists():
        logging.info(f"Loading results from {results_file} for standalone report generation.")
        df = pd.read_csv(results_file, index_col=0)

        # Assume plots exist (or call visualization script first in a real scenario)
        # For this example, we just list potential plot files
        from visualization import KEY_VARIABLES # Import for titles
        example_plot_files = {var: f"plots/{var}.png" for var in KEY_VARIABLES if (plots_dir / f"{var}.png").exists()}

        generate_html_report(
            results_df=df,
            plot_files=example_plot_files,
            plot_titles={var: details['title'] for var, details in KEY_VARIABLES.items()},
            template_dir=template_dir,
            template_name='report_template.html',
            output_path=output_html
        )
    else:
        logging.warning(f"Results file {results_file} not found. Cannot generate standalone report.")
