# Case Study: Business Operations Reporting & Automation System

## One-Line Summary

I built a Python and SQL reporting system that turns messy service operations data into a weekly dashboard for backlog, response time, rework, customer satisfaction, and process improvement decisions.

## My Positioning

I am building from a Business Administration + CIST foundation, so this project focuses on the bridge between business operations and technical systems. The goal was to show that I can work with messy operational data, design useful reporting logic, and communicate business recommendations clearly.

## Business Problem

The fictional organization receives service requests across email, web forms, phone calls, referrals, and walk-ins. Like many small businesses and admin teams, it has data but not a reliable reporting system.

The source data has common real-world problems:

- Duplicated request IDs
- Inconsistent department, channel, and status labels
- Missing response and resolution times
- Mixed date formats
- Invalid negative values
- No standardized KPI fields
- No dashboard for weekly review

Without a clean process, the team cannot quickly answer:

- Where is the backlog building?
- Which departments are slowest to resolve requests?
- Which channels create more rework?
- Which request types create the most value?
- Where should automation be introduced first?

## Solution Built

I created a repeatable operations reporting workflow.

1. **Raw data generation:** Built a realistic messy dataset with 658 service request records.
2. **Python cleaning pipeline:** Standardized categories, dates, missing values, boolean fields, and numeric values.
3. **Deduplication:** Reduced the dataset to 640 clean request records.
4. **KPI design:** Added fields for first-response SLA, resolution SLA, backlog, rework, satisfaction, revenue supported, cost estimate, and estimated margin.
5. **SQLite reporting database:** Loaded the clean dataset into SQLite for reusable analysis.
6. **SQL analysis:** Created KPI summary, weekly performance, department bottlenecks, channel performance, and request-type ROI queries.
7. **Dashboard and summary:** Generated a static HTML dashboard and executive summary for management review.
8. **Excel reporting version:** Built a client-friendly Excel workbook with dashboard KPIs, analysis sheets, preview images, and native charts.

## Tools Used

- Python
- SQL
- SQLite
- CSV
- HTML/CSS
- Excel workbook dashboard
- Business operations analysis
- KPI design

## Results

- Raw records: 658
- Clean records after deduplication: 640
- Open backlog identified: 229 requests
- First-response SLA performance: 95.8%
- Rework rate: 14.4%
- Average satisfaction: 4.23/5
- Estimated margin supported: $158,891
- Largest bottleneck: Systems Operations
- Highest-value request type: Dashboard Requests

## Business Recommendations

Based on the analysis, the team should:

- Improve intake forms for Systems Operations and Data & Reporting requests.
- Standardize recurring request categories to reduce manual cleanup.
- Track rework weekly because it is a strong signal of unclear process design.
- Batch low-value admin tasks like vendor record updates and billing questions.
- Use the dashboard as a weekly operating review rather than a one-time report.

## Why This Project Matters

This project is intentionally practical. Many small organizations do not need a complex AI product first. They need their spreadsheet data cleaned, their KPIs defined, their reporting process automated, and their decisions made clearer.

That is the gap this project targets.

## What This Demonstrates

This case study shows that I can:

- Translate a business problem into a data workflow.
- Clean messy data programmatically.
- Use SQL to answer business questions.
- Design KPIs around operations, not vanity metrics.
- Build simple dashboards for decision-makers.
- Package the same analysis into Excel for business users.
- Explain insights in plain business language.

## Professional Relevance

This project supports beginner-to-intermediate client, internship, and analyst work such as:

- Spreadsheet cleanup and reporting
- Excel/CSV dashboard preparation
- Weekly KPI reporting
- SQL reporting setup
- Operations dashboard creation
- Admin workflow analysis
- Automation opportunity audits

## Next Iteration

The next version should include a Power BI dashboard and a short video walkthrough so the project is easier to review quickly.
