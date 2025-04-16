import numpy as np # For potential financial calculations

class DebtManagementModel:
    """Model public debt sustainability and management"""
    def __init__(self, config):
        """Initialize debt parameters based on config."""
        self.config = config
        # Load initial stock from config, ensure keys exist
        initial_stock = config.get('initial_debt_stock', {'total': 0, 'domestic': 0, 'external': 0})
        self.debt_stock = {
            'total': initial_stock.get('total', 0),
            'domestic': initial_stock.get('domestic', 0),
            'external': initial_stock.get('external', 0)
        }
        self.avg_interest_rate_domestic = config.get('avg_interest_rate_domestic', 0.08)
        self.avg_interest_rate_external = config.get('avg_interest_rate_external', 0.03)
        self.dsa_thresholds = config.get('dsa_thresholds', {'debt_to_gdp': 0.70})
        print("DebtManagementModel Initialized with stock:", self.debt_stock)

    def _calculate_debt_service(self, year, state):
        """Calculate interest and principal payments for the year."""
        # TODO: Model complex debt portfolio (maturities, interest rates, currency risk)
        # Simple calculation based on average rates and previous year's stock
        interest_domestic = self.debt_stock['domestic'] * self.avg_interest_rate_domestic
        interest_external = self.debt_stock['external'] * self.avg_interest_rate_external
        total_interest = interest_domestic + interest_external

        # Placeholder for principal repayment - assume a fixed fraction for simplicity
        principal_repayment_domestic = self.debt_stock['domestic'] * 0.05 # Example: 5% repaid annually
        principal_repayment_external = self.debt_stock['external'] * 0.03 # Example: 3% repaid annually
        total_principal_paid = principal_repayment_domestic + principal_repayment_external

        debt_service = {
            'interest_domestic': interest_domestic,
            'interest_external': interest_external,
            'total_interest': total_interest,
            'principal_domestic': principal_repayment_domestic,
            'principal_external': principal_repayment_external,
            'total_principal': total_principal_paid,
            'total_service': total_interest + total_principal_paid
        }
        print(f"Year {year}: Calculated Debt Service (Total): {debt_service['total_service']:.2f}")
        return debt_service

    def _update_debt_stock(self, year, state, debt_service, deficit_financing):
        """Update the debt stock based on new borrowing and repayments."""
        # TODO: Model financing mix (domestic vs external), market conditions, concessionality
        # Simple assumption: deficit financed proportionally to existing debt structure (or configurable)
        total_current_debt = self.debt_stock['total']
        if total_current_debt <= 0: # Avoid division by zero if starting with no debt
            domestic_share = 0.5
        else:
            domestic_share = self.debt_stock['domestic'] / total_current_debt
        
        new_borrowing_domestic = deficit_financing * domestic_share
        new_borrowing_external = deficit_financing * (1 - domestic_share)

        # Update stocks
        self.debt_stock['domestic'] += new_borrowing_domestic - debt_service['principal_domestic']
        self.debt_stock['external'] += new_borrowing_external - debt_service['principal_external']
        self.debt_stock['total'] = self.debt_stock['domestic'] + self.debt_stock['external']

        print(f"Year {year}: Updated Debt Stock (Total): {self.debt_stock['total']:.2f} (Dom: {self.debt_stock['domestic']:.2f}, Ext: {self.debt_stock['external']:.2f})")

    def _perform_dsa(self, year, state):
        """Perform basic Debt Sustainability Analysis."""
        # TODO: Implement comprehensive DSA framework (stress tests, thresholds for various indicators)
        gdp = state.get('economic_state', {}).get('gdp', 1) # Use 1 to avoid division by zero if GDP not available
        if gdp <= 0: gdp = 1

        debt_to_gdp = self.debt_stock['total'] / gdp
        total_revenue = state.get('total_revenue', 1) # Use 1 to avoid division by zero
        if total_revenue <= 0: total_revenue = 1

        debt_service = state.get('debt_service', {})
        debt_service_to_revenue = debt_service.get('total_service', 0) / total_revenue

        sustainability_metrics = {
            'debt_to_gdp': debt_to_gdp,
            'debt_service_to_revenue': debt_service_to_revenue,
            'breached_threshold': debt_to_gdp > self.dsa_thresholds.get('debt_to_gdp', 0.70)
        }
        print(f"Year {year}: DSA - Debt/GDP: {debt_to_gdp:.2%}, Service/Revenue: {debt_service_to_revenue:.2%}, Breached Threshold: {sustainability_metrics['breached_threshold']}")
        return sustainability_metrics


    def simulate_debt_dynamics(self, year, state, deficit_financing):
        """Project debt levels, composition, and sustainability for a given year."""
        print(f"--- Simulating Debt Dynamics for Year {year} ---")

        # 1. Calculate Debt Service based on previous year's stock
        # Assumes state passed contains previous year's debt stock implicitly via self.debt_stock
        debt_service = self._calculate_debt_service(year, state)

        # 2. Update Debt Stock based on financing needs and repayments
        self._update_debt_stock(year, state, debt_service, deficit_financing)

        # 3. Perform Basic DSA using updated stock and current economic/fiscal state
        # We need the *current* state (GDP, revenue) for DSA ratios
        # Pass the *updated* debt stock within the state for DSA calculation
        state_for_dsa = state.copy() # Avoid modifying the main loop's state directly here
        state_for_dsa['debt_stock'] = self.debt_stock # Use the just-updated stock
        state_for_dsa['debt_service'] = debt_service # Use the just-calculated service
        sustainability_metrics = self._perform_dsa(year, state_for_dsa)

        print(f"--- Year {year} Debt Simulation Complete ---")
        # Return the updated debt stock (dict) and the sustainability metrics (dict)
        # Also return the calculated debt service for this year, as it's needed for fiscal calculations
        return self.debt_stock, sustainability_metrics, debt_service
