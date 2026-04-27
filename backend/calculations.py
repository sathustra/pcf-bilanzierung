from typing import List, Dict, Tuple
from dataclasses import dataclass, field


BIOGENIC_C_TO_CO2_FACTOR = 3.664


@dataclass
class EntryEmission:
    biogenic: float = 0.0
    luc: float = 0.0
    fossil: float = 0.0
    life_cycle_stage: str = ""
    sub_category: str = ""
    ef_data_type: str = "Sekundär"
    ter: int = 3
    ger: int = 3
    tir: int = 3

    @property
    def total(self):
        return self.biogenic + self.luc + self.fossil


def _calc_entry(activity: float, ef_biogenic: float, ef_luc: float, ef_fossil: float,
                annual_production: float, life_cycle_stage: str, sub_category: str,
                data_type: str, ter: int, ger: int, tir: int) -> EntryEmission:
    if annual_production <= 0:
        return EntryEmission(life_cycle_stage=life_cycle_stage, sub_category=sub_category,
                             ef_data_type=data_type, ter=ter, ger=ger, tir=tir)
    return EntryEmission(
        biogenic=activity * ef_biogenic / annual_production,
        luc=activity * ef_luc / annual_production,
        fossil=activity * ef_fossil / annual_production,
        life_cycle_stage=life_cycle_stage,
        sub_category=sub_category,
        ef_data_type=data_type,
        ter=ter,
        ger=ger,
        tir=tir,
    )


def calculate_pcf(product, materials, energy_entries, transport_entries, waste_entries):
    ap = product.annual_production
    emissions: List[EntryEmission] = []

    for m in materials:
        ef = m.emission_factor
        emissions.append(_calc_entry(
            m.batch_amount, ef.ef_biogenic_co2, ef.ef_luc_co2e, ef.ef_fossil_co2e,
            ap, m.life_cycle_stage.value, m.sub_category.value,
            ef.data_type.value, ef.ter, ef.ger, ef.tir
        ))

    for e in energy_entries:
        ef = e.emission_factor
        emissions.append(_calc_entry(
            e.batch_amount, ef.ef_biogenic_co2, ef.ef_luc_co2e, ef.ef_fossil_co2e,
            ap, e.life_cycle_stage.value, e.sub_category.value,
            ef.data_type.value, ef.ter, ef.ger, ef.tir
        ))

    for t in transport_entries:
        ef = t.emission_factor
        tkm = t.distance_km * t.batch_weight_kg / 1000
        emissions.append(_calc_entry(
            tkm, ef.ef_biogenic_co2, ef.ef_luc_co2e, ef.ef_fossil_co2e,
            ap, t.life_cycle_stage.value, t.sub_category.value,
            ef.data_type.value, ef.ter, ef.ger, ef.tir
        ))

    for w in waste_entries:
        ef = w.emission_factor
        emissions.append(_calc_entry(
            w.batch_amount, ef.ef_biogenic_co2, ef.ef_luc_co2e, ef.ef_fossil_co2e,
            ap, w.life_cycle_stage.value, w.sub_category.value,
            ef.data_type.value, ef.ter, ef.ger, ef.tir
        ))

    # ── GWP Indicators ──────────────────────────────────────────────────────
    gwp_fossil = sum(e.fossil for e in emissions)
    gwp_biogenic_emissions = sum(e.biogenic for e in emissions)
    gwp_luluc = sum(e.luc for e in emissions)
    gwp_biogenic_uptake = product.biogenic_carbon_content * BIOGENIC_C_TO_CO2_FACTOR * (-1)
    gwp_total = gwp_fossil + gwp_biogenic_emissions + gwp_luluc

    # ── Category results ────────────────────────────────────────────────────
    def _sum_category(entries_list, stage_prefix=None):
        if stage_prefix:
            subset = [e for e in entries_list if e.life_cycle_stage == stage_prefix]
        else:
            subset = entries_list
        return (
            sum(e.biogenic for e in subset),
            sum(e.luc for e in subset),
            sum(e.fossil for e in subset),
        )

    mat_em = emissions[:len(materials)]
    en_em = emissions[len(materials):len(materials)+len(energy_entries)]
    tr_em = emissions[len(materials)+len(energy_entries):len(materials)+len(energy_entries)+len(transport_entries)]
    wa_em = emissions[len(materials)+len(energy_entries)+len(transport_entries):]

    # ── Life Cycle Stage aggregation ────────────────────────────────────────
    lcs_map: Dict[str, List[float]] = {}
    for e in emissions:
        if e.life_cycle_stage not in lcs_map:
            lcs_map[e.life_cycle_stage] = [0.0, 0.0, 0.0]
        lcs_map[e.life_cycle_stage][0] += e.biogenic
        lcs_map[e.life_cycle_stage][1] += e.luc
        lcs_map[e.life_cycle_stage][2] += e.fossil

    lifecycle_results = []
    for stage, (bio, luc, fossil) in lcs_map.items():
        share_total = (bio + luc + fossil) / gwp_total * 100 if gwp_total != 0 else 0
        share_fossil = fossil / gwp_fossil * 100 if gwp_fossil != 0 else 0
        lifecycle_results.append({
            "stage": stage,
            "biogenic": round(bio, 6),
            "luc": round(luc, 6),
            "fossil": round(fossil, 6),
            "share_of_gwp_total": round(share_total, 2),
            "share_of_gwp_fossil": round(share_fossil, 2),
        })

    # ── Sub-Category aggregation ────────────────────────────────────────────
    subcat_map: Dict[Tuple[str, str], List[float]] = {}
    for e in emissions:
        key = (e.sub_category, e.life_cycle_stage)
        if key not in subcat_map:
            subcat_map[key] = [0.0, 0.0, 0.0]
        subcat_map[key][0] += e.biogenic
        subcat_map[key][1] += e.luc
        subcat_map[key][2] += e.fossil

    subcategory_results = [
        {
            "sub_category": subcat,
            "life_cycle_stage": lcs,
            "biogenic": round(bio, 6),
            "luc": round(luc, 6),
            "fossil": round(fossil, 6),
        }
        for (subcat, lcs), (bio, luc, fossil) in subcat_map.items()
    ]

    # ── DQR ─────────────────────────────────────────────────────────────────
    total_abs = sum(abs(e.total) for e in emissions)
    if total_abs > 0:
        weighted_dqr = sum(
            abs(e.total) * (e.ter + e.ger + e.tir) / 3
            for e in emissions
        ) / total_abs
    else:
        weighted_dqr = 3.0

    if weighted_dqr <= 1.6:
        traffic_light = "grün"
    elif weighted_dqr <= 3.0:
        traffic_light = "gelb"
    else:
        traffic_light = "rot"

    primary_total = sum(abs(e.total) for e in emissions if e.ef_data_type == "Primär")
    pds = primary_total / total_abs * 100 if total_abs > 0 else 0

    def _triple(subset):
        return {
            "biogenic": round(sum(e.biogenic for e in subset), 6),
            "luc": round(sum(e.luc for e in subset), 6),
            "fossil": round(sum(e.fossil for e in subset), 6),
        }

    return {
        "gwp_indicators": {
            "gwp_fossil": round(gwp_fossil, 6),
            "gwp_biogenic_emissions": round(gwp_biogenic_emissions, 6),
            "gwp_biogenic_uptake": round(gwp_biogenic_uptake, 6),
            "gwp_luluc": round(gwp_luluc, 6),
            "gwp_total": round(gwp_total, 6),
        },
        "category_results": {
            "materials": _triple(mat_em),
            "energy": _triple(en_em),
            "transport": _triple(tr_em),
            "waste": _triple(wa_em),
        },
        "lifecycle_results": lifecycle_results,
        "subcategory_results": subcategory_results,
        "dqr": {
            "dqr_score": round(weighted_dqr, 2),
            "traffic_light": traffic_light,
            "primary_data_share": round(pds, 1),
        },
    }
