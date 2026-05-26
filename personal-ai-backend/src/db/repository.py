"""Repository layer: replaces mock_data.py with real PostgreSQL queries.

Each function mirrors a mock_*() function from src/tools/mock_data.py.
Agents call these instead of mock data. Returns the same shapes.
"""

from datetime import date, timedelta
from random import sample

from src.db.connection import get_pool


async def get_random_patient() -> dict | None:
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT * FROM patients ORDER BY RANDOM() LIMIT 1"
        )
        if not row:
            return None
        return {
            "id": row["id"],
            "nome": row["name"],
            "idade": row["age"],
            "diagnostico_principal": row["main_diagnosis"],
            "comorbidades": row["comorbidities"],
            "alergias": row["allergies"],
            "data_internacao": row["admission_date"],
            "leito": row["bed"],
            "especialidade": row["specialty"],
        }


async def get_patient_evolutions_text(patient_id: str | None = None, days: int = 7) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if patient_id:
            rows = await conn.fetch(
                """SELECT record_date, content FROM clinical_evolutions
                   WHERE patient_id = $1
                   ORDER BY record_date DESC LIMIT $2""",
                patient_id, days,
            )
        else:
            pid_row = await conn.fetchval("SELECT id FROM patients ORDER BY RANDOM() LIMIT 1")
            if not pid_row:
                return ""
            rows = await conn.fetch(
                """SELECT record_date, content FROM clinical_evolutions
                   WHERE patient_id = $1
                   ORDER BY record_date DESC LIMIT $2""",
                pid_row, days,
            )

        lines = []
        for r in reversed(rows):
            date_str = r["record_date"].strftime("%d/%m")
            lines.append(f"{date_str} - {r['content']}")
        return "\n".join(lines)


async def get_kpi_text() -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM kpi_metrics ORDER BY category, indicator")

    sections: dict[str, list[str]] = {}
    for r in rows:
        cat_label = {"clinical": "CLINICAL INDICATORS", "operational": "OPERATIONAL INDICATORS", "financial": "FINANCIAL INDICATORS"}
        section = cat_label.get(r["category"], r["category"].upper())
        sections.setdefault(section, [])
        val = r["current_value"]
        tgt = r["target_value"]
        unit = r["unit"]
        sections[section].append(f"{r['indicator']}: {val}{' ' + unit if unit else ''} (target {tgt}{' ' + unit if unit else ''})")

    parts = []
    for section, lines in sections.items():
        parts.append(f"=== {section} ===")
        parts.extend(lines)
        parts.append("")
    return "\n".join(parts).strip()


async def get_regulatory_requests() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM regulatory_requests ORDER BY RANDOM() LIMIT 10")
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "paciente": r["patient_name"],
                "idade": r["age"],
                "cid": r["cid"],
                "procedimento": r["procedure_name"],
                "dias_espera": r["wait_days"],
                "risco_clinico": r["clinical_risk"],
                "sla_dias": r["sla_days"],
            })
        return results


async def get_hospital_bills() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM hospital_bills ORDER BY RANDOM() LIMIT 10")
        results = []
        for r in rows:
            results.append({
                "id": r["id"],
                "paciente": r["patient_name"],
                "convenio": r["insurance"],
                "procedimento": r["procedure_name"],
                "valor": float(r["amount"]),
                "tem_laudo": r["has_medical_report"],
                "tem_relatorio_cirurgico": r["has_surgical_report"],
                "tem_evolucoes": r["has_progress_notes"],
                "tem_opme_autorizada": r["has_opme_authorized"],
                "cid_compativel": r["icd_compatible"],
                "historico_glosa_convenio": float(r["historical_denial_rate"]),
            })
        return results


async def get_appointments() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM appointments ORDER BY RANDOM() LIMIT 10")
        results = []
        for r in rows:
            results.append({
                "paciente": r["patient_name"],
                "tipo": r["appointment_type"],
                "confirmou": r["confirmed"],
                "taxa_historica_faltas": float(r["historical_miss_rate"]),
                "distancia_km": float(r["distance_km"]),
                "plano": r["insurance_plan"],
                "idade": r["age"],
            })
        return results


async def get_clinical_context(patient_id: str | None = None) -> str:
    pool = await get_pool()
    async with pool.acquire() as conn:
        if patient_id:
            p = await conn.fetchrow("SELECT * FROM patients WHERE id = $1", patient_id)
        else:
            p = await conn.fetchrow("SELECT * FROM patients ORDER BY RANDOM() LIMIT 1")

        if not p:
            return ""

        evos = await conn.fetch(
            """SELECT content FROM clinical_evolutions
               WHERE patient_id = $1
               ORDER BY record_date DESC LIMIT 2""",
            p["id"],
        )

        latest_evo = evos[0]["content"] if evos else "No recent progress notes."

        return (
            f"Patient {p['name']}, {p['age']} years old, admitted with "
            f"{p['main_diagnosis']} since {p['admission_date'].strftime('%d/%m/%Y')}.\n"
            f"Bed: {p['bed']}, Specialty: {p['specialty']}.\n"
            f"Comorbidities: {', '.join(p['comorbidities']) if p['comorbidities'] else 'None'}.\n"
            f"Allergies: {', '.join(p['allergies']) if p['allergies'] else 'None known'}.\n"
            f"Recent progress: {latest_evo}"
        )


async def get_hospital_units() -> list[dict]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT * FROM hospital_units ORDER BY occupancy_pct DESC")
        results = []
        for r in rows:
            results.append({
                "nome": r["name"],
                "ocupacao": float(r["occupancy_pct"]),
                "espera_min": r["wait_time_min"],
                "status": r["status"],
            })
        return results


async def get_surgical_data() -> dict:
    pool = await get_pool()
    async with pool.acquire() as conn:
        rooms = await conn.fetch("SELECT * FROM surgical_rooms")
        salas = []
        for room in rooms:
            surgeries = await conn.fetch(
                """SELECT * FROM surgeries WHERE room_id = $1
                   ORDER BY scheduled_date LIMIT 5""",
                room["id"],
            )
            salas.append({
                "sala": room["name"],
                "cirurgias": [s["procedure_name"] + (" (urgent)" if s["is_urgent"] else "") for s in surgeries],
                "utilizacao": random_utilization(),
            })
        return {"salas": salas}


def random_utilization() -> int:
    from random import randint
    return randint(20, 90)
