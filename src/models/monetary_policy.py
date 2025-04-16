class MonetaryPolicyModel:
    """Model monetary policy implementation and effectiveness"""
    def __init__(self, config):
        """Initialize monetary policy parameters based on config."""
        self.config = config
        self.target_inflation = config.get('target_inflation_band', [0.04, 0.06]) # Target band
        self.policy_rate = config.get('initial_policy_rate', 0.06) # Proxy policy rate
        self.inflation_gap_weight = config.get('inflation_gap_weight', 1.5) # Taylor rule like weight
        self.policy_transmission_lag = config.get('policy_transmission_lag', 0.1) # How much policy rate affects inflation next period

        print(f"MonetaryPolicyModel Initialized (Target: {self.target_inflation}, Initial Rate: {self.policy_rate:.2%})")

    def _adjust_policy_rate(self, year, state):
        """Adjust the policy rate based on inflation deviation from target."""
        # TODO: Model policy instruments (repo, reserve req), transmission channels, FX intervention
        current_inflation = state.get('inflation', 0.07)
        inflation_target_midpoint = (self.target_inflation[0] + self.target_inflation[1]) / 2
        inflation_gap = current_inflation - inflation_target_midpoint

        # Simple Taylor-like rule for policy rate adjustment
        # Increase rate if inflation is above target, decrease if below
        rate_adjustment = self.inflation_gap_weight * inflation_gap
        self.policy_rate += rate_adjustment

        # Apply bounds to the policy rate (e.g., 1% to 15%)
        self.policy_rate = max(0.01, min(0.15, self.policy_rate))

        print(f"Year {year}: Current Inflation: {current_inflation:.2%}, Target Mid: {inflation_target_midpoint:.2%}, Adjusted Policy Rate: {self.policy_rate:.2%})")

    def _simulate_inflation_impact(self, year, state):
        """Simulate the lagged impact of policy rate changes on inflation."""
        # TODO: Model inflation expectations, supply shocks, exchange rate pass-through
        # Very simple model: higher policy rate reduces next period's inflation slightly
        # Assumes the 'inflation' in the state is the *current* year's inflation before this model runs
        # We calculate the *projected* inflation for the *end* of this year / start of next year
        
        current_inflation = state.get('inflation', 0.07)
        projected_inflation = current_inflation - (self.policy_transmission_lag * (self.policy_rate - 0.06)) # Effect relative to baseline rate (e.g., 6%)
        
        # Add some basic inertia/persistence
        projected_inflation = 0.8 * projected_inflation + 0.2 * current_inflation

        # Apply bounds (e.g., 0% to 20%)
        projected_inflation = max(0.00, min(0.20, projected_inflation))

        print(f"Year {year}: Projected Inflation for next period: {projected_inflation:.2%}")
        return projected_inflation


    def simulate_monetary_conditions(self, year, state):
        """Calculate monetary policy impacts and effectiveness for a given year."""
        print(f"--- Simulating Monetary Conditions for Year {year} ---")

        # 1. Adjust Policy Rate based on current inflation vs target
        self._adjust_policy_rate(year, state)

        # 2. Simulate the impact on next period's inflation
        projected_inflation = self._simulate_inflation_impact(year, state)

        print(f"--- Year {year} Monetary Conditions Simulation Complete ---")

        # Return the adjusted policy rate and the projected inflation for the *next* period
        return self.policy_rate, projected_inflation
