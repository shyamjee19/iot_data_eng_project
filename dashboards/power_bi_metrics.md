# 📊 Power BI Dashboard Resource Kit

Because Power BI Desktop uses a proprietary, binary file format (`.pbix`), it cannot be compiled directly by an AI. However, **this kit contains all the heavy lifting** you need to build a professional, industry-standard dashboard in Power BI Desktop in under 10 minutes.

---

## 🛠️ Step 1: Connecting Power BI to PostgreSQL

1. Open **Power BI Desktop** (Free).
2. Click **Get Data** ➔ **PostgreSQL database**.
3. Fill in the connection coordinates from `configs/settings.py`:
   * **Server**: `localhost:5432`
   * **Database**: `iot_db`
4. Under **Data Connectivity Mode**, select:
   * **DirectQuery** (for real-time live sensor updates)
5. Enter credentials:
   * **Username**: `admin`
   * **Password**: `admin123`

---

## 🗄️ Step 2: Create Optimized SQL Views (Analytical Layer)

Instead of importing raw, messy tables directly into Power BI, data engineers create **Database Views**. This keeps the Power BI model fast and simple.

Run these SQL scripts against your PostgreSQL database to create optimized analytical views (you can copy-paste this into pgAdmin, or I can execute it for you):

```sql
-- 1. Create a View for real-time KPI indicators
CREATE OR REPLACE VIEW view_realtime_kpis AS
SELECT 
    device_id,
    ROUND(AVG(temperature), 2) AS current_temp,
    ROUND(AVG(vibration), 2) AS current_vibration,
    ROUND(AVG(pressure), 2) AS current_pressure,
    MAX(event_time) AS last_reported_time
FROM telemetry_data
WHERE event_time >= NOW() - INTERVAL '5 minutes'
GROUP BY device_id;

-- 2. Create a View for daily aggregation trends
CREATE OR REPLACE VIEW view_daily_device_analytics AS
SELECT 
    device_id,
    DATE(event_time) AS reporting_date,
    ROUND(MIN(temperature), 2) AS min_temp,
    ROUND(MAX(temperature), 2) AS max_temp,
    ROUND(AVG(temperature), 2) AS avg_temp,
    ROUND(AVG(vibration), 2) AS avg_vibration,
    ROUND(AVG(pressure), 2) AS avg_pressure,
    COUNT(*) AS total_telemetry_points
FROM telemetry_data
GROUP BY device_id, DATE(event_time);
```

---

## 🔢 Step 3: Reusable DAX Formulas (Copy-Paste Measures)

Inside Power BI, you will need to create **Measures** using **DAX** (Data Analysis Expressions) to calculate KPI cards and alert warnings. Here are the exact formulas to copy-paste:

### A. Temperature Alert Status (Visual Indicator)
Create a new measure to flag if a machine is overheating:
```dax
TempAlertStatus = 
IF(
    SELECTEDVALUE(view_realtime_kpis[current_temp]) > 80, 
    "🚨 OVERHEATING (CRITICAL)", 
    "🟢 NORMAL"
)
```

### B. Machine Status Alert (Combined Risk)
Flag machines with combined high temperature and high vibration:
```dax
MachineRiskScore = 
IF(
    SELECTEDVALUE(view_realtime_kpis[current_temp]) > 80 && SELECTEDVALUE(view_realtime_kpis[current_vibration]) > 0.8,
    "CRITICAL RISK",
    IF(
        SELECTEDVALUE(view_realtime_kpis[current_temp]) > 60 || SELECTEDVALUE(view_realtime_kpis[current_vibration]) > 0.6,
        "WARNING",
        "STABLE"
    )
)
```

### C. Total Daily Active Events
```dax
ProcessedEventCount = SUM(view_daily_device_analytics[total_telemetry_points])
```

---

## 🎨 Step 4: Recommended Visual Layout

To build a professional factory dashboard, arrange your Power BI canvas with this layout:

| Visual Type | Fields to Use | Purpose |
| :--- | :--- | :--- |
| **Slicer (Filter)** | `view_realtime_kpis[device_id]` | Allows clicking between `motor-01`, `motor-02`, and `pump-01` |
| **Multi-Row Card** | `current_temp`, `current_vibration`, `current_pressure` | Displays real-time live sensor numbers |
| **Line Chart** | **Axis**: `event_time` <br>**Values**: `temperature` | Real-time trend line showing temperature shifts |
| **Donut Chart** | **Legend**: `MachineRiskScore` <br>**Values**: Count of `device_id` | Shows percentage of healthy vs. unstable machinery |
