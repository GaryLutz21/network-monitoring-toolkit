# Network Monitoring & Analysis Toolkit

## 📌 Overview
Network Monitoring & Analysis Toolkit is a Python-based system designed to monitor host availability, detect network incidents, and analyze performance metrics.  

The system performs periodic checks on hosts, stores results in a PostgreSQL database, and generates metrics such as availability, downtime, and latency. Data can also be exported and visualized using Power BI.

---

## 🚀 Features
- Periodic host monitoring using ICMP (ping)
- Logging of checks into a PostgreSQL database
- Detection of state changes (UP/DOWN)
- Automatic incident management (open/close incidents)
- Calculation of key metrics:
  - Availability (%)
  - Number of outages
  - Total downtime
  - Average latency
- Report generation in console
- Export of data to CSV files (`report.csv`, `checks_report.csv`)

---

## 🧱 Project Structure

Create a `.env` file with the following variables:

DB_HOST=localhost
DB_NAME=your_database
DB_USER=your_user
DB_PASSWORD=your_password

app/
│── db.py # Database connection
│── monitor.py # Host monitoring logic
│── incidents.py # Incident detection and management
│── reporter.py # Metrics calculation and reporting
│── main.py # Main execution script

sql/
│── schema.sql # Database schema

## 🗄️ Database Schema
The system uses three main tables:
- **hosts** → Registered hosts to monitor  
- **checks** → Historical monitoring data  
- **incidents** → Detected network incidents  

---

## ⚙️ Technologies Used
- Python
- PostgreSQL
- psycopg2
- Power BI (for visualization)

---

## ▶️ How to Run

1. Create a PostgreSQL database  
2. Execute the schema:
   ```sql
   sql/schema.sql
  Feel free to modify the hosts table to include additional hosts depending on your monitoring needs.
3. Configure database credentials in:
app/db.py
4. Run the application:
python app/main.py

## 📊 Visualization
Data can be exported to CSV and analyzed in Power BI for:
- Availability dashboards
- Latency analysis
- Host status tracking
- Time-based network behavior analysis

## 🧠 Future Improvements
- Real-time alerting system
- Advanced historical analysis
- Web-based dashboard
- Configurable monitoring intervals

## 📎 Notes

This project simulates a basic network monitoring system, focusing on availability tracking and incident management.