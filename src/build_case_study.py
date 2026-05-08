from __future__ import annotations

import csv
import random
import sqlite3
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "business_operations_raw.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "clean_operations_requests.csv"
DB_PATH = ROOT / "data" / "processed" / "operations_reporting.sqlite"
REPORT_DIR = ROOT / "reports"
SQL_PATH = ROOT / "sql" / "analysis_queries.sql"


REQUEST_TYPES = {
    "Account Setup": {"department": "IT Support", "base_value": 320},
    "Billing Question": {"department": "Billing", "base_value": 210},
    "Invoice Correction": {"department": "Billing", "base_value": 280},
    "Dashboard Request": {"department": "Data & Reporting", "base_value": 850},
    "Data Export": {"department": "Data & Reporting", "base_value": 480},
    "Automation Request": {"department": "Systems Operations", "base_value": 1200},
    "Intake Form Issue": {"department": "Systems Operations", "base_value": 390},
    "Appointment Change": {"department": "Scheduling", "base_value": 160},
    "Service Follow-Up": {"department": "Client Success", "base_value": 260},
    "Vendor Record Update": {"department": "Admin Operations", "base_value": 180},
}

CHANNELS = ["Email", "Web Form", "Phone", "Referral", "Walk-In"]
CUSTOMER_TYPES = ["Student", "Parent", "Small Business", "Internal Staff", "Vendor"]
PRIORITIES = ["Low", "Normal", "High", "Urgent"]
STATUSES = ["Closed", "Closed", "Closed", "Closed", "In Progress", "Open"]

TEXT_VARIANTS = {
    "Email": ["Email", "email", " EMAIL ", "E-mail"],
    "Web Form": ["Web Form", "web form", "WEB", "Online Form"],
    "Phone": ["Phone", "phone", "Call", " PHONE "],
    "Referral": ["Referral", "referral", "Referred"],
    "Walk-In": ["Walk-In", "Walk in", "walk-in", "In Person"],
    "Closed": ["Closed", "closed", "Complete", "Done"],
    "In Progress": ["In Progress", "in progress", "Working", "Pending"],
    "Open": ["Open", "open", "New"],
}


def ensure_dirs() -> None:
    for path in [
        RAW_PATH.parent,
        CLEAN_PATH.parent,
        DB_PATH.parent,
        REPORT_DIR,
        SQL_PATH.parent,
    ]:
        path.mkdir(parents=True, exist_ok=True)


def messy_text(value: str, chance: float = 0.18) -> str:
    if random.random() < chance and value in TEXT_VARIANTS:
        return random.choice(TEXT_VARIANTS[value])
    if random.random() < 0.03:
        return ""
    return value


def messy_number(value: float, chance: float = 0.08) -> str:
    if random.random() < chance:
        return ""
    if random.random() < 0.02:
        return str(round(value * -1, 2))
    if random.random() < 0.08:
        return f" {value:.1f} "
    return f"{value:.2f}"


def messy_date(value: date) -> str:
    formats = ["%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"]
    if random.random() < 0.02:
        return ""
    return value.strftime(random.choice(formats))


def generate_raw_dataset(record_count: int = 640) -> list[dict[str, str]]:
    random.seed(26)
    rows: list[dict[str, str]] = []
    start = date(2026, 1, 5)

    for i in range(record_count):
        request_type = random.choices(
            list(REQUEST_TYPES),
            weights=[9, 11, 8, 10, 9, 7, 8, 13, 16, 9],
            k=1,
        )[0]
        department = REQUEST_TYPES[request_type]["department"]
        channel = random.choices(CHANNELS, weights=[34, 29, 18, 9, 10], k=1)[0]
        customer_type = random.choice(CUSTOMER_TYPES)
        priority = random.choices(PRIORITIES, weights=[22, 52, 21, 5], k=1)[0]
        status = random.choice(STATUSES)
        request_date = start + timedelta(days=random.randint(0, 109))

        priority_speed = {"Low": 1.3, "Normal": 1.0, "High": 0.68, "Urgent": 0.42}[priority]
        channel_drag = {"Email": 1.16, "Web Form": 0.92, "Phone": 0.72, "Referral": 1.05, "Walk-In": 0.8}[channel]
        department_drag = {
            "IT Support": 0.86,
            "Billing": 1.18,
            "Data & Reporting": 1.34,
            "Systems Operations": 1.42,
            "Scheduling": 0.74,
            "Client Success": 0.9,
            "Admin Operations": 1.0,
        }[department]

        response_hours = max(0.3, random.lognormvariate(1.15, 0.55) * priority_speed * channel_drag)
        resolution_hours = max(
            response_hours + 0.8,
            random.lognormvariate(2.45, 0.6) * priority_speed * department_drag,
        )
        if status != "Closed":
            resolution_hours = 0

        rework_required = random.random() < (
            0.08
            + (0.05 if department in {"Billing", "Data & Reporting", "Systems Operations"} else 0)
            + (0.04 if channel == "Email" else 0)
        )
        value_noise = random.uniform(0.72, 1.45)
        revenue_value = REQUEST_TYPES[request_type]["base_value"] * value_noise
        cost_estimate = revenue_value * random.uniform(0.22, 0.55)
        if rework_required:
            cost_estimate *= random.uniform(1.18, 1.55)

        satisfaction = 4.7
        satisfaction -= min(1.2, response_hours / 28)
        satisfaction -= min(1.1, resolution_hours / 90) if status == "Closed" else 0.35
        satisfaction -= 0.35 if rework_required else 0
        satisfaction += random.uniform(-0.22, 0.18)
        satisfaction = min(5.0, max(1.0, satisfaction))

        rows.append(
            {
                "ticket_id": f"REQ-{10000 + i}",
                "request_date": messy_date(request_date),
                "channel": messy_text(channel),
                "department": messy_text(department, 0.1),
                "request_type": messy_text(request_type, 0.08),
                "customer_type": messy_text(customer_type, 0.06),
                "priority": messy_text(priority, 0.08),
                "status": messy_text(status),
                "response_hours": messy_number(response_hours),
                "resolution_hours": messy_number(resolution_hours),
                "rework_required": random.choice(["yes", "Y", "true", "1"]) if rework_required else random.choice(["no", "N", "false", "0"]),
                "revenue_value": messy_number(revenue_value),
                "cost_estimate": messy_number(cost_estimate),
                "satisfaction_score": messy_number(satisfaction, 0.05),
            }
        )

    duplicate_candidates = random.sample(rows, 18)
    for row in duplicate_candidates:
        duplicate = row.copy()
        duplicate["status"] = messy_text("Closed")
        duplicate["resolution_hours"] = messy_number(random.uniform(12, 140))
        rows.append(duplicate)

    random.shuffle(rows)
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def normalize_text(value: str, default: str = "Unknown") -> str:
    cleaned = " ".join((value or "").strip().replace("-", " ").split()).title()
    if not cleaned:
        return default
    aliases = {
        "E Mail": "Email",
        "Web": "Web Form",
        "Online Form": "Web Form",
        "Call": "Phone",
        "Walk In": "Walk-In",
        "In Person": "Walk-In",
        "Referred": "Referral",
        "Complete": "Closed",
        "Done": "Closed",
        "Working": "In Progress",
        "Pending": "In Progress",
        "New": "Open",
        "It Support": "IT Support",
        "Service Follow Up": "Service Follow-Up",
    }
    return aliases.get(cleaned, cleaned)


def parse_date(value: str) -> date | None:
    value = (value or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%b %d %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_float(value: str) -> float | None:
    try:
        parsed = float((value or "").strip().replace("$", "").replace(",", ""))
    except ValueError:
        return None
    return parsed if parsed >= 0 else None


def parse_bool(value: str) -> int:
    return 1 if (value or "").strip().lower() in {"yes", "y", "true", "1"} else 0


def week_start(value: date) -> str:
    return (value - timedelta(days=value.weekday())).isoformat()


def median_by_priority(rows: list[dict[str, str]], column: str) -> dict[str, float]:
    values: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        priority = normalize_text(row.get("priority", ""), "Normal")
        parsed = parse_float(row.get(column, ""))
        if parsed is not None:
            values[priority].append(parsed)
    return {key: median(items) for key, items in values.items() if items}


def clean_dataset(raw_rows: list[dict[str, str]]) -> list[dict]:
    response_medians = median_by_priority(raw_rows, "response_hours")
    resolution_medians = median_by_priority(raw_rows, "resolution_hours")
    seen: dict[str, dict] = {}

    for raw in raw_rows:
        ticket_id = (raw.get("ticket_id") or "").strip()
        if not ticket_id:
            continue

        request_date = parse_date(raw.get("request_date", "")) or date(2026, 1, 5)
        request_type = normalize_text(raw.get("request_type", ""), "General Request")
        priority = normalize_text(raw.get("priority", ""), "Normal")
        status = normalize_text(raw.get("status", ""), "Open")
        department = normalize_text(raw.get("department", ""), "Unknown")
        if department == "Unknown" and request_type in REQUEST_TYPES:
            department = REQUEST_TYPES[request_type]["department"]
        elif department == "Unknown":
            department = "Admin Operations"

        response_hours = parse_float(raw.get("response_hours", ""))
        if response_hours is None:
            response_hours = response_medians.get(priority, response_medians.get("Normal", 6.0))

        resolution_hours = parse_float(raw.get("resolution_hours", ""))
        if status == "Closed" and resolution_hours is None:
            resolution_hours = resolution_medians.get(priority, resolution_medians.get("Normal", 36.0))
        if status != "Closed":
            resolution_hours = 0.0

        revenue_value = parse_float(raw.get("revenue_value", "")) or REQUEST_TYPES.get(request_type, {}).get("base_value", 250)
        cost_estimate = parse_float(raw.get("cost_estimate", "")) or revenue_value * 0.35
        satisfaction_score = parse_float(raw.get("satisfaction_score", "")) or 3.8
        satisfaction_score = min(5.0, max(1.0, satisfaction_score))

        response_sla = {"Urgent": 2, "High": 4, "Normal": 8, "Low": 16}.get(priority, 8)
        resolution_sla = {"Urgent": 24, "High": 36, "Normal": 72, "Low": 120}.get(priority, 72)

        cleaned = {
            "ticket_id": ticket_id,
            "request_date": request_date.isoformat(),
            "week_start": week_start(request_date),
            "channel": normalize_text(raw.get("channel", ""), "Unknown"),
            "department": department,
            "request_type": request_type,
            "customer_type": normalize_text(raw.get("customer_type", ""), "Unknown"),
            "priority": priority,
            "status": status,
            "response_hours": round(response_hours, 2),
            "resolution_hours": round(resolution_hours, 2),
            "response_sla_hours": response_sla,
            "resolution_sla_hours": resolution_sla,
            "first_response_met": int(response_hours <= response_sla),
            "resolution_sla_met": int(status != "Closed" or resolution_hours <= resolution_sla),
            "rework_required": parse_bool(raw.get("rework_required", "")),
            "revenue_value": round(revenue_value, 2),
            "cost_estimate": round(cost_estimate, 2),
            "estimated_margin": round(revenue_value - cost_estimate, 2),
            "satisfaction_score": round(satisfaction_score, 2),
        }

        existing = seen.get(ticket_id)
        if not existing or (existing["status"] != "Closed" and cleaned["status"] == "Closed"):
            seen[ticket_id] = cleaned

    return sorted(seen.values(), key=lambda item: (item["request_date"], item["ticket_id"]))


QUERIES = {
    "kpi_summary": """
SELECT
  COUNT(*) AS total_requests,
  SUM(CASE WHEN status = 'Closed' THEN 1 ELSE 0 END) AS closed_requests,
  SUM(CASE WHEN status <> 'Closed' THEN 1 ELSE 0 END) AS open_requests,
  ROUND(AVG(response_hours), 2) AS avg_response_hours,
  ROUND(AVG(CASE WHEN status = 'Closed' THEN resolution_hours END), 2) AS avg_resolution_hours,
  ROUND(100.0 * AVG(first_response_met), 1) AS first_response_sla_pct,
  ROUND(100.0 * AVG(resolution_sla_met), 1) AS resolution_sla_pct,
  ROUND(100.0 * AVG(rework_required), 1) AS rework_pct,
  ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
  ROUND(SUM(revenue_value), 2) AS revenue_supported,
  ROUND(SUM(estimated_margin), 2) AS estimated_margin
FROM operations_requests;
""",
    "weekly_metrics": """
SELECT
  week_start,
  COUNT(*) AS total_requests,
  SUM(CASE WHEN status <> 'Closed' THEN 1 ELSE 0 END) AS open_requests,
  ROUND(AVG(response_hours), 2) AS avg_response_hours,
  ROUND(100.0 * AVG(first_response_met), 1) AS first_response_sla_pct,
  ROUND(100.0 * AVG(rework_required), 1) AS rework_pct,
  ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
  ROUND(SUM(estimated_margin), 2) AS estimated_margin
FROM operations_requests
GROUP BY week_start
ORDER BY week_start;
""",
    "department_bottlenecks": """
SELECT
  department,
  COUNT(*) AS total_requests,
  SUM(CASE WHEN status <> 'Closed' THEN 1 ELSE 0 END) AS open_requests,
  ROUND(AVG(response_hours), 2) AS avg_response_hours,
  ROUND(AVG(CASE WHEN status = 'Closed' THEN resolution_hours END), 2) AS avg_resolution_hours,
  ROUND(100.0 * AVG(first_response_met), 1) AS first_response_sla_pct,
  ROUND(100.0 * AVG(resolution_sla_met), 1) AS resolution_sla_pct,
  ROUND(100.0 * AVG(rework_required), 1) AS rework_pct,
  ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction,
  ROUND(SUM(estimated_margin), 2) AS estimated_margin
FROM operations_requests
GROUP BY department
ORDER BY avg_resolution_hours DESC;
""",
    "request_type_roi": """
SELECT
  request_type,
  COUNT(*) AS request_count,
  ROUND(AVG(response_hours), 2) AS avg_response_hours,
  ROUND(AVG(CASE WHEN status = 'Closed' THEN resolution_hours END), 2) AS avg_resolution_hours,
  ROUND(100.0 * AVG(rework_required), 1) AS rework_pct,
  ROUND(SUM(revenue_value), 2) AS revenue_supported,
  ROUND(SUM(estimated_margin), 2) AS estimated_margin
FROM operations_requests
GROUP BY request_type
ORDER BY estimated_margin DESC;
""",
    "channel_performance": """
SELECT
  channel,
  COUNT(*) AS total_requests,
  ROUND(AVG(response_hours), 2) AS avg_response_hours,
  ROUND(100.0 * AVG(first_response_met), 1) AS first_response_sla_pct,
  ROUND(100.0 * AVG(rework_required), 1) AS rework_pct,
  ROUND(AVG(satisfaction_score), 2) AS avg_satisfaction
FROM operations_requests
GROUP BY channel
ORDER BY total_requests DESC;
""",
}


def load_sqlite(clean_rows: list[dict]) -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    columns = clean_rows[0].keys()
    column_defs = ", ".join(f"{column} TEXT" for column in columns)
    conn.execute(f"CREATE TABLE operations_requests ({column_defs})")
    placeholders = ", ".join("?" for _ in columns)
    conn.executemany(
        f"INSERT INTO operations_requests VALUES ({placeholders})",
        [[row[column] for column in columns] for row in clean_rows],
    )
    conn.commit()
    return conn


def run_query(conn: sqlite3.Connection, query: str) -> list[dict]:
    cursor = conn.execute(query)
    columns = [item[0] for item in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def write_query_outputs(conn: sqlite3.Connection) -> dict[str, list[dict]]:
    outputs: dict[str, list[dict]] = {}
    for name, query in QUERIES.items():
        rows = run_query(conn, query)
        outputs[name] = rows
        write_csv(ROOT / "data" / "processed" / f"{name}.csv", rows)
    SQL_PATH.write_text(
        "\n\n".join(f"-- {name}\n{query.strip()}" for name, query in QUERIES.items()) + "\n",
        encoding="utf-8",
    )
    return outputs


def format_money(value: float | int | str) -> str:
    return f"${float(value):,.0f}"


def format_pct(value: float | int | str) -> str:
    return f"{float(value):.1f}%"


def bar(value: float, maximum: float, label: str) -> str:
    width = 0 if maximum == 0 else max(4, min(100, value / maximum * 100))
    return f"""
    <div class="bar-row">
      <span>{label}</span>
      <div class="track"><div class="fill" style="width:{width:.1f}%"></div></div>
      <strong>{value:.1f}</strong>
    </div>
    """


def render_dashboard(outputs: dict[str, list[dict]]) -> None:
    kpi = outputs["kpi_summary"][0]
    weekly = outputs["weekly_metrics"]
    departments = outputs["department_bottlenecks"]
    channels = outputs["channel_performance"]
    request_types = outputs["request_type_roi"]

    max_dept_resolution = max(float(row["avg_resolution_hours"] or 0) for row in departments)
    max_margin = max(float(row["estimated_margin"] or 0) for row in request_types)

    department_bars = "\n".join(
        bar(float(row["avg_resolution_hours"] or 0), max_dept_resolution, row["department"])
        for row in departments
    )
    margin_bars = "\n".join(
        bar(float(row["estimated_margin"] or 0), max_margin, row["request_type"])
        for row in request_types[:7]
    )

    weekly_rows = "\n".join(
        f"""
        <tr>
          <td>{row['week_start']}</td>
          <td>{row['total_requests']}</td>
          <td>{row['open_requests']}</td>
          <td>{row['avg_response_hours']}</td>
          <td>{format_pct(row['first_response_sla_pct'])}</td>
          <td>{format_pct(row['rework_pct'])}</td>
          <td>{row['avg_satisfaction']}</td>
        </tr>
        """
        for row in weekly[-8:]
    )
    channel_rows = "\n".join(
        f"""
        <tr>
          <td>{row['channel']}</td>
          <td>{row['total_requests']}</td>
          <td>{row['avg_response_hours']}</td>
          <td>{format_pct(row['first_response_sla_pct'])}</td>
          <td>{format_pct(row['rework_pct'])}</td>
          <td>{row['avg_satisfaction']}</td>
        </tr>
        """
        for row in channels
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Business Operations Reporting Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #18212f;
      --muted: #607085;
      --line: #d8dee8;
      --bg: #f5f7fa;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-2: #b45309;
      --accent-3: #2563eb;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.45;
    }}
    header {{
      background: #111827;
      color: white;
      padding: 34px clamp(20px, 5vw, 64px);
    }}
    header p {{ color: #cbd5e1; max-width: 840px; margin: 8px 0 0; }}
    main {{ padding: 28px clamp(20px, 5vw, 64px) 48px; }}
    h1, h2 {{ margin: 0; letter-spacing: 0; }}
    h2 {{ font-size: 1.1rem; margin-bottom: 14px; }}
    .grid {{
      display: grid;
      gap: 16px;
    }}
    .kpis {{
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      margin-bottom: 24px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
      min-width: 0;
    }}
    .metric-label {{
      color: var(--muted);
      font-size: .82rem;
      font-weight: 650;
      text-transform: uppercase;
    }}
    .metric-value {{
      display: block;
      margin-top: 6px;
      font-size: clamp(1.35rem, 2.4vw, 2rem);
      font-weight: 760;
    }}
    .two-col {{
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      align-items: start;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: minmax(120px, 180px) 1fr 56px;
      align-items: center;
      gap: 10px;
      margin: 11px 0;
      font-size: .91rem;
    }}
    .track {{
      height: 10px;
      background: #e5e7eb;
      border-radius: 999px;
      overflow: hidden;
    }}
    .fill {{
      height: 100%;
      background: var(--accent);
      border-radius: inherit;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .9rem;
    }}
    th, td {{
      border-bottom: 1px solid var(--line);
      padding: 9px 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ color: var(--muted); font-size: .78rem; text-transform: uppercase; }}
    .recommendations {{
      border-left: 4px solid var(--accent);
    }}
    .recommendations li {{ margin-bottom: 8px; }}
    @media (max-width: 640px) {{
      .bar-row {{ grid-template-columns: 1fr; gap: 5px; }}
      table {{ display: block; overflow-x: auto; white-space: nowrap; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Business Operations Reporting Dashboard</h1>
    <p>Business Admin + CIST case study: cleaned messy service operations data, analyzed bottlenecks with SQL, and created a repeatable reporting dashboard for weekly management decisions.</p>
  </header>
  <main>
    <section class="grid kpis">
      <div class="card"><span class="metric-label">Requests Analyzed</span><span class="metric-value">{kpi['total_requests']}</span></div>
      <div class="card"><span class="metric-label">Open Backlog</span><span class="metric-value">{kpi['open_requests']}</span></div>
      <div class="card"><span class="metric-label">First Response SLA</span><span class="metric-value">{format_pct(kpi['first_response_sla_pct'])}</span></div>
      <div class="card"><span class="metric-label">Rework Rate</span><span class="metric-value">{format_pct(kpi['rework_pct'])}</span></div>
      <div class="card"><span class="metric-label">Avg Satisfaction</span><span class="metric-value">{kpi['avg_satisfaction']}/5</span></div>
      <div class="card"><span class="metric-label">Margin Supported</span><span class="metric-value">{format_money(kpi['estimated_margin'])}</span></div>
    </section>

    <section class="grid two-col">
      <div class="card">
        <h2>Department Resolution Bottlenecks</h2>
        {department_bars}
      </div>
      <div class="card">
        <h2>Highest-Value Request Types</h2>
        {margin_bars}
      </div>
    </section>

    <section class="grid two-col" style="margin-top:16px;">
      <div class="card">
        <h2>Last 8 Weeks</h2>
        <table>
          <thead><tr><th>Week</th><th>Req.</th><th>Open</th><th>Resp Hrs</th><th>SLA</th><th>Rework</th><th>Sat.</th></tr></thead>
          <tbody>{weekly_rows}</tbody>
        </table>
      </div>
      <div class="card">
        <h2>Channel Performance</h2>
        <table>
          <thead><tr><th>Channel</th><th>Req.</th><th>Resp Hrs</th><th>SLA</th><th>Rework</th><th>Sat.</th></tr></thead>
          <tbody>{channel_rows}</tbody>
        </table>
      </div>
    </section>

    <section class="card recommendations" style="margin-top:16px;">
      <h2>Management Recommendations</h2>
      <ul>
        <li>Create intake templates for Data & Reporting and Systems Operations requests, where resolution time and rework are highest.</li>
        <li>Move repeat billing and vendor updates into a weekly batch workflow to reduce context switching for admin staff.</li>
        <li>Use the dashboard as a Monday operating review: backlog, SLA misses, rework causes, and high-value automation opportunities.</li>
      </ul>
    </section>
  </main>
</body>
</html>
"""
    (REPORT_DIR / "operations_dashboard.html").write_text(html, encoding="utf-8")


def write_executive_summary(outputs: dict[str, list[dict]]) -> None:
    kpi = outputs["kpi_summary"][0]
    bottleneck = outputs["department_bottlenecks"][0]
    top_value = outputs["request_type_roi"][0]
    summary = f"""# Executive Summary

## Project
Business Operations Reporting & Automation Case Study

## Business Problem
A service-based operation was handling requests across email, web forms, phone calls, referrals, and walk-ins. Leadership needed a cleaner weekly view of request volume, response speed, rework, backlog, customer satisfaction, and high-value automation opportunities.

## What I Built
- Generated and cleaned a messy operations dataset with duplicate tickets, inconsistent labels, missing values, and invalid numeric fields.
- Built a repeatable Python cleaning workflow.
- Loaded the cleaned data into SQLite and used SQL to calculate KPIs.
- Created a static management dashboard for weekly operating reviews.
- Produced CSV outputs that can be opened in Excel, Google Sheets, Power BI, or Tableau.

## Key Findings
- Total requests analyzed: {kpi['total_requests']}
- Open backlog: {kpi['open_requests']}
- First response SLA: {format_pct(kpi['first_response_sla_pct'])}
- Rework rate: {format_pct(kpi['rework_pct'])}
- Average satisfaction: {kpi['avg_satisfaction']}/5
- Estimated margin supported: {format_money(kpi['estimated_margin'])}
- Largest resolution bottleneck: {bottleneck['department']} at {bottleneck['avg_resolution_hours']} average resolution hours
- Highest-value request type: {top_value['request_type']} with {format_money(top_value['estimated_margin'])} estimated margin

## Recommendation
Use this reporting system as a weekly admin operations review. The biggest improvement opportunity is reducing rework and resolution time in complex technical/admin requests through better intake forms, clearer routing rules, and automation of recurring low-value tasks.

## Skills Demonstrated
Python, SQL, SQLite, CSV data cleaning, KPI design, dashboard creation, business operations analysis, process improvement, and CIST-style systems thinking.
"""
    (REPORT_DIR / "executive_summary.md").write_text(summary, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw_rows = generate_raw_dataset()
    write_csv(RAW_PATH, raw_rows)
    clean_rows = clean_dataset(raw_rows)
    write_csv(CLEAN_PATH, clean_rows)
    conn = load_sqlite(clean_rows)
    try:
        outputs = write_query_outputs(conn)
    finally:
        conn.close()
    render_dashboard(outputs)
    write_executive_summary(outputs)
    print(f"Generated raw rows: {len(raw_rows)}")
    print(f"Clean rows after dedupe: {len(clean_rows)}")
    print(f"Dashboard: {REPORT_DIR / 'operations_dashboard.html'}")
    print(f"Executive summary: {REPORT_DIR / 'executive_summary.md'}")


if __name__ == "__main__":
    main()
