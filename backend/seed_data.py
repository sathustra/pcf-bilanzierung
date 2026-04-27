"""Seed script: inserts demo emission factors and a sample product."""
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

# Demo Emission Factors
efs = [
    dict(name="Gestrichenes Papier (80 g/m²)", ef_biogenic_co2=0.0, ef_luc_co2e=0.005,
         ef_fossil_co2e=0.92, unit="kg", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=2, ger=2, tir=2),
    dict(name="Druckfarbe (Offsetdruck)", ef_biogenic_co2=0.0, ef_luc_co2e=0.001,
         ef_fossil_co2e=3.10, unit="kg", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=3, ger=3, tir=3),
    dict(name="Strom Deutschland (Netz-Mix 2023)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.380, unit="kWh", database_source="UBA 2023",
         reference_year=2023, data_type=models.DataType.secondary, ter=1, ger=1, tir=2),
    dict(name="Strom Ökostrom (zertifiziert)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.020, unit="kWh", database_source="Lieferant Primärdaten",
         reference_year=2023, data_type=models.DataType.primary, ter=1, ger=1, tir=1),
    dict(name="Erdgas (Verbrennung)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.202, unit="kWh", database_source="GEMIS 5.0",
         reference_year=2022, data_type=models.DataType.secondary, ter=2, ger=2, tir=2),
    dict(name="LKW Transport (25t, EURO VI)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.062, unit="tkm", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=2, ger=3, tir=2),
    dict(name="Seefracht (Containerschiff)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.011, unit="tkm", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=3, ger=3, tir=3),
    dict(name="Deponierung Druckabfälle", ef_biogenic_co2=0.045, ef_luc_co2e=0.0,
         ef_fossil_co2e=0.008, unit="kg", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=3, ger=3, tir=3),
    dict(name="Primärkarton (Verpackung)", ef_biogenic_co2=0.0, ef_luc_co2e=0.010,
         ef_fossil_co2e=0.65, unit="kg", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=2, ger=2, tir=3),
    dict(name="Isopropanol (IPA)", ef_biogenic_co2=0.0, ef_luc_co2e=0.0,
         ef_fossil_co2e=1.85, unit="kg", database_source="ecoinvent 3.10",
         reference_year=2023, data_type=models.DataType.secondary, ter=3, ger=3, tir=3),
]

existing = db.query(models.EmissionFactor).count()
if existing == 0:
    for ef_data in efs:
        db.add(models.EmissionFactor(**ef_data))
    db.commit()
    print(f"✓ {len(efs)} Emissionsfaktoren eingefügt")

# Demo Product
if db.query(models.Product).count() == 0:
    product = models.Product(
        product_name="Katalog A4 glossy (80 g/m² gestrichenes Papier)",
        product_category="Graphisches Druckerzeugnis",
        reference_unit="m²",
        annual_production=5_000_000,
        weight_per_unit=0.096,
        biogenic_carbon_content=0.035,
        scope="Cradle-to-Gate",
        allocation_method="Masse-Allokation",
        reference_year=2023,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    pid = product.id

    ef_ids = {ef.name: ef.id for ef in db.query(models.EmissionFactor).all()}

    # Materials
    db.add(models.MaterialEntry(
        product_id=pid, position=1, designation="Gestrichenes Papier",
        supplier="Sappi Europe", batch_amount=480_000,
        ef_id=ef_ids["Gestrichenes Papier (80 g/m²)"],
        life_cycle_stage=models.LifeCycleStage.raw_material,
        sub_category=models.SubCategory.main_material,
    ))
    db.add(models.MaterialEntry(
        product_id=pid, position=2, designation="Druckfarben Offsetdruck",
        supplier="Huber Group", batch_amount=8_500,
        ef_id=ef_ids["Druckfarbe (Offsetdruck)"],
        life_cycle_stage=models.LifeCycleStage.raw_material,
        sub_category=models.SubCategory.auxiliaries,
    ))
    db.add(models.MaterialEntry(
        product_id=pid, position=3, designation="Isopropanol Feuchtmittel",
        supplier="intern", batch_amount=1_200,
        ef_id=ef_ids["Isopropanol (IPA)"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.auxiliaries,
    ))
    db.add(models.MaterialEntry(
        product_id=pid, position=4, designation="Transportkarton (Verpackung)",
        supplier="Smurfit Kappa", batch_amount=6_000,
        ef_id=ef_ids["Primärkarton (Verpackung)"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.packaging_logistics,
    ))

    # Energy
    db.add(models.EnergyEntry(
        product_id=pid, energy_carrier="Strom (Netz-Mix)",
        process_step="Druckmaschinen & Weiterverarbeitung",
        batch_amount=320_000,
        ef_id=ef_ids["Strom Deutschland (Netz-Mix 2023)"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.electricity_grid,
    ))
    db.add(models.EnergyEntry(
        product_id=pid, energy_carrier="Strom Ökostrom",
        process_step="Beleuchtung & Lager",
        batch_amount=45_000,
        ef_id=ef_ids["Strom Ökostrom (zertifiziert)"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.electricity_renewable,
    ))
    db.add(models.EnergyEntry(
        product_id=pid, energy_carrier="Erdgas",
        process_step="Trocknung & Heizung",
        batch_amount=180_000,
        ef_id=ef_ids["Erdgas (Verbrennung)"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.heat_steam,
    ))

    # Transport
    db.add(models.TransportEntry(
        product_id=pid, transport_type="Inbound Papier",
        from_location="Gratkorn (AT)", to_location="Druckerei",
        distance_km=850, transport_mode="LKW 25t",
        batch_weight_kg=480_000,
        ef_id=ef_ids["LKW Transport (25t, EURO VI)"],
        life_cycle_stage=models.LifeCycleStage.transport_storage,
        sub_category=models.SubCategory.inbound_transport,
    ))
    db.add(models.TransportEntry(
        product_id=pid, transport_type="Inbound Farbe",
        from_location="München", to_location="Druckerei",
        distance_km=220, transport_mode="LKW 25t",
        batch_weight_kg=8_500,
        ef_id=ef_ids["LKW Transport (25t, EURO VI)"],
        life_cycle_stage=models.LifeCycleStage.transport_storage,
        sub_category=models.SubCategory.inbound_transport,
    ))

    # Waste
    db.add(models.WasteEntry(
        product_id=pid, waste_type="Makulatur & Schnittabfälle",
        treatment="Deponierung",
        batch_amount=22_000,
        ef_id=ef_ids["Deponierung Druckabfälle"],
        life_cycle_stage=models.LifeCycleStage.manufacturing,
        sub_category=models.SubCategory.production_waste,
    ))

    db.commit()
    print(f"✓ Demo-Produkt '{product.product_name}' mit Bilanzierungsdaten eingefügt (ID={pid})")

db.close()
print("Seed abgeschlossen.")
