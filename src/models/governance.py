class GovernanceModel:
    """Model governance quality and institutional capability"""
    def __init__(self, config):
        """Initialize governance parameters based on config."""
        self.config = config
        # Initial levels (scale 0-1, higher is better)
        self.pfm_reform_level = config.get('initial_pfm_level', 0.4)
        self.nbr_capacity_level = config.get('initial_nbr_level', 0.5)
        self.central_bank_capacity = config.get('initial_cb_level', 0.6)
        self.anti_corruption_effectiveness = config.get('initial_ac_level', 0.3)
        self.accountability_score = config.get('initial_accountability_score', 0.4)
        # Add SOE, Subnational later if needed explicitly here

        # Factors influencing change (simple annual improvement rates)
        self.pfm_improvement_rate = config.get('pfm_improvement_rate', 0.015)
        self.nbr_improvement_rate = config.get('nbr_improvement_rate', 0.01)
        self.cb_improvement_rate = config.get('cb_improvement_rate', 0.005)
        self.ac_improvement_rate = config.get('ac_improvement_rate', 0.008)
        self.accountability_improvement_rate = config.get('accountability_improvement_rate', 0.012)

        # Overall Index Weights
        self.weights = config.get('governance_weights', {
            'pfm': 0.25,
            'nbr': 0.20,
            'cb': 0.15,
            'ac': 0.20,
            'accountability': 0.20
        })

        self.governance_index = 0 # Will be calculated
        print(f"GovernanceModel Initialized (PFM: {self.pfm_reform_level:.2f}, NBR: {self.nbr_capacity_level:.2f}, AC: {self.anti_corruption_effectiveness:.2f})")

    def _update_governance_areas(self, year, state):
        """Simulate the gradual evolution of different governance aspects."""
        # TODO: Model impact of specific reforms, political economy factors, external support
        # Simple linear improvement trend for now, capped at 0.95
        self.pfm_reform_level = min(0.95, self.pfm_reform_level + self.pfm_improvement_rate)
        self.nbr_capacity_level = min(0.95, self.nbr_capacity_level + self.nbr_improvement_rate)
        self.central_bank_capacity = min(0.95, self.central_bank_capacity + self.cb_improvement_rate)
        self.anti_corruption_effectiveness = min(0.95, self.anti_corruption_effectiveness + self.ac_improvement_rate)
        self.accountability_score = min(0.95, self.accountability_score + self.accountability_improvement_rate)

        print(f"Year {year}: Updated Governance Areas - PFM: {self.pfm_reform_level:.3f}, NBR: {self.nbr_capacity_level:.3f}, AC: {self.anti_corruption_effectiveness:.3f}, Acc: {self.accountability_score:.3f}")

    def _calculate_governance_index(self, year):
        """Calculate the overall governance index based on component levels."""
        # Weighted average of the components
        index = (self.pfm_reform_level * self.weights['pfm'] +
                 self.nbr_capacity_level * self.weights['nbr'] +
                 self.central_bank_capacity * self.weights['cb'] +
                 self.anti_corruption_effectiveness * self.weights['ac'] +
                 self.accountability_score * self.weights['accountability'])
        
        # Scale to 0-100 for easier interpretation (optional)
        self.governance_index = index * 100
        print(f"Year {year}: Calculated Overall Governance Index: {self.governance_index:.2f}")
        return self.governance_index


    def simulate_governance_evolution(self, year, state):
        """Project governance improvements and constraints for a given year."""
        print(f"--- Simulating Governance Evolution for Year {year} ---")

        # 1. Update the levels of individual governance areas
        self._update_governance_areas(year, state)

        # 2. Calculate the overall governance index
        index = self._calculate_governance_index(year)

        print(f"--- Year {year} Governance Simulation Complete ---")

        # Return the overall index and potentially the individual components if needed by other models
        governance_state_outputs = {
            'governance_index': index,
            'pfm_reform_level': self.pfm_reform_level,
            'nbr_modernization_level': self.nbr_capacity_level, # Use consistent name
            'central_bank_capacity': self.central_bank_capacity,
            'anti_corruption_effectiveness': self.anti_corruption_effectiveness,
            'accountability_score': self.accountability_score
        }
        return governance_state_outputs
