from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
import enum


class DataType(str, enum.Enum):
    primary = "Primär"
    secondary = "Sekundär"


class LifeCycleStage(str, enum.Enum):
    raw_material = "Rohstoffbereitstellung & Vorverarbeitung"
    manufacturing = "Herstellung"
    transport_storage = "Transport & Lagerung (intern/Inbound)"


class SubCategory(str, enum.Enum):
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


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(255), nullable=False)
    product_category = Column(String(255))
    reference_unit = Column(String(50), nullable=False)
    annual_production = Column(Float, nullable=False)
    weight_per_unit = Column(Float, nullable=False)
    biogenic_carbon_content = Column(Float, default=0.0)
    scope = Column(String(100), default="Cradle-to-Gate")
    allocation_method = Column(String(255))
    reference_year = Column(Integer)

    materials = relationship("MaterialEntry", back_populates="product", cascade="all, delete-orphan")
    energy_entries = relationship("EnergyEntry", back_populates="product", cascade="all, delete-orphan")
    transport_entries = relationship("TransportEntry", back_populates="product", cascade="all, delete-orphan")
    waste_entries = relationship("WasteEntry", back_populates="product", cascade="all, delete-orphan")


class EmissionFactor(Base):
    __tablename__ = "emission_factors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    ef_biogenic_co2 = Column(Float, default=0.0)
    ef_luc_co2e = Column(Float, default=0.0)
    ef_fossil_co2e = Column(Float, default=0.0)
    unit = Column(String(50), nullable=False)
    database_source = Column(String(255))
    reference_year = Column(Integer)
    data_type = Column(Enum(DataType), default=DataType.secondary)
    ter = Column(Integer, default=3)
    ger = Column(Integer, default=3)
    tir = Column(Integer, default=3)


class MaterialEntry(Base):
    __tablename__ = "material_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    position = Column(Integer)
    designation = Column(String(255), nullable=False)
    supplier = Column(String(255))
    batch_amount = Column(Float, nullable=False)
    ef_id = Column(Integer, ForeignKey("emission_factors.id"), nullable=False)
    life_cycle_stage = Column(Enum(LifeCycleStage), nullable=False)
    sub_category = Column(Enum(SubCategory), nullable=False)

    product = relationship("Product", back_populates="materials")
    emission_factor = relationship("EmissionFactor")


class EnergyEntry(Base):
    __tablename__ = "energy_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    energy_carrier = Column(String(255), nullable=False)
    process_step = Column(String(255))
    batch_amount = Column(Float, nullable=False)
    ef_id = Column(Integer, ForeignKey("emission_factors.id"), nullable=False)
    life_cycle_stage = Column(Enum(LifeCycleStage), nullable=False)
    sub_category = Column(Enum(SubCategory), nullable=False)

    product = relationship("Product", back_populates="energy_entries")
    emission_factor = relationship("EmissionFactor")


class TransportEntry(Base):
    __tablename__ = "transport_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    transport_type = Column(String(255))
    from_location = Column(String(255))
    to_location = Column(String(255))
    distance_km = Column(Float, nullable=False)
    transport_mode = Column(String(255))
    batch_weight_kg = Column(Float, nullable=False)
    ef_id = Column(Integer, ForeignKey("emission_factors.id"), nullable=False)
    life_cycle_stage = Column(Enum(LifeCycleStage), nullable=False)
    sub_category = Column(Enum(SubCategory), nullable=False)

    product = relationship("Product", back_populates="transport_entries")
    emission_factor = relationship("EmissionFactor")

    @property
    def transport_performance_tkm(self):
        return self.distance_km * self.batch_weight_kg / 1000


class WasteEntry(Base):
    __tablename__ = "waste_entries"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    waste_type = Column(String(255), nullable=False)
    treatment = Column(String(255))
    batch_amount = Column(Float, nullable=False)
    ef_id = Column(Integer, ForeignKey("emission_factors.id"), nullable=False)
    life_cycle_stage = Column(Enum(LifeCycleStage), nullable=False)
    sub_category = Column(Enum(SubCategory), nullable=False)

    product = relationship("Product", back_populates="waste_entries")
    emission_factor = relationship("EmissionFactor")
