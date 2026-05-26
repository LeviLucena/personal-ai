"""Seed the PostgreSQL database with realistic hospital data using Faker.

Usage:
    python -m src.db.seed                    # uses DATABASE_URL from .env
    python -m src.db.seed --url postgresql://...
"""

import argparse
import asyncio
import random
from datetime import date, timedelta

import asyncpg

try:
    from faker import Faker
except ImportError:
    Faker = None  # handled at runtime


DIAGNOSES = [
    ("I10", "Essential Hypertension"),
    ("I50.0", "Congestive Heart Failure"),
    ("J18.9", "Pneumonia, Unspecified"),
    ("E11", "Type 2 Diabetes Mellitus"),
    ("I21.0", "Acute Myocardial Infarction"),
    ("C50.9", "Breast Cancer"),
    ("N20.0", "Kidney Stone"),
    ("K80.0", "Cholelithiasis"),
    ("M17.9", "Osteoarthritis of Knee"),
    ("J45.0", "Asthma"),
    ("N40", "Benign Prostatic Hyperplasia"),
    ("K35.9", "Acute Appendicitis"),
    ("S72.0", "Femoral Neck Fracture"),
    ("G40.9", "Epilepsy"),
    ("F32.9", "Major Depressive Disorder"),
]

PROCEDURES = [
    "Cardiac Catheterization",
    "Knee Arthroscopy",
    "Cholecystectomy",
    "Herniorrhaphy",
    "Hysterectomy",
    "Nephrolithotripsy",
    "Cesarean Delivery",
    "Total Hip Replacement",
    "Coronary Artery Bypass",
    "Appendectomy",
    "Cataract Surgery",
    "Spinal Fusion",
]

EXAM_PROCEDURES = [
    "Upper Endoscopy",
    "Colonoscopy",
    "Diagnostic MRI",
    "CT Scan",
    "Echocardiogram",
    "Stress Test",
    "Mammography",
]

INSURANCE_PLANS = ["Unimed", "Amil", "Bradesco Saude", "SulAmerica", "Private", "NotreDame"]

EVOLUTION_TEMPLATES = [
    "Patient {name}, {age} years old, {diagnosis}. Vital signs: BP {bp_sys}/{bp_dia} mmHg, HR {hr} bpm, SpO2 {spo2}%, temperature {temp}C. "
    "Condition: {condition}. Medications administered: {meds}. "
    "Plan: {plan}.",
    "Daily progress note for {name} ({age}y, {diagnosis}). "
    "Subjective: {subjective}. "
    "Objective: BP {bp_sys}/{bp_dia}, HR {hr}, SpO2 {spo2}, Temp {temp}C. "
    "Assessment: {condition}. "
    "Plan: {plan}.",
    "Patient {name} remains hospitalized with {diagnosis}. "
    "Current status: {condition}. "
    "Vitals: {bp_sys}/{bp_dia}, {hr} bpm, {spo2}% O2, {temp}C. "
    "Ongoing treatment: {meds}. "
    "Next steps: {plan}.",
]

SUBJECTIVE_POOL = [
    "Patient reports feeling better today, pain reduced.",
    "Patient complains of persistent dyspnea on minimal exertion.",
    "No new complaints. Pain well controlled with medication.",
    "Patient reports headache and nausea since last night.",
    "Patient is anxious about discharge planning.",
    "Reports good appetite, sleeping well.",
    "Mild discomfort at surgical site, rated 3/10.",
]

CONDITION_POOL = [
    "clinically stable, improving",
    "partially improved, requiring monitoring",
    "unchanged from previous assessment",
    "showing gradual improvement",
    "slight deterioration in respiratory function",
    "stable, afebrile for 24 hours",
    "hemodynamically stable",
    "recovering well post-procedure",
]

MEDS_POOL = [
    "Ceftriaxone 1g IV 12/12h, Azithromycin 500mg IV 24/24h",
    "Furosemide 40mg IV 12/12h, Enalapril 10mg PO 24/24h",
    "Morphine 5mg IV PRN, Paracetamol 750mg PO 6/6h",
    "Metformin 850mg PO 12/12h, Insulin NPH 20U SC",
    "Amoxicillin 500mg PO 8/8h, Ibuprofen 400mg PO 8/8h",
    "Heparin 5000U SC 12/12h, Warfarin 5mg PO",
    "Dexamethasone 8mg IV 8/8h, Salbutamol nebulization 6/6h",
]

PLAN_POOL = [
    "Continue current antibiotic therapy. Repeat cultures in 48h.",
    "Wean vasopressors gradually. Monitor urine output.",
    "Schedule physiotherapy evaluation. Consider transfer to ward.",
    "Prepare discharge planning with social services.",
    "Advance diet as tolerated. Increase mobilization.",
    "Repeat laboratory tests tomorrow morning.",
    "Consult cardiology for heart failure optimization.",
    "Plan surgical intervention for next available slot.",
]


def random_patient_data(fake: Faker, patient_id: str) -> dict:
    sex = random.choice(["male", "female"])
    name = fake.name_male() if sex == "male" else fake.name_female()

    if random.random() < 0.6:
        cid, diag = random.choice(DIAGNOSES)
    else:
        cid, diag = f"I{random.randint(0,99)}.{random.randint(0,9)}", fake.sentence(nb_words=3).rstrip(".")

    num_comorb = random.choices([0, 1, 2, 3], weights=[20, 40, 30, 10])[0]
    other_diags = random.sample([d for d in DIAGNOSES if d[0] != cid], min(num_comorb, len(DIAGNOSES) - 1))
    comorbidities = [f"{d[1]} ({d[0]})" for d in other_diags]

    num_alerg = random.choices([0, 1, 2], weights=[50, 35, 15])[0]
    allergies = random.sample(["Penicillin", "Dipyrone", "Sulfa", "Iodine", "Aspirin", "Latex", "Codeine", "Morphine"], num_alerg)

    specialties = ["Cardiology", "Pulmonology", "General Surgery", "Orthopedics", "Neurology", "Internal Medicine", "Oncology", "Urology"]
    beds = [f"{random.choice(['1','2','3','4'])}{random.choice('ABCDEF')}-{random.randint(1,30):02d}" for _ in range(1)]

    admission = fake.date_between(start_date="-30d", end_date="-1d")

    return {
        "id": patient_id,
        "name": name,
        "age": random.randint(18, 88),
        "main_diagnosis": f"{diag} ({cid})",
        "comorbidities": comorbidities,
        "allergies": allergies,
        "admission_date": admission,
        "bed": beds[0],
        "specialty": random.choice(specialties),
    }


def generate_evolution_text(fake: Faker, patient_name: str, age: int, diagnosis: str, day_num: int) -> str:
    template = random.choice(EVOLUTION_TEMPLATES)
    bp_sys = random.randint(95, 155)
    bp_dia = random.randint(60, 95)
    hr = random.randint(60, 110)
    spo2 = random.randint(88, 99)
    temp = round(random.uniform(36.0, 38.8), 1)

    if day_num <= 2:
        condition = random.choice(["hemodynamically unstable, requiring monitoring", "critical, under intensive care"])
        subjective = ""
    else:
        condition = random.choice(CONDITION_POOL)
        subjective = random.choice(SUBJECTIVE_POOL)

    return template.format(
        name=patient_name,
        age=age,
        diagnosis=diagnosis,
        bp_sys=bp_sys,
        bp_dia=bp_dia,
        hr=hr,
        spo2=spo2,
        temp=temp,
        condition=condition,
        meds=random.choice(MEDS_POOL),
        plan=random.choice(PLAN_POOL),
        subjective=subjective,
    )


async def seed_database(dsn: str, patient_count: int = 50, skip_if_seeded: bool = False):
    fake = Faker("en_US")
    fake.seed_instance(42)
    random.seed(42)

    conn = await asyncpg.connect(dsn)

    try:
        if skip_if_seeded:
            existing = await conn.fetchval("SELECT COUNT(*) FROM patients")
            if existing and existing > 0:
                print(f"Database already seeded ({existing} patients found). Skipping.")
                return
        print(f"Seeding database with {patient_count} patients...")

        # --- Patients ---
        patients = []
        for i in range(1, patient_count + 1):
            pid = f"PAC-{2026:04d}-{i:04d}"
            p = random_patient_data(fake, pid)
            patients.append(p)

            await conn.execute(
                """INSERT INTO patients (id, name, age, main_diagnosis, comorbidities, allergies, admission_date, bed, specialty)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9)""",
                p["id"], p["name"], p["age"], p["main_diagnosis"],
                p["comorbidities"], p["allergies"],
                p["admission_date"], p["bed"], p["specialty"],
            )
        print(f"  ✓ {len(patients)} patients created")

        # --- Clinical Evolutions ---
        evo_count = 0
        for p in patients:
            admission = p["admission_date"]
            days = min(random.randint(3, 10), (date.today() - admission).days)
            if days < 1:
                days = 3

            for d in range(days):
                record_date = admission + timedelta(days=d)
                content = generate_evolution_text(
                    fake, p["name"], p["age"], p["main_diagnosis"], d + 1
                )
                await conn.execute(
                    """INSERT INTO clinical_evolutions (patient_id, record_date, content)
                       VALUES ($1,$2,$3)""",
                    p["id"], record_date, content,
                )
                evo_count += 1
        print(f"  ✓ {evo_count} clinical evolutions created")

        # --- Regulatory Requests ---
        req_count = 0
        for p in random.sample(patients, min(30, patient_count)):
            rid = f"REG-{2026:04d}-{req_count + 1:04d}"
            risk = random.choices(["LOW", "MEDIUM", "HIGH", "CRITICAL"], weights=[15, 35, 35, 15])[0]
            sla = {"LOW": 15, "MEDIUM": 10, "HIGH": 10, "CRITICAL": 7}[risk]

            req = {
                "id": rid,
                "patient_name": p["name"],
                "age": p["age"],
                "cid": p["main_diagnosis"].split("(")[-1].rstrip(")"),
                "procedure_name": random.choice(PROCEDURES + EXAM_PROCEDURES),
                "wait_days": random.randint(1, 25),
                "clinical_risk": risk,
                "sla_days": sla,
            }
            await conn.execute(
                """INSERT INTO regulatory_requests (id, patient_name, age, cid, procedure_name, wait_days, clinical_risk, sla_days)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
                req["id"], req["patient_name"], req["age"], req["cid"],
                req["procedure_name"], req["wait_days"], req["clinical_risk"], req["sla_days"],
            )
            req_count += 1
        print(f"  ✓ {req_count} regulatory requests created")

        # --- Hospital Bills ---
        bill_count = 0
        for p in random.sample(patients, min(25, patient_count)):
            bid = f"CTH-{2026:04d}-{bill_count + 1:04d}"
            bill = {
                "id": bid,
                "patient_name": p["name"],
                "insurance": random.choice(INSURANCE_PLANS),
                "procedure_name": random.choice(PROCEDURES),
                "amount": round(random.uniform(2000, 35000), 2),
                "has_medical_report": random.choices([True, False], weights=[75, 25])[0],
                "has_surgical_report": random.choices([True, False], weights=[70, 30])[0],
                "has_progress_notes": random.choices([True, False], weights=[80, 20])[0],
                "has_opme_authorized": random.choices([True, False], weights=[60, 40])[0],
                "icd_compatible": random.choices([True, False], weights=[85, 15])[0],
                "historical_denial_rate": round(random.uniform(0.01, 0.25), 2),
            }
            await conn.execute(
                """INSERT INTO hospital_bills (id, patient_name, insurance, procedure_name, amount,
                   has_medical_report, has_surgical_report, has_progress_notes,
                   has_opme_authorized, icd_compatible, historical_denial_rate)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11)""",
                bill["id"], bill["patient_name"], bill["insurance"], bill["procedure_name"],
                bill["amount"], bill["has_medical_report"], bill["has_surgical_report"],
                bill["has_progress_notes"], bill["has_opme_authorized"],
                bill["icd_compatible"], bill["historical_denial_rate"],
            )
            bill_count += 1
        print(f"  ✓ {bill_count} hospital bills created")

        # --- Appointments ---
        appt_count = 0
        types = ["Cardiology", "Follow-up", "Exam", "Pediatrics", "Orthopedics", "Neurology", "Dermatology"]
        for _ in range(40):
            age = random.randint(5, 85)
            name = fake.name_male() if random.random() < 0.5 else fake.name_female()
            appt = {
                "patient_name": name,
                "appointment_type": random.choice(types),
                "confirmed": random.choices([True, False], weights=[55, 45])[0],
                "historical_miss_rate": round(random.uniform(0, 0.5), 2),
                "distance_km": round(random.uniform(1, 40), 1),
                "insurance_plan": random.choice(INSURANCE_PLANS),
                "age": age,
                "scheduled_date": fake.date_between(start_date="today", end_date="+14d"),
            }
            await conn.execute(
                """INSERT INTO appointments (patient_name, appointment_type, confirmed,
                   historical_miss_rate, distance_km, insurance_plan, age, scheduled_date)
                   VALUES ($1,$2,$3,$4,$5,$6,$7,$8)""",
                appt["patient_name"], appt["appointment_type"], appt["confirmed"],
                appt["historical_miss_rate"], appt["distance_km"], appt["insurance_plan"],
                appt["age"], appt["scheduled_date"],
            )
            appt_count += 1
        print(f"  ✓ {appt_count} appointments created")

        # --- Hospital Units ---
        units_data = [
            ("Emergency Room", 98, 85, "CRITICAL"),
            ("General ICU", 95, 120, "CRITICAL"),
            ("Clinical Ward", 82, 45, "WARNING"),
            ("Surgical Center", 74, 20, "NORMAL"),
            ("Outpatient Clinic", 65, 35, "NORMAL"),
            ("Cardiology Unit", 88, 60, "WARNING"),
            ("Orthopedics Ward", 70, 30, "NORMAL"),
            ("Pediatrics Unit", 55, 25, "NORMAL"),
            ("Maternity Ward", 78, 15, "NORMAL"),
            ("Oncology Unit", 90, 50, "WARNING"),
        ]
        for name, occ, wait, status in units_data:
            await conn.execute(
                "INSERT INTO hospital_units (name, occupancy_pct, wait_time_min, status) VALUES ($1,$2,$3,$4)",
                name, occ, wait, status,
            )
        print(f"  ✓ {len(units_data)} hospital units created")

        # --- Surgical Rooms & Surgeries ---
        rooms = ["Sala 1 — Orthopedics", "Sala 2 — General Surgery", "Sala 3 — Uro/Gynecology"]
        room_ids = []
        for name in rooms:
            rid = await conn.fetchval(
                "INSERT INTO surgical_rooms (name) VALUES ($1) RETURNING id", name
            )
            room_ids.append(rid)

        surgery_data = [
            (room_ids[0], "Knee Arthroplasty", "Orthopedics", False, 120),
            (room_ids[0], "ACL Reconstruction", "Orthopedics", False, 90),
            (room_ids[1], "Cholecystectomy", "General Surgery", True, 60),
            (room_ids[1], "Herniorrhaphy", "General Surgery", False, 45),
            (room_ids[1], "Appendectomy", "General Surgery", True, 50),
            (room_ids[2], "Hysterectomy", "Gynecology", False, 110),
            (room_ids[2], "Nephrolithotripsy", "Urology", False, 75),
            (room_ids[2], "Diagnostic Laparoscopy", "Gynecology", False, 40),
            (room_ids[0], "Total Hip Replacement", "Orthopedics", False, 150),
            (room_ids[1], "Colectomy", "General Surgery", False, 130),
        ]
        surg_count = 0
        for room_id, proc, spec, urgent, dur in surgery_data:
            pat_name = fake.name()
            sched_date = fake.date_between(start_date="today", end_date="+7d")
            await conn.execute(
                """INSERT INTO surgeries (room_id, patient_name, procedure_name, specialty, is_urgent, duration_min, scheduled_date)
                   VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                room_id, pat_name, proc, spec, urgent, dur, sched_date,
            )
            surg_count += 1
        print(f"  ✓ {surg_count} surgeries created")

        # --- KPI Metrics ---
        kpis = [
            ("clinical", "Occupancy Rate", 87.5, 85.0, "%"),
            ("clinical", "ER Average Wait Time", 42.0, 30.0, "min"),
            ("clinical", "7-day Readmission Rate", 4.2, 5.0, "%"),
            ("operational", "Clinic No-show Rate", 18.5, 12.0, "%"),
            ("operational", "Surgical Center Occupancy", 74.0, 80.0, "%"),
            ("operational", "Average Length of Stay", 3.2, 4.0, "days"),
            ("financial", "Total Revenue", 4850000.0, 5200000.0, "R$"),
            ("financial", "Operating Margin", 11.2, 15.0, "%"),
            ("financial", "Deduction Rate", 6.8, 4.0, "%"),
            ("financial", "Default Rate", 3.5, 5.0, "%"),
            ("clinical", "Bed Productivity", 3.2, 4.0, "days"),
            ("operational", "ICU Occupancy", 95.0, 85.0, "%"),
            ("financial", "Average Ticket", 12500.0, 10000.0, "R$"),
            ("clinical", "Satisfaction Score", 82.0, 90.0, "%"),
            ("operational", "Surgery Cancellation Rate", 5.5, 3.0, "%"),
        ]
        for cat, ind, cur, tgt, unit in kpis:
            await conn.execute(
                "INSERT INTO kpi_metrics (category, indicator, current_value, target_value, unit) VALUES ($1,$2,$3,$4,$5)",
                cat, ind, cur, tgt, unit,
            )
        print(f"  ✓ {len(kpis)} KPI metrics created")

        print("\n✅ Database seeded successfully!")

    finally:
        await conn.close()


def main():
    parser = argparse.ArgumentParser(description="Seed Personal AI database")
    parser.add_argument("--url", help="Database URL", default=None)
    parser.add_argument("--patients", type=int, default=50, help="Number of patients (default: 50)")
    parser.add_argument("--skip-if-seeded", action="store_true", help="Skip if database already has data")
    args = parser.parse_args()

    if Faker is None:
        print("ERROR: faker is not installed. Run: pip install faker")
        return

    dsn = args.url
    if not dsn:
        from src.config import settings
        dsn = settings.database_url
    if not dsn:
        print("ERROR: DATABASE_URL not set. Provide --url or set in .env")
        return

    asyncio.run(seed_database(dsn, args.patients, skip_if_seeded=args.skip_if_seeded))


if __name__ == "__main__":
    main()
