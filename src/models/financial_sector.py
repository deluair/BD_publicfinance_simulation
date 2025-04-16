class FinancialSectorModel:
    """Model financial sector health and stability"""
    def __init__(self, config):
        """Initialize financial sector parameters based on config."""
        self.config = config
        # Initial state values from config
        self.npl_ratio = config.get('initial_npl_ratio', 0.11)
        self.capital_adequacy_ratio = config.get('initial_car', 0.12)
        self.required_car = config.get('required_car', 0.10) # Regulatory minimum
        # Sensitivity parameters (how much NPLs react to GDP/Supervision)
        self.npl_gdp_sensitivity = config.get('npl_gdp_sensitivity', -0.5) # Higher growth reduces NPLs
        self.npl_supervision_sensitivity = config.get('npl_supervision_sensitivity', -0.2) # Better supervision reduces NPLs

        print(f"FinancialSectorModel Initialized (NPL: {self.npl_ratio:.2%}, CAR: {self.capital_adequacy_ratio:.2%})")

    def _update_npls(self, year, state):
        """Simulate changes in Non-Performing Loans ratio."""
        # TODO: Model credit growth, sector exposures, loan classification/resolution policies
        gdp_growth = state.get('economic_state', {}).get('gdp_growth', 0.06)
        supervision_effectiveness = state.get('supervision_effectiveness', 0.7) # 0-1 scale

        # Change in NPL ratio based on GDP growth and supervision (simplified)
        delta_npl_gdp = self.npl_gdp_sensitivity * (gdp_growth - 0.04) # Change relative to a baseline growth (e.g., 4%)
        delta_npl_supervision = self.npl_supervision_sensitivity * (supervision_effectiveness - 0.6) # Change relative to baseline supervision (e.g., 0.6)

        # Apply changes, keeping NPLs non-negative
        self.npl_ratio += delta_npl_gdp + delta_npl_supervision
        self.npl_ratio = max(0.01, self.npl_ratio) # Floor NPLs at 1%

        print(f"Year {year}: Updated NPL Ratio: {self.npl_ratio:.2%}")

    def _update_capital_adequacy(self, year, state):
        """Simulate changes in Capital Adequacy Ratio."""
        # TODO: Model bank profitability, capital injections, risk-weighted asset growth
        # Simple model: CAR decreases if NPLs rise significantly, increases slightly otherwise
        if self.npl_ratio > 0.15: # If NPLs are high
            self.capital_adequacy_ratio *= 0.98 # CAR erodes
        else:
            self.capital_adequacy_ratio *= 1.01 # CAR improves slightly

        # Ensure CAR doesn't go below a minimum realistic level or excessively high
        self.capital_adequacy_ratio = max(0.05, min(0.25, self.capital_adequacy_ratio))

        print(f"Year {year}: Updated Capital Adequacy Ratio: {self.capital_adequacy_ratio:.2%}")

    def _calculate_stability_index(self, year):
        """Calculate a simple financial stability index."""
        # TODO: Incorporate more indicators (liquidity, market volatility, credit growth)
        # Example: Weighted average of NPL (lower is better) and CAR buffer (higher is better)
        npl_score = max(0, 1 - (self.npl_ratio / 0.20)) # Score 1 if NPL=0, 0 if NPL=20% or more
        car_buffer = self.capital_adequacy_ratio - self.required_car
        car_score = max(0, min(1, car_buffer / 0.05)) # Score 1 if buffer is 5% or more, 0 if below required

        # Simple weighted index
        stability_index = (0.6 * npl_score) + (0.4 * car_score)

        print(f"Year {year}: Financial Stability Index: {stability_index:.2f}")
        return stability_index

    def simulate_financial_system(self, year, state):
        """Project financial sector conditions and stability for a given year."""
        print(f"--- Simulating Financial System for Year {year} ---")

        # 1. Update NPLs based on economic state and supervision
        self._update_npls(year, state)

        # 2. Update Capital Adequacy based on NPLs (simplified)
        self._update_capital_adequacy(year, state)

        # 3. Calculate Overall Stability Index
        stability_index = self._calculate_stability_index(year)

        print(f"--- Year {year} Financial System Simulation Complete ---")

        # Return updated key metrics as a dictionary
        return {
            'npl_ratio': self.npl_ratio,
            'capital_adequacy_ratio': self.capital_adequacy_ratio,
            'stability_index': stability_index
        }

# Example usage (if run directly)
if __name__ == "__main__":
    # Example config
    config = {
        'initial_npl_ratio': 0.11,
        'initial_car': 0.12,
        'required_car': 0.10,
        'npl_gdp_sensitivity': -0.5,
        'npl_supervision_sensitivity': -0.2
    }

    # Initialize model
    model = FinancialSectorModel(config)

    # Simulate financial system for a year
    year = 2023
    state = {
        'economic_state': {'gdp_growth': 0.06},
        'supervision_effectiveness': 0.7
    }
    result = model.simulate_financial_system(year, state)
    print(result)
