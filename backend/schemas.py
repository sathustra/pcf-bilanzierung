from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class DataType(str, Enum):
    primary = "Primär"
    secondary = "Sekundär"


class LifeCycleStage(str, Enum):
    raw_material = "Rohstoffbereitstellung & Vorverarbeitung"
    manufacturing = "Herstellung"
    transport_storage = "Transport & Lagerung (intern/Inbound)"


class SubCategory(str, Enum):
    main_material = "Hauptmaterialgewinnung & Aufbereitung"
    auxiliaries = "Hilfsstoffe (Druckfarben Additive Trennmittel etc.)"
    packaging_product = "Verpackung (Primär/Produkt)"
    packaging_logistics = "Verpackung (Transport/Logistik)"
    inbound_transport = "Inbound Transport (LKW Schiff Bahn Luft)"
    internal_transport = "Innerbetrieblicher Transport (Stapler Lager)"
    electricity_grid = "Strom (Netz/Mix)"
    electricity_renewable = "Strom (Erneuerbar/Grün)"
    heat_steam = "Wärme & Dampf (Gas/Öl/Biomasse)"
    direct_emissions = "Direkte Prozessemissionen (Scope 1 / Kältemittel)"
    wastewater = "Kläranlage & Abwasser"
    production_waste = "Abfall Produktion"
    maintenance = "Wartung und Pflege"
    machine_parts = "Maschinenteile"


# ── Product ──────────────────────────────────────────────────────────────────

class ProductBase(BaseModel):
    product_name: str
    product_category: Optional[str] = None
    reference_unit: str
    annual_production: float
    weight_per_unit: float
    biogenic_carbon_content: float = 0.0
    scope: str = "Cradle-to-Gate"
    allocation_method: Optional[str] = None
    reference_year: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(ProductBase):
    pass


class ProductRead(ProductBase):
    id: int

    class Config:
        from_attributes = True


# ── EmissionFactor ────────────────────────────────────────────────────────────

class EmissionFactorBase(BaseModel):
    name: str
    ef_biogenic_co2: float = 0.0
    ef_luc_co2e: float = 0.0
    ef_fossil_co2e: float = 0.0
    unit: str
    database_source: Optional[str] = None
    reference_year: Optional[int] = None
    data_type: DataType = DataType.secondary
    ter: int = Field(default=3, ge=1, le=5)
    ger: int = Field(default=3, ge=1, le=5)
    tir: int = Field(default=3, ge=1, le=5)


class EmissionFactorCreate(EmissionFactorBase):
    pass


class EmissionFactorUpdate(EmissionFactorBase):
    pass


class EmissionFactorRead(EmissionFactorBase):
    id: int

    class Config:
        from_attributes = True


# ── Material ──────────────────────────────────────────────────────────────────

class MaterialEntryBase(BaseModel):
    position: Optional[int] = None
    designation: str
    supplier: Optional[str] = None
    batch_amount: float
    ef_id: int
    life_cycle_stage: LifeCycleStage
    sub_category: SubCategory


class MaterialEntryCreate(MaterialEntryBase):
    product_id: int


class MaterialEntryUpdate(MaterialEntryBase):
    pass


class MaterialEntryRead(MaterialEntryBase):
    id: int
    product_id: int
    emission_factor: Optional[EmissionFactorRead] = None

    class Config:
        from_attributes = True


# ── Energy ────────────────────────────────────────────────────────────────────

class EnergyEntryBase(BaseModel):
    energy_carrier: str
    process_step: Optional[str] = None
    batch_amount: float
    ef_id: int
    life_cycle_stage: LifeCycleStage
    sub_category: SubCategory


class EnergyEntryCreate(EnergyEntryBase):
    product_id: int


class EnergyEntryUpdate(EnergyEntryBase):
    pass


class EnergyEntryRead(EnergyEntryBase):
    id: int
    product_id: int
    emission_factor: Optional[EmissionFactorRead] = None

    class Config:
        from_attributes = True


# ── Transport ─────────────────────────────────────────────────────────────────

class TransportEntryBase(BaseModel):
    transport_type: Optional[str] = None
    from_location: Optional[str] = None
    to_location: Optional[str] = None
    distance_km: float
    transport_mode: Optional[str] = None
    batch_weight_kg: float
    ef_id: int
    life_cycle_stage: LifeCycleStage
    sub_category: SubCategory


class TransportEntryCreate(TransportEntryBase):
    product_id: int


class TransportEntryUpdate(TransportEntryBase):
    pass


class TransportEntryRead(TransportEntryBase):
    id: int
    product_id: int
    transport_performance_tkm: float = 0.0
    emission_factor: Optional[EmissionFactorRead] = None

    class Config:
        from_attributes = True


# ── Waste ─────────────────────────────────────────────────────────────────────

class WasteEntryBase(BaseModel):
    waste_type: str
    treatment: Optional[str] = None
    batch_amount: float
    ef_id: int
    life_cycle_stage: LifeCycleStage
    sub_category: SubCategory


class WasteEntryCreate(WasteEntryBase):
    product_id: int


class WasteEntryUpdate(WasteEntryBase):
    pass


class WasteEntryRead(WasteEntryBase):
    id: int
    product_id: int
    emission_factor: Optional[EmissionFactorRead] = None

    class Config:
        from_attributes = True


# ── Calculation Results ───────────────────────────────────────────────────────

class EmissionTriple(BaseModel):
    biogenic: float = 0.0
    luc: float = 0.0
    fossil: float = 0.0

    @property
    def total(self) -> float:
        return self.biogenic + self.luc + self.fossil


class CategoryResult(BaseModel):
    materials: EmissionTriple
    energy: EmissionTriple
    transport: EmissionTriple
    waste: EmissionTriple


class LifeCycleStageResult(BaseModel):
    stage: str
    biogenic: float
    luc: float
    fossil: float
    share_of_gwp_total: float = 0.0
    share_of_gwp_fossil: float = 0.0


class SubCategoryResult(BaseModel):
    sub_category: str
    life_cycle_stage: str
    biogenic: float
    luc: float
    fossil: float


class GWPIndicators(BaseModel):
    gwp_fossil: float
    gwp_biogenic_emissions: float
    gwp_biogenic_uptake: float
    gwp_luluc: float
    gwp_total: float


class DQRResult(BaseModel):
    dqr_score: float
    traffic_light: str
    primary_data_share: float


class PCFResult(BaseModel):
    product_id: int
    product_name: str
    reference_unit: str
    annual_production: float
    gwp_indicators: GWPIndicators
    category_results: CategoryResult
    lifecycle_results: List[LifeCycleStageResult]
    subcategory_results: List[SubCategoryResult]
    dqr: DQRResult
