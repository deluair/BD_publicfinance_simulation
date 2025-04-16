# src/models/revenue.py
import pandas as pd # Assuming we might use pandas for structured data later

class RevenueModel:
    """Model revenue collection mechanisms and potential"""
    def __init__(self, config):
        """Initialize revenue system parameters based on config."""
        self.config = config
        self.tax_structure = config.get('tax_structure', {})
        self.admin_capacity = config.get('admin_capacity', {})
        self.compliance_params = config.get('compliance_params', {})
        self.economic_structure = config.get('economic_structure', {})
        self.informality_metrics = config.get('informality_metrics', {})
        self.enforcement_caps = config.get('enforcement_caps', {})

        # Potential state variables internal to the model, updated annually
        self.current_compliance_rate = self.compliance_params.get('initial_compliance', 0.6)
        self.current_admin_efficiency = self.admin_capacity.get('initial_efficiency', 0.7)
        self.formal_sector_share = 1.0 - self.informality_metrics.get('initial_share', 0.3)

        print("RevenueModel Initialized")

    def _calculate_tax_potential(self, year, economic_state):
        """Estimate potential revenue based purely on economic activity and tax structure."""
        # TODO: Implement detailed calculations based on tax types (VAT, Income, Corp, Trade etc.)
        # Example: Use GDP, consumption, imports/exports from economic_state
        gdp = economic_state.get('gdp', 0)
        potential_vat = gdp * 0.4 * self.tax_structure.get('vat_rate', 0.15) # Simplified: 40% of GDP is VAT base
        potential_income_tax = gdp * 0.3 * self.tax_structure.get('avg_income_tax_rate', 0.10) # Simplified
        potential_corp_tax = gdp * 0.2 * self.tax_structure.get('avg_corp_tax_rate', 0.25) # Simplified
        potential_trade_tax = economic_state.get('imports', gdp*0.2) * self.tax_structure.get('avg_trade_tax', 0.05) # Simplified
        # Add other taxes (property, excise etc.)
        potential_revenue = potential_vat + potential_income_tax + potential_corp_tax + potential_trade_tax
        print(f"Year {year}: Potential Revenue (Est.): {potential_revenue:.2f}")
        return potential_revenue

    def _apply_structural_constraints(self, year, potential_revenue, economic_state):
        """Adjust potential revenue for structural factors like informality."""
        # TODO: Implement impact of informality, sector composition, etc.
        # Example: Reduce potential based on informal sector size
        constrained_revenue = potential_revenue * self.formal_sector_share
        # TODO: Add effects of digital economy, agriculture taxation policy, etc.
        print(f"Year {year}: Revenue after Structural Constraints: {constrained_revenue:.2f}")
        return constrained_revenue

    def _apply_administrative_capacity(self, year, constrained_revenue):
        """Adjust revenue based on the capacity of the tax administration."""
        # TODO: Model NBR modernization, audit capacity, IT systems etc.
        # Example: Use an efficiency factor derived from admin_capacity config/state
        admin_factor = self.current_admin_efficiency # Use internal state
        collected_revenue = constrained_revenue * admin_factor
        print(f"Year {year}: Revenue after Admin Capacity Adjustment: {collected_revenue:.2f}")
        return collected_revenue

    def _apply_compliance_dynamics(self, year, collected_revenue):
        """Adjust revenue based on taxpayer compliance levels."""
        # TODO: Model voluntary compliance, e-filing, enforcement impact etc.
        # Example: Use a compliance factor derived from compliance_params config/state
        compliance_factor = self.current_compliance_rate # Use internal state
        final_revenue = collected_revenue * compliance_factor
        print(f"Year {year}: Final Revenue after Compliance Adjustment: {final_revenue:.2f}")
        return final_revenue

    def _update_internal_state(self, year, economic_state, governance_state):
        """Update internal state variables like compliance and admin efficiency for the next year."""
        # TODO: Implement logic for how compliance/efficiency evolves over time
        # This could depend on reforms (governance_state), investments, economic conditions etc.
        # Example: Slight improvement based on governance index
        if governance_state.get('nbr_modernization_level', 0) > self.current_admin_efficiency:
             self.current_admin_efficiency = min(1.0, self.current_admin_efficiency * 1.01) # Improve by 1% capped at 1.0

        # Example: Compliance improves slightly with GDP growth? (Needs better logic)
        if economic_state.get('gdp_growth', 0) > 0.05:
            self.current_compliance_rate = min(0.95, self.current_compliance_rate * 1.005) # Improve by 0.5% capped at 0.95

        print(f"Year {year} End: Updated Admin Efficiency: {self.current_admin_efficiency:.3f}, Compliance Rate: {self.current_compliance_rate:.3f}")


    def project_revenue(self, year, economic_state, governance_state):
        """Projects total revenue for a given year based on inputs."""
        # Note: Governance state influences admin capacity and compliance.
        print(f"--- Projecting Revenue for Year {year} ---")

        # 1. Calculate Tax Potential (Base)
        potential = self._calculate_tax_potential(year, economic_state)

        # 2. Adjust for structural constraints (e.g., informal economy)
        structurally_adjusted = self._apply_structural_constraints(year, potential, economic_state)

        # 3. Adjust for administrative capacity (how much can be realistically collected)
        admin_adjusted = self._apply_administrative_capacity(year, structurally_adjusted)

        # 4. Adjust for taxpayer compliance behavior
        final_revenue = self._apply_compliance_dynamics(year, admin_adjusted)

        # 5. Update Internal State (Admin Capacity, Compliance)
        self._update_internal_state(year, economic_state, governance_state)

        print(f"--- Year {year} Final Projected Revenue: {final_revenue:.2f} ---")
        # Return the final projected revenue in a dictionary
        return {'final_revenue': final_revenue}
