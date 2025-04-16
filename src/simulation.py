# src/simulation.py

import yaml
import pandas as pd
import numpy as np
import os
from pathlib import Path
from .visualization import generate_plots, KEY_VARIABLES
from .reporting import generate_html_report
import logging
import sys

# Import all model classes
from .models.revenue import RevenueModel
from .models.expenditure import ExpenditureModel
from .models.debt import DebtManagementModel
from .models.financial_sector import FinancialSectorModel
from .models.monetary_policy import MonetaryPolicyModel
from .models.policy_coordination import PolicyCoordinationModel
from .models.governance import GovernanceModel
from .models.supervision import SupervisionModel
from .models.soe import SOEModel
from .models.external_sector import ExternalSectorModel
from .models.fiscal_federalism import FiscalFederalismModel
from .models.development_finance import DevelopmentFinanceModel

class BangladeshPublicFinanceSimulation:
    def __init__(self, config_path):
        """Initializes the simulation environment.

        Args:
            config_path (str or Path): Path to the configuration YAML file.
        """
        print("Initializing Simulation...")
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
            print("Configuration loaded.")
        except FileNotFoundError:
            logging.error(f"Configuration file not found at: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logging.error(f"Error parsing configuration file: {e}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"An unexpected error occurred loading configuration: {e}")
            sys.exit(1)

        # Extract simulation parameters
        self.start_year = self.config['simulation']['start_year']
        self.end_year = self.config['simulation']['end_year']
        self.years = range(self.start_year, self.end_year + 1)

        # Initialize Models
        print("Initializing models...")
        self.revenue_model = RevenueModel(self.config['revenue_model'])
        self.expenditure_model = ExpenditureModel(self.config['expenditure_model'])
        self.debt_model = DebtManagementModel(self.config['debt_model'])
        self.financial_sector_model = FinancialSectorModel(self.config['financial_sector'])
        self.monetary_policy_model = MonetaryPolicyModel(self.config['monetary_policy'])
        self.policy_coord_model = PolicyCoordinationModel(self.config['policy_coordination'])
        self.governance_model = GovernanceModel(self.config['governance_model'])
        self.supervision_model = SupervisionModel(self.config['supervision_model'])
        self.soe_model = SOEModel(self.config['soe_model'])
        self.external_sector_model = ExternalSectorModel(self.config['external_sector'])
        self.fiscal_federalism_model = FiscalFederalismModel(self.config['fiscal_federalism'])
        self.dev_finance_model = DevelopmentFinanceModel(self.config['development_finance'])
        print("All models initialized.")

        # Initialize Simulation State
        self.state = self._initialize_state()
        
        # Results Storage
        self.results = {}
        print("Simulation initialized successfully.")

    def _initialize_state(self):
        """Initialize the state dictionary for the first year."""
        print("Initializing simulation state...")
        state = {
            'economic_state': {
                'gdp': self.config['simulation']['initial_gdp'],
                'gdp_growth': self.config['simulation']['initial_gdp_growth'],
                'real_gdp_growth': self.config['simulation']['base_real_gdp_growth'], # Start with base
            },
            'inflation': self.config['simulation']['initial_inflation'],
            # Add initial states from models where necessary (though many initialize internally)
            'debt_stock': self.config['debt_model']['initial_debt_gdp_ratio'] * self.config['simulation']['initial_gdp'],
            'npl_ratio': self.config['financial_sector']['initial_npl_ratio'],
            'fx_reserves': 0, # Will be set by external sector model init
            'soe_debt_stock': 0, # Will be set by SOE model init
            # Placeholder for model outputs from the previous year
            'governance_state': {},
            'revenue_state': {},
            'expenditure_state': {},
            'debt_state': {},
            'financial_sector_state': {},
            'monetary_policy_state': {},
            'policy_coordination_state': {},
            'supervision_state': {},
            'soe_state': {},
            'external_sector_state': {},
            'fiscal_federalism_state': {},
            'dev_finance_state': {},
            # Fiscal aggregates needed across models
            'deficit': 0,
            'primary_deficit': 0, 
        }
        print(f"Initial State: GDP={state['economic_state']['gdp']}, Inflation={state['inflation']}, Debt={state['debt_stock']}")
        return state

    def _update_economic_state(self, year):
        """Update basic macroeconomic variables like GDP and inflation."""
        # TODO: Make this more sophisticated - link growth to investment, external demand etc.
        # Simple GDP projection: Base real growth + adjustment based on previous year dynamics (if any)
        prev_real_growth = self.state['economic_state'].get('real_gdp_growth', self.config['simulation']['base_real_gdp_growth'])
        # Add some volatility or link to other factors later
        current_real_growth = self.config['simulation']['base_real_gdp_growth'] * (1 + np.random.normal(0, 0.05)) # Add noise
        
        # Simple inflation projection: Persistence + impact from monetary policy
        prev_inflation = self.state['inflation']
        monetary_policy_effect = self.state['monetary_policy_state'].get('projected_inflation_impact', 0) # How much MP affects this year's inflation
        # Projected inflation from monetary policy is for the *next* period, so we use previous state's projection if available
        if 'projected_inflation' in self.state['monetary_policy_state']:
             base_inflation = self.state['monetary_policy_state']['projected_inflation']
        else:
             base_inflation = prev_inflation * self.config['simulation']['inflation_persistence'] + \
                              (1 - self.config['simulation']['inflation_persistence']) * self.config['simulation']['initial_inflation'] # Revert to mean initially
        
        current_inflation = base_inflation # Incorporate MP effects here or directly in projection logic
        current_inflation = max(0.01, min(0.15, current_inflation)) # Bounds
        
        # Update GDP (Nominal)
        prev_gdp = self.state['economic_state']['gdp']
        current_gdp = prev_gdp * (1 + current_real_growth) * (1 + current_inflation)
        gdp_growth = (current_gdp / prev_gdp - 1) if prev_gdp > 0 else 0
        
        self.state['economic_state']['gdp'] = current_gdp
        self.state['economic_state']['gdp_growth'] = gdp_growth
        self.state['economic_state']['real_gdp_growth'] = current_real_growth
        self.state['inflation'] = current_inflation
        self.state['economic_state']['inflation_rate'] = current_inflation
        
        print(f"Year {year} Economic Update: Real Growth={current_real_growth:.2%}, Inflation={current_inflation:.2%}, GDP={current_gdp:.1f}")

    def run_single_year(self, year):
        """Run all models for a single year."""
        print(f"\n===== Running Simulation for Year {year} =====")
        
        # 0. Update basic economic state (GDP, Inflation)
        self._update_economic_state(year)
        
        # --- Run Models (Order Matters!) ---
        # 1. Governance (Influences many others)
        gov_outputs = self.governance_model.simulate_governance_evolution(year, self.state)
        self.state['governance_state'] = gov_outputs
        self.state.update(gov_outputs) # Make keys directly accessible if needed

        # 2. Supervision (Influences Financial Sector)
        sup_eff = self.supervision_model.simulate_supervision_effectiveness(year, self.state)
        self.state['supervision_state'] = {'supervision_effectiveness': sup_eff}
        self.state.update(self.state['supervision_state']) # Make key directly accessible
        
        # 3. Financial Sector (Influences Monetary Policy, Economy)
        fin_outputs = self.financial_sector_model.simulate_financial_system(year, self.state)
        self.state['financial_sector_state'] = fin_outputs
        self.state.update(fin_outputs) # Make NPL, CAR etc. directly accessible

        # 4. Monetary Policy (Influences Inflation, Coordination)
        mp_rate, proj_inf = self.monetary_policy_model.simulate_monetary_conditions(year, self.state)
        self.state['monetary_policy_state'] = {'policy_rate': mp_rate, 'projected_inflation': proj_inf}
        self.state.update(self.state['monetary_policy_state'])
        
        # 5. External Sector (Influences Reserves, Deficit Financing)
        ext_outputs = self.external_sector_model.simulate_external_sector(year, self.state)
        self.state['external_sector_state'] = ext_outputs
        self.state.update(ext_outputs) # Make reserves, BoP etc. directly accessible
        
        # 6. Development Finance (Influences Fiscal Space / Financing)
        dev_fin_outputs = self.dev_finance_model.simulate_development_finance(year, self.state)
        self.state['dev_finance_state'] = dev_fin_outputs
        self.state.update(dev_fin_outputs) # Make grants, DFI lending directly accessible

        # 7. Revenue Mobilization
        rev_outputs = self.revenue_model.project_revenue(year, self.state['economic_state'], self.state['governance_state'])
        self.state['revenue_state'] = rev_outputs
        self.state.update(rev_outputs) # Make final_revenue directly accessible
        final_revenue = rev_outputs['final_revenue']

        # 8. Fiscal Federalism (Transfers depend on Central Revenue)
        ff_outputs = self.fiscal_federalism_model.simulate_fiscal_federalism(year, self.state)
        self.state['fiscal_federalism_state'] = ff_outputs
        self.state.update(ff_outputs) # Make transfers etc. accessible
        transfers_to_subnational = ff_outputs['total_transfers']
        # Note: Central revenue available for central spending is reduced by transfers
        revenue_for_central_gov = final_revenue - transfers_to_subnational
        self.state['revenue_state']['revenue_for_central_gov'] = revenue_for_central_gov

        # 9. Expenditure Management (Central Gov Spending)
        # TODO: Refine budget_allocation logic - using revenue as proxy for now
        # TODO: Confirm state keys for capacity, accountability, political economy
        exp_outputs = self.expenditure_model.simulate_expenditure(
            year,
            budget_allocation=self.state.get('final_revenue', 0), # Proxy
            implementation_capacity=self.state['governance_state'].get('pfm_effectiveness', 0.5),
            accountability_mechanisms=self.state['governance_state'].get('accountability_index', 0.5),
            political_economy=self.state['governance_state'].get('governance_index', 0.5) # Proxy
        )
        self.state['expenditure_state'] = exp_outputs # Store the full output dict
        self.state.update(exp_outputs) # Make keys accessible, e.g., expenditure_efficiency
        # Calculate total realized spending from the details
        realized_central_spending = sum(exp_outputs.get('actual_spending', {}).values())

        # 10. SOE Sector (Fiscal impact depends on performance)
        soe_dividends, soe_transfers, soe_debt = self.soe_model.simulate_soe_sector(year, self.state)
        self.state['soe_state'] = {'dividends': soe_dividends, 'transfers_needed': soe_transfers, 'debt': soe_debt}
        self.state['soe_debt_stock'] = soe_debt # Update main state variable

        # --- Calculate Fiscal Aggregates ---
        # Total Revenue = Central Revenue (net of transfers) + SOE Dividends
        total_revenue_inc_soe = revenue_for_central_gov + soe_dividends
        # Total Expenditure = Realized Central Spending + Transfers to SOEs
        total_expenditure_inc_soe = realized_central_spending + soe_transfers
        
        # Overall Fiscal Deficit (Central Gov Perspective)
        deficit = total_expenditure_inc_soe - total_revenue_inc_soe
        self.state['deficit'] = deficit
        deficit_gdp = deficit / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] > 0 else 0
        print(f"Year {year} Fiscal Aggregates: Rev={total_revenue_inc_soe:.1f}, Exp={total_expenditure_inc_soe:.1f}, Deficit={deficit:.1f} ({deficit_gdp:.2%})")

        # 11. Debt Management (Deficit needs financing)
        updated_debt_stock, dsa_results, debt_service_calculated = self.debt_model.simulate_debt_dynamics(year, self.state, deficit)
        self.state['debt_stock'] = updated_debt_stock  # Update state with the returned stock
        self.state['dsa_results'] = dsa_results
        self.state['debt_service_calculated'] = debt_service_calculated # Store calculated service

        # --- Calculate Primary Deficit ---
        interest_payments = debt_service_calculated.get('total_interest_paid', 0)
        primary_deficit = deficit - interest_payments
        self.state['primary_deficit'] = primary_deficit
        primary_deficit_gdp = primary_deficit / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] > 0 else 0
        print(f"Year {year}: Interest={interest_payments:.1f}, Primary Deficit={primary_deficit:.1f} ({primary_deficit_gdp:.2%})")

        # 12. Policy Coordination (Assess based on outcomes)
        coord_score = self.policy_coord_model.simulate_coordination(year, self.state)
        self.state['policy_coordination_state'] = {'coordination_score': coord_score}

        # --- Store Results --- 
        self._store_results(year)
        print(f"===== Year {year} Simulation Complete =====")

    def _store_results(self, year):
        """Store key simulation results for the given year."""
        # Deep copy relevant parts of the state to avoid overwriting
        results_for_year = {
            # Economic
            'GDP': self.state['economic_state']['gdp'],
            'GDP_Growth': self.state['economic_state'].get('gdp_growth', np.nan),
            'Inflation': self.state['economic_state']['inflation_rate'],
            # Fiscal
            'Total_Revenue': self.state.get('total_revenue', np.nan),
            'Central_Revenue': self.state.get('central_revenue', np.nan),
            'Revenue_GDP': self.state.get('total_revenue', np.nan) / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            'Total_Expenditure': self.state.get('total_expenditure', np.nan),
            'Central_Expenditure': self.state.get('central_expenditure', np.nan),
            'Expenditure_GDP': self.state.get('total_expenditure', np.nan) / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            'Overall_Deficit': self.state['deficit'],
            'Primary_Deficit': self.state.get('primary_deficit', np.nan),
            'Overall_Deficit_GDP': self.state['deficit'] / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            'Primary_Deficit_GDP': self.state['primary_deficit'] / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            # Debt
            'Debt_Stock_Total': self.state.get('debt_stock', {}).get('total', np.nan),
            'Debt_Stock_Domestic': self.state.get('debt_stock', {}).get('domestic', np.nan),
            'Debt_Stock_External': self.state.get('debt_stock', {}).get('external', np.nan),
            'Debt_Stock_GDP': self.state.get('debt_stock', {}).get('total', np.nan) / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            'Debt_Service': self.state.get('debt_service_calculated', {}).get('total_service', np.nan),
            'Interest_Payments': self.state.get('debt_service_calculated', {}).get('total_interest_paid', np.nan),
            'DSA_Debt_GDP_Ratio': self.state.get('dsa_results', {}).get('debt_to_gdp', np.nan),
            'DSA_Service_Revenue_Ratio': self.state.get('dsa_results', {}).get('service_to_revenue', np.nan),
            # External
            'Exports': self.state['external_sector_state'].get('exports', np.nan),
            'Imports': self.state['external_sector_state'].get('imports', np.nan),
            'Remittances': self.state['external_sector_state'].get('remittances', np.nan),
            'FDI': self.state['external_sector_state'].get('fdi', np.nan),
            'CAB_GDP': self.state['external_sector_state'].get('cab_gdp', np.nan),
            'FX_Reserves_Months': self.state['external_sector_state'].get('reserves_months_imp', np.nan),
            # Governance & Other Indicators
            'Governance_Index': self.state['governance_index'],
            'PFM_Score': self.state['governance_state'].get('pfm_level', np.nan),
            'NBR_Score': self.state['governance_state'].get('nbr_capacity', np.nan),
            'AC_Score': self.state['governance_state'].get('anti_corruption_effectiveness', np.nan),
            'Accountability_Score': self.state['governance_state'].get('accountability_level', np.nan),
            'Financial_Stability_Index': self.state['financial_sector_state'].get('financial_stability_index', np.nan),
            'NPL_Ratio': self.state['financial_sector_state'].get('npl_ratio', np.nan),
            'CAR_Ratio': self.state['financial_sector_state'].get('capital_adequacy_ratio', np.nan),
            'Policy_Rate': self.state.get('policy_rate', np.nan),
            'Supervision_Effectiveness': self.state.get('supervision_effectiveness', np.nan),
            'SOE_Performance': self.state.get('soe_state', {}).get('performance_index', np.nan),
            'SOE_Debt_GDP': self.state.get('soe_state', {}).get('debt', np.nan) / self.state['economic_state']['gdp'] if self.state['economic_state']['gdp'] else np.nan,
            'Subnational_Own_Revenue': self.state.get('fiscal_federalism_state', {}).get('own_revenue', np.nan),
            'Subnational_Debt': self.state.get('fiscal_federalism_state', {}).get('aggregate_debt', np.nan),
            'Grant_Receipts': self.state.get('development_finance_state', {}).get('grants', np.nan),
            'DFI_Lending': self.state.get('development_finance_state', {}).get('dfi_net_lending', np.nan),
            'Expenditure_Efficiency': self.state.get('expenditure_outputs', {}).get('expenditure_efficiency', np.nan),
            'Policy_Coordination_Score': self.state.get('policy_coordination_score', np.nan),
        }
        self.results[year] = results_for_year

    def run_simulation(self):
        """Run the simulation over the entire period."""
        print(f"\nStarting Simulation from {self.start_year} to {self.end_year}...")
        for year in self.years:
            self.run_single_year(year)
        print("\nSimulation Run Complete.")
        # Convert results to DataFrame
        df = pd.DataFrame.from_dict(self.results, orient='index')
        # Optionally reorder columns
        # desired_order = [...] 
        # df = df[desired_order]
        print("Simulation Results:")
        print(df.head().to_string()) # Print head to avoid excessive output
        return df

    def save_results(self, output_path='../results/simulation_results.csv'):
        """Save the results DataFrame to a CSV file."""
        # Create results directory if it doesn't exist
        output_dir = os.path.dirname(output_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created results directory: {output_dir}")
            
        self.results.to_csv(output_path)
        print(f"Results saved to {output_path}")

def main():
    config_path = os.path.join('config', 'config.yaml')
    project_root = Path(__file__).parent.parent # Get project root directory
    results_dir = project_root / 'results'
    plots_dir = results_dir / 'plots'
    template_dir = project_root / 'templates'
    report_output_path = results_dir / 'simulation_report.html'
    results_output_path = results_dir / 'simulation_output.csv'

    # Ensure results directory exists
    results_dir.mkdir(parents=True, exist_ok=True)

    simulation = BangladeshPublicFinanceSimulation(config_path)
    results_df = simulation.run_simulation()

    if results_df is not None and not results_df.empty:
        # Save raw results
        results_df.to_csv(results_output_path)
        print(f"\nSimulation results saved to: {results_output_path}")

        # Print summary of the final year
        print("\nSimulation Results Summary (Final Year):")
        print(results_df.iloc[-1].to_string())

        # Generate Visualizations
        print("\nGenerating visualizations...")
        try:
            plot_files = generate_plots(results_df, plots_dir)
            plot_titles = {var: details['title'] for var, details in KEY_VARIABLES.items()}
            print(f"Visualizations saved in: {plots_dir}")

            # Generate HTML Report
            print("\nGenerating HTML report...")
            generate_html_report(
                results_df=results_df,
                plot_files=plot_files,
                plot_titles=plot_titles,
                template_dir=template_dir,
                template_name='report_template.html',
                output_path=report_output_path
            )
            print(f"HTML report saved to: {report_output_path}")

        except Exception as e:
            logging.error(f"Failed during post-processing (visualization/reporting): {e}")

    else:
        print("Simulation did not produce results. Skipping post-processing.")

if __name__ == "__main__":
    # Add src to path to allow running as a module
    # sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    main()
