from __future__ import annotations

from .acquisition import AcquisitionPricingAgent
from .bear_case import BearCaseAgent
from .bull_case import BullCaseAgent
from .debt import DebtCapitalMarketsAgent
from .exit_liquidity import ExitLiquidityAgent
from .insurance import InsuranceAgent
from .market import MarketFundamentalsAgent
from .portfolio import PortfolioManagerAgent
from .renovation import RenovationExecutionAgent
from .rental_comps import RentalCompsAgent
from .risk import RiskManagerAgent
from .sale_comps import SaleCompsAgent
from .taxes import TaxAndAssessmentAgent
from .tenant_demand import TenantDemandAgent
from .zoning import ZoningAndRegulatoryAgent
from .cash_flow_quality import CashFlowQualityAgent
from .expense_load import ExpenseLoadAgent
from .appreciation import AppreciationAssumptionAgent
from .neighborhood import NeighborhoodQualityAgent
from .property_condition import PropertyConditionAgent
from .lease_up import LeaseUpAgent
from .reserves import ReservePlanningAgent
from .environmental import EnvironmentalAgent
from .title_legal import TitleAndLegalAgent
from .sponsor_fit import SponsorFitAgent
from .property_management import PropertyManagementAgent
from .liquidity_stress import LiquidityStressAgent
from .data_quality import DataQualityAgent
from .ic_chair import InvestmentCommitteeChairAgent

DEFAULT_AGENT_REGISTRY = [
    AcquisitionPricingAgent,
    RentalCompsAgent,
    SaleCompsAgent,
    CashFlowQualityAgent,
    ExpenseLoadAgent,
    DebtCapitalMarketsAgent,
    TaxAndAssessmentAgent,
    InsuranceAgent,
    ReservePlanningAgent,
    RenovationExecutionAgent,
    PropertyConditionAgent,
    MarketFundamentalsAgent,
    NeighborhoodQualityAgent,
    TenantDemandAgent,
    LeaseUpAgent,
    ZoningAndRegulatoryAgent,
    EnvironmentalAgent,
    TitleAndLegalAgent,
    AppreciationAssumptionAgent,
    ExitLiquidityAgent,
    PropertyManagementAgent,
    SponsorFitAgent,
    DataQualityAgent,
    LiquidityStressAgent,
    RiskManagerAgent,
    BullCaseAgent,
    BearCaseAgent,
    PortfolioManagerAgent,
    InvestmentCommitteeChairAgent,
]


def build_default_agents():
    return [agent_cls() for agent_cls in DEFAULT_AGENT_REGISTRY]
