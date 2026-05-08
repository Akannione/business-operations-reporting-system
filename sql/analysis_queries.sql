-- kpi_summary
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

-- weekly_metrics
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

-- department_bottlenecks
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

-- request_type_roi
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

-- channel_performance
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
