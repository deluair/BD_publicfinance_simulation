class PolicyCoordinationModel:
    """Model coordination between fiscal and monetary authorities"""
    def __init__(self, config):
        """Initialize policy coordination parameters based on config."""
        self.config = config
        self.base_coordination_score = config.get('base_coordination_score', 0.6) # Scale 0-1
        self.conflict_threshold_inflation = config.get('conflict_threshold_inflation', 0.08) # High inflation threshold
        self.conflict_threshold_deficit = config.get('conflict_threshold_deficit', 0.05) # High deficit/GDP threshold
        self.conflict_impact = config.get('conflict_impact', -0.1) # Penalty for conflict
        self.institutional_impact = config.get('institutional_impact', 0.05) # Bonus for good institutions

        # Internal state
        self.current_coordination_score = self.base_coordination_score
        print(f"PolicyCoordinationModel Initialized (Score: {self.current_coordination_score:.2f})")

    def _assess_policy_conflict(self, year, state):
        """Check for potential conflicts between policy objectives."""
        # TODO: Model specific mechanisms (Fiscal council, MoF-BB meetings), financing constraints
        inflation = state.get('inflation', 0.07)
        deficit = state.get('deficit', 0)
        gdp = state.get('economic_state', {}).get('gdp', 1)
        deficit_gdp_ratio = deficit / gdp if gdp > 0 else 0

        potential_conflict = (inflation > self.conflict_threshold_inflation) and \
                           (deficit_gdp_ratio > self.conflict_threshold_deficit)

        if potential_conflict:
            print(f"Year {year}: Potential Policy Conflict Detected (Inflation: {inflation:.2%}, Deficit/GDP: {deficit_gdp_ratio:.2%})")
            return True
        else:
            return False

    def _assess_institutional_framework(self, year, state):
        """Assess the strength of the institutional framework for coordination."""
        # TODO: Use specific outputs from Governance model
        # Example: Use overall governance index or a dedicated coordination framework indicator
        governance_index = state.get('governance_index', 50)
        # Simple mapping: better governance implies better institutional framework for coordination
        framework_strength = governance_index / 100 # Normalize to 0-1
        print(f"Year {year}: Institutional Framework Strength (proxy): {framework_strength:.2f}")
        return framework_strength


    def simulate_coordination(self, year, state):
        """Project policy coordination effectiveness and outcomes for a given year."""
        print(f"--- Simulating Policy Coordination for Year {year} ---")

        # 1. Check for potential conflicts
        conflict_exists = self._assess_policy_conflict(year, state)

        # 2. Assess institutional strength
        framework_strength = self._assess_institutional_framework(year, state)

        # 3. Update coordination score
        # Start with previous score
        score_change = 0
        if conflict_exists:
            score_change += self.conflict_impact
        # Benefit from strong institutions (above a baseline, e.g., 0.5)
        if framework_strength > 0.5:
            score_change += self.institutional_impact * (framework_strength - 0.5) * 2 # Amplify effect

        self.current_coordination_score += score_change
        # Apply bounds (0 to 1)
        self.current_coordination_score = max(0.1, min(0.9, self.current_coordination_score)) # Bounds 0.1-0.9

        print(f"Year {year}: Updated Policy Coordination Score: {self.current_coordination_score:.2f}")
        print(f"--- Year {year} Policy Coordination Simulation Complete ---")

        return self.current_coordination_score
