import random

class DevelopmentFinanceModel:
    """Model flows from development partners (aid, DFI lending)"""
    def __init__(self, config):
        """Initialize development finance parameters based on config."""
        self.config = config
        # Base levels (as % of GDP)
        self.initial_grant_aid_gdp = config.get('initial_grant_aid_gdp', 0.008)
        self.initial_dfi_net_lending_gdp = config.get('initial_dfi_net_lending_gdp', 0.015)
        # Sensitivities
        self.grant_global_factor_sensitivity = config.get('grant_global_factor_sens', 0.5) # Sensitivity to global aid environment
        self.dfi_lending_governance_sensitivity = config.get('dfi_lending_governance_sens', 0.3) # Better governance attracts more/better DFI lending
        self.absorption_capacity_sensitivity = config.get('absorption_capacity_sens', 0.4) # Link to PFM/governance for effective use
        
        # Internal State
        self.grant_aid = 0
        self.dfi_net_lending = 0
        # Could track cumulative DFI debt contribution if needed separately
        self.initialized = False

        print(f"DevelopmentFinanceModel Initialized (Grant/GDP: {self.initial_grant_aid_gdp:.1%}, DFI Lend/GDP: {self.initial_dfi_net_lending_gdp:.1%})")

    def _initialize_state(self, initial_gdp):
        """Set initial flows based on initial GDP."""
        self.grant_aid = self.initial_grant_aid_gdp * initial_gdp
        self.dfi_net_lending = self.initial_dfi_net_lending_gdp * initial_gdp
        self.initialized = True
        print(f"Development Finance Initialized: Grants={self.grant_aid:.1f}, DFI Net Lending={self.dfi_net_lending:.1f}")

    def _simulate_flows(self, year, state):
        """Simulate grant aid and DFI net lending for the year."""
        # TODO: Model specific DFI projects, concessionality, aid effectiveness impact
        gdp = state.get('economic_state', {}).get('gdp', 1)
        gdp_growth = state.get('economic_state', {}).get('gdp_growth', 0.05)
        governance_score = state.get('governance_state', {}).get('governance_index', 50) / 100 # Normalized 0-1
        pfm_level = state.get('governance_state', {}).get('pfm_reform_level', 0.4) # Proxy for absorption capacity

        # Simulate global aid environment factor (e.g., fluctuating donor budgets)
        global_aid_factor = random.uniform(0.90, 1.10)
        
        # Project Grants: Baseline growth + global factor + absorption capacity influence
        grant_growth_factor = (1 + gdp_growth * 0.2) # Base growth slightly linked to GDP
        grant_growth_factor *= (1 + (global_aid_factor - 1) * self.grant_global_factor_sensitivity)
        grant_growth_factor *= (1 + (pfm_level - 0.5) * self.absorption_capacity_sensitivity) # Better PFM helps absorb grants
        self.grant_aid *= grant_growth_factor
        self.grant_aid = max(0, self.grant_aid)

        # Project DFI Net Lending: Baseline growth + governance influence
        dfi_growth_factor = (1 + gdp_growth * 0.5) # Base growth linked to GDP/demand
        dfi_growth_factor *= (1 + (governance_score - 0.5) * self.dfi_lending_governance_sensitivity) # Better governance attracts DFI
        self.dfi_net_lending *= dfi_growth_factor
        self.dfi_net_lending = max(0, self.dfi_net_lending) # Net lending can be zero, but not negative here for simplicity

        print(f"Year {year}: Gov: {governance_score:.2f}, PFM: {pfm_level:.2f}, GlobalAidFactor: {global_aid_factor:.2f}")
        print(f"Year {year}: Projected Grants: {self.grant_aid:.1f}, DFI Net Lending: {self.dfi_net_lending:.1f}")


    def simulate_development_finance(self, year, state):
        """Project development finance flows and their potential impact for a given year."""
        print(f"--- Simulating Development Finance for Year {year} ---")

        if not self.initialized:
            initial_gdp = state.get('economic_state', {}).get('gdp', 0)
            if initial_gdp > 0:
                self._initialize_state(initial_gdp)
            else:
                print("Warning: Cannot initialize Development Finance, GDP not available.")
                return {}, 0, 0 # Return empty state, zero flows

        # 1. Simulate Grant and DFI flows
        self._simulate_flows(year, state)

        print(f"--- Year {year} Development Finance Simulation Complete ---")

        # Return the calculated flows
        dev_finance_outputs = {
            'grant_aid': self.grant_aid,
            'dfi_net_lending': self.dfi_net_lending
            # Add concessionality metric later if needed
        }
        return dev_finance_outputs
