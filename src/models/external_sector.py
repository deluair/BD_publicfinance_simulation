import random

class ExternalSectorModel:
    """Model external sector dynamics including trade, remittances, FDI, and reserves"""
    def __init__(self, config):
        """Initialize external sector parameters based on config."""
        self.config = config
        # Initial Ratios (as % of GDP)
        self.initial_export_gdp = config.get('initial_export_gdp', 0.15)
        self.initial_import_gdp = config.get('initial_import_gdp', 0.22)
        self.initial_remittance_gdp = config.get('initial_remittance_gdp', 0.05)
        self.initial_fdi_gdp = config.get('initial_fdi_gdp', 0.01)
        self.initial_reserves_months_import = config.get('initial_reserves_months_import', 5.0)

        # Sensitivities
        self.export_global_growth_sensitivity = config.get('export_global_growth_sens', 1.5)
        self.import_domestic_growth_sensitivity = config.get('import_domestic_growth_sens', 1.2)
        self.remittance_global_growth_sensitivity = config.get('remittance_global_growth_sens', 0.8)
        self.fdi_governance_sensitivity = config.get('fdi_governance_sens', 0.05)
        # Global economic condition proxy (simple multiplier)
        self.global_growth_factor = config.get('global_growth_factor', 1.02) # Base 2% global growth impact

        # Internal State
        self.exports = 0
        self.imports = 0
        self.remittances = 0
        self.fdi = 0
        self.current_account_balance = 0
        self.financial_account_balance = 0 # Simplified: includes FDI and other flows
        self.overall_bop = 0
        self.fx_reserves = 0
        self.initialized = False

        print(f"ExternalSectorModel Initialized (Exp/GDP: {self.initial_export_gdp:.1%}, Imp/GDP: {self.initial_import_gdp:.1%}, Res: {self.initial_reserves_months_import:.1f}m)")

    def _initialize_state(self, initial_gdp):
        """Set initial flows and reserves based on initial GDP."""
        self.exports = self.initial_export_gdp * initial_gdp
        self.imports = self.initial_import_gdp * initial_gdp
        self.remittances = self.initial_remittance_gdp * initial_gdp
        self.fdi = self.initial_fdi_gdp * initial_gdp
        # Initial reserves based on initial import level
        self.fx_reserves = self.imports * (self.initial_reserves_months_import / 12.0)
        self.initialized = True
        print(f"External Sector Initialized: Exp={self.exports:.1f}, Imp={self.imports:.1f}, Rem={self.remittances:.1f}, FDI={self.fdi:.1f}, Res={self.fx_reserves:.1f}")

    def _project_flows(self, year, state):
        """Project exports, imports, remittances, and FDI."""
        # TODO: Model exchange rate impacts, competitiveness, trade policy, specific shocks
        gdp = state.get('economic_state', {}).get('gdp', 1)
        gdp_growth = state.get('economic_state', {}).get('gdp_growth', 0.05)
        governance_score = state.get('governance_state', {}).get('governance_index', 50) / 100 # Normalized 0-1
        
        # Simple growth projections based on sensitivities
        # Assume flows grow relative to previous year's base adjusted by sensitivities
        global_factor = random.uniform(0.98, 1.05) # Simulate fluctuating global conditions slightly
        
        self.exports *= (1 + gdp_growth * 0.5 + (global_factor - 1) * self.export_global_growth_sensitivity)
        self.imports *= (1 + gdp_growth * self.import_domestic_growth_sensitivity)
        self.remittances *= (1 + (global_factor - 1) * self.remittance_global_growth_sensitivity)
        # FDI sensitive to governance improvements
        self.fdi *= (1 + gdp_growth + self.fdi_governance_sensitivity * (governance_score - 0.5))
        
        # Ensure non-negative flows
        self.exports = max(0, self.exports)
        self.imports = max(0, self.imports)
        self.remittances = max(0, self.remittances)
        self.fdi = max(0, self.fdi)
        
        print(f"Year {year}: Projected Flows - Exp: {self.exports:.1f}, Imp: {self.imports:.1f}, Rem: {self.remittances:.1f}, FDI: {self.fdi:.1f}")

    def _calculate_bop(self, year, state):
        """Calculate Current Account Balance (CAB) and Overall Balance of Payments (BoP)."""
        # TODO: Model services trade, income balance, capital flows (portfolio, loans)
        # Simplified CAB = Trade Balance + Remittances
        trade_balance = self.exports - self.imports
        self.current_account_balance = trade_balance + self.remittances

        # Simplified Financial Account = FDI (assuming other flows net to zero or are captured implicitly)
        self.financial_account_balance = self.fdi
        
        # Simplified Overall BoP = CAB + Financial Account Balance (+ errors/omissions assumed zero)
        self.overall_bop = self.current_account_balance + self.financial_account_balance

        print(f"Year {year}: BoP Calculation - CAB: {self.current_account_balance:.1f}, FinAcc: {self.financial_account_balance:.1f}, Overall BoP: {self.overall_bop:.1f}")

    def _update_reserves(self, year):
        """Update FX reserves based on the overall BoP."""
        # TODO: Model valuation changes, reserve management costs/income
        self.fx_reserves += self.overall_bop
        # Reserves cannot go below zero (or some minimum threshold)
        self.fx_reserves = max(0, self.fx_reserves)
        
        # Calculate reserves in months of imports for reporting
        months_of_imports = (self.fx_reserves / (self.imports / 12.0)) if self.imports > 0 else 0
        print(f"Year {year}: Updated FX Reserves: {self.fx_reserves:.1f} ({months_of_imports:.1f} months of imports)")
        return months_of_imports

    def simulate_external_sector(self, year, state):
        """Project external flows, BoP, and reserves for a given year."""
        print(f"--- Simulating External Sector for Year {year} ---")

        if not self.initialized:
            initial_gdp = state.get('economic_state', {}).get('gdp', 0)
            if initial_gdp > 0:
                self._initialize_state(initial_gdp)
            else:
                print("Warning: Cannot initialize External Sector, GDP not available in state.")
                return {}, 0 # Return empty dict and zero reserves

        # 1. Project flows for the year
        self._project_flows(year, state)

        # 2. Calculate Balance of Payments components
        self._calculate_bop(year, state)

        # 3. Update FX Reserves based on BoP
        months_of_imports = self._update_reserves(year)

        print(f"--- Year {year} External Sector Simulation Complete ---")

        # Return key external sector indicators
        external_sector_outputs = {
            'exports': self.exports,
            'imports': self.imports,
            'remittances': self.remittances,
            'fdi': self.fdi,
            'current_account_balance': self.current_account_balance,
            'overall_bop': self.overall_bop,
            'fx_reserves': self.fx_reserves,
            'reserves_months_imports': months_of_imports
        }
        return external_sector_outputs
