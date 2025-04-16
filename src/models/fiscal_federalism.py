class FiscalFederalismModel:
    """Model fiscal relations between central and subnational governments"""
    def __init__(self, config):
        """Initialize fiscal federalism parameters based on config."""
        self.config = config
        # Transfer rules
        self.transfer_ratio_central_revenue = config.get('transfer_ratio_central_revenue', 0.10) # % of central revenue transferred
        # Subnational Capacity & Performance
        self.initial_subnational_revenue_gdp = config.get('initial_subnational_revenue_gdp', 0.005) # Own revenue as % of GDP
        self.subnational_revenue_capacity_growth = config.get('subnational_revenue_capacity_growth', 0.01) # Annual improvement rate
        self.subnational_spending_efficiency = config.get('subnational_spending_efficiency', 0.8) # Efficiency of spending
        # Debt Rules
        self.subnational_debt_limit_gdp = config.get('subnational_debt_limit_gdp', 0.02) # Ceiling on aggregate debt
        
        # Internal State
        self.subnational_revenue_capacity_index = 1.0 # Starts at 1, grows over time
        self.total_transfers = 0
        self.total_subnational_own_revenue = 0
        self.total_subnational_spending = 0
        self.aggregate_subnational_debt = 0
        self.initialized = False

        print(f"FiscalFederalismModel Initialized (Transfer Ratio: {self.transfer_ratio_central_revenue:.1%}, Debt Limit: {self.subnational_debt_limit_gdp:.1%})")

    def _initialize_state(self, initial_gdp):
        """Set initial subnational revenue and debt based on GDP."""
        self.total_subnational_own_revenue = self.initial_subnational_revenue_gdp * initial_gdp
        # Assume initial debt is a fraction of the limit
        self.aggregate_subnational_debt = (self.subnational_debt_limit_gdp * initial_gdp) * 0.5 
        self.initialized = True
        print(f"Fiscal Federalism Initialized: OwnRev={self.total_subnational_own_revenue:.1f}, Debt={self.aggregate_subnational_debt:.1f}")

    def _calculate_central_transfers(self, year, state):
        """Calculate total transfers based on central government revenue."""
        # TODO: Model different types of transfers (conditional, unconditional), allocation formulas
        central_revenue = state.get('revenue_state', {}).get('final_revenue', 0)
        self.total_transfers = central_revenue * self.transfer_ratio_central_revenue
        print(f"Year {year}: Calculated Central Transfers: {self.total_transfers:.1f}")

    def _simulate_subnational_revenue(self, year, state):
        """Simulate aggregate subnational own-source revenue generation."""
        # TODO: Link to local economic activity, property values, specific local taxes
        # Simple model: capacity grows over time
        self.subnational_revenue_capacity_index *= (1 + self.subnational_revenue_capacity_growth)
        # Base revenue grows with nominal GDP, adjusted by capacity improvement
        gdp = state.get('economic_state', {}).get('gdp', 1)
        if not self.initialized: # Use initial ratio if not initialized
             base_rev = gdp * self.initial_subnational_revenue_gdp
        else:
            # Assume previous revenue grows roughly with GDP + capacity factor
             gdp_growth = state.get('economic_state', {}).get('gdp_growth', 0.05)
             inflation = state.get('inflation', 0.06) # Use overall inflation as proxy
             nominal_gdp_growth = (1+gdp_growth)*(1+inflation) - 1
             base_rev = self.total_subnational_own_revenue * (1 + nominal_gdp_growth + self.subnational_revenue_capacity_growth)

        self.total_subnational_own_revenue = base_rev # Simplified update
        self.total_subnational_own_revenue = max(0, self.total_subnational_own_revenue)
        print(f"Year {year}: Subnational Capacity Index: {self.subnational_revenue_capacity_index:.3f}, Own Revenue: {self.total_subnational_own_revenue:.1f}")

    def _simulate_subnational_spending(self, year, state):
        """Simulate aggregate subnational spending based on available resources."""
        # TODO: Differentiate spending types (dev vs recurrent), link to service delivery outcomes
        available_resources = self.total_transfers + self.total_subnational_own_revenue
        # Simple: Assume they spend most of their available resources, adjusted by efficiency
        potential_spending = available_resources * 0.95 # Assume they try to spend 95%
        self.total_subnational_spending = potential_spending * self.subnational_spending_efficiency
        self.total_subnational_spending = max(0, self.total_subnational_spending)
        print(f"Year {year}: Available Resources: {available_resources:.1f}, Subnational Spending: {self.total_subnational_spending:.1f}")

    def _update_subnational_debt(self, year, state):
        """Update aggregate subnational debt based on subnational fiscal balance."""
        # TODO: Model interest on subnational debt, central govt guarantees/bailouts
        subnational_deficit = self.total_subnational_spending - (self.total_transfers + self.total_subnational_own_revenue)
        
        # Calculate potential new borrowing
        new_borrowing = max(0, subnational_deficit) # Only borrow if deficit exists
        
        # Check against debt limit
        gdp = state.get('economic_state', {}).get('gdp', 1)
        debt_limit_amount = self.subnational_debt_limit_gdp * gdp
        allowed_borrowing = max(0, debt_limit_amount - self.aggregate_subnational_debt)
        
        actual_borrowing = min(new_borrowing, allowed_borrowing)
        
        # Update debt stock (simple increase by actual borrowing, ignores repayments for now)
        self.aggregate_subnational_debt += actual_borrowing
        self.aggregate_subnational_debt = max(0, self.aggregate_subnational_debt)
        print(f"Year {year}: Subnational Deficit: {subnational_deficit:.1f}, Actual Borrowing: {actual_borrowing:.1f}, Aggregate Debt: {self.aggregate_subnational_debt:.1f}")


    def simulate_fiscal_federalism(self, year, state):
        """Project intergovernmental fiscal dynamics for a given year."""
        print(f"--- Simulating Fiscal Federalism for Year {year} ---")

        if not self.initialized:
            initial_gdp = state.get('economic_state', {}).get('gdp', 0)
            if initial_gdp > 0:
                self._initialize_state(initial_gdp)
            else:
                print("Warning: Cannot initialize Fiscal Federalism, GDP not available.")
                return {}, 0 # Return empty state and zero debt

        # 1. Calculate Central Transfers
        self._calculate_central_transfers(year, state)

        # 2. Simulate Subnational Own Revenue
        self._simulate_subnational_revenue(year, state)

        # 3. Simulate Subnational Spending
        self._simulate_subnational_spending(year, state)

        # 4. Update Subnational Debt
        self._update_subnational_debt(year, state)

        print(f"--- Year {year} Fiscal Federalism Simulation Complete ---")

        # Return key indicators
        fiscal_federalism_outputs = {
            'total_transfers': self.total_transfers,
            'total_subnational_own_revenue': self.total_subnational_own_revenue,
            'total_subnational_spending': self.total_subnational_spending,
            'aggregate_subnational_debt': self.aggregate_subnational_debt
        }
        return fiscal_federalism_outputs
