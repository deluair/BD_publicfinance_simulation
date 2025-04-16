class SOEModel:
    """Model State-Owned Enterprise performance and fiscal impact"""
    def __init__(self, config):
        """Initialize SOE parameters based on config."""
        self.config = config
        self.initial_performance_index = config.get('initial_soe_performance', 0.4) # Scale 0-1
        self.initial_soe_debt_gdp = config.get('initial_soe_debt_gdp', 0.10) # SOE Debt as % of GDP
        self.gdp_growth_sensitivity = config.get('soe_gdp_sensitivity', 0.3)
        self.governance_sensitivity = config.get('soe_governance_sensitivity', 0.2)
        self.debt_drag_factor = config.get('soe_debt_drag', -0.1)
        self.dividend_payout_ratio = config.get('soe_dividend_payout', 0.2) # Payout ratio if profitable
        self.transfer_need_threshold = config.get('soe_transfer_threshold', 0.3) # Performance below which transfers are likely
        self.transfer_scale_factor = config.get('soe_transfer_scale', 0.01) # Transfers needed scale with poor performance (as % of SOE Debt)

        # Internal State
        self.performance_index = self.initial_performance_index
        self.soe_debt_stock = 0 # Will be initialized based on first year GDP
        self.initialized = False

        print(f"SOEModel Initialized (Initial Perf: {self.performance_index:.2f}, Debt/GDP: {self.initial_soe_debt_gdp:.2%})")

    def _initialize_debt(self, initial_gdp):
        """Set initial SOE debt based on initial GDP."""
        self.soe_debt_stock = self.initial_soe_debt_gdp * initial_gdp
        self.initialized = True
        print(f"SOE Debt Initialized: {self.soe_debt_stock:.2f}")

    def _update_financial_performance(self, year, state):
        """Simulate changes in SOE financial performance."""
        # TODO: Model SOE reforms, pricing policies, sector-specific issues
        gdp_growth = state.get('economic_state', {}).get('gdp_growth', 0.05)
        # Use overall governance index as a proxy for oversight quality
        governance_score = state.get('governance_state', {}).get('governance_index', 50) / 100 # Normalize 0-1
        
        # Performance changes based on growth, governance, and debt burden
        performance_change = (self.gdp_growth_sensitivity * gdp_growth) + \
                             (self.governance_sensitivity * (governance_score - 0.5)) # Relative to baseline governance
        
        # Debt drag - higher debt may reduce performance/increase costs
        current_debt_gdp = self.soe_debt_stock / state.get('economic_state', {}).get('gdp', 1) if state.get('economic_state', {}).get('gdp', 0) > 0 else 0
        performance_change += self.debt_drag_factor * (current_debt_gdp - self.initial_soe_debt_gdp) # Drag if debt ratio grows
        
        self.performance_index += performance_change
        # Apply bounds (0.1 to 0.9)
        self.performance_index = max(0.1, min(0.9, self.performance_index))
        print(f"Year {year}: GDP Growth: {gdp_growth:.2%}, Gov Score: {governance_score:.2f}, SOE Perf Index: {self.performance_index:.3f}")

    def _update_soe_debt(self, year, state, transfers_received, dividends_paid):
        """Update SOE debt stock based on performance and fiscal flows."""
        # TODO: Model interest payments on SOE debt explicitly
        # Simple: Assume poor performance leads to borrowing needs offset by transfers,
        # and good performance allows some debt reduction after dividends.
        implied_profit_loss = (self.performance_index - 0.5) * self.soe_debt_stock * 0.1 # Very crude proxy for profit/loss scale
        
        # Change in debt = -Profit/Loss + Transfers Received - Dividends Paid (assuming profit used for dividends/repayment)
        debt_change = -implied_profit_loss + transfers_received - dividends_paid
        self.soe_debt_stock += debt_change
        self.soe_debt_stock = max(0, self.soe_debt_stock) # Cannot be negative
        print(f"Year {year}: Implied P/L: {implied_profit_loss:.2f}, Transfers: {transfers_received:.2f}, Dividends: {dividends_paid:.2f}, SOE Debt: {self.soe_debt_stock:.2f}")

    def _calculate_fiscal_impact(self, year, state):
        """Calculate dividends paid to government or transfers needed from government."""
        dividends = 0
        transfers = 0
        if self.performance_index > 0.55: # If reasonably profitable
            # Calculate potential profit (again, crude proxy)
            potential_profit = (self.performance_index - 0.5) * self.soe_debt_stock * 0.1
            dividends = potential_profit * self.dividend_payout_ratio
        elif self.performance_index < self.transfer_need_threshold: # If performing poorly
            # Calculate required transfers based on how far below threshold
            performance_gap = self.transfer_need_threshold - self.performance_index
            transfers = performance_gap * self.transfer_scale_factor * self.soe_debt_stock
            
        print(f"Year {year}: Calculated SOE Dividends: {dividends:.2f}, Transfers Needed: {transfers:.2f}")
        return dividends, transfers


    def simulate_soe_sector(self, year, state):
        """Project SOE financial health and fiscal impact for a given year."""
        print(f"--- Simulating SOE Sector for Year {year} ---")

        if not self.initialized:
            initial_gdp = state.get('economic_state', {}).get('gdp', 0)
            if initial_gdp > 0:
                self._initialize_debt(initial_gdp)
            else:
                print("Warning: Cannot initialize SOE debt, GDP not available in state.")
                return 0, 0, 0 # Return zero impact if not initialized

        # 1. Update financial performance
        self._update_financial_performance(year, state)

        # 2. Calculate potential fiscal impact (dividends/transfers)
        dividends, transfers = self._calculate_fiscal_impact(year, state)

        # 3. Update SOE debt stock based on performance and fiscal flows
        self._update_soe_debt(year, state, transfers, dividends)

        print(f"--- Year {year} SOE Simulation Complete ---")

        # Return fiscal impact and SOE debt level
        return dividends, transfers, self.soe_debt_stock
