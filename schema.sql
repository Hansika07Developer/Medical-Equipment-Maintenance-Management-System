-- MEMMS MySQL 8 schema. Flask-SQLAlchemy models are the canonical schema.
CREATE DATABASE IF NOT EXISTS memms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE memms_db;

CREATE TABLE departments (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL UNIQUE,
 location VARCHAR(150)
) ENGINE=InnoDB;

CREATE TABLE users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 full_name VARCHAR(120) NOT NULL,
 email VARCHAR(160) NOT NULL UNIQUE,
 password_hash VARCHAR(255) NOT NULL,
 role VARCHAR(30) NOT NULL DEFAULT 'DEPARTMENT_STAFF',
 department_id INT NULL,
 active BOOLEAN NOT NULL DEFAULT TRUE,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT fk_user_department FOREIGN KEY (department_id) REFERENCES departments(id)
) ENGINE=InnoDB;

CREATE TABLE equipment (
 id INT AUTO_INCREMENT PRIMARY KEY,
 asset_code VARCHAR(50) NOT NULL UNIQUE,
 name VARCHAR(150) NOT NULL,
 category VARCHAR(100), manufacturer VARCHAR(120), model VARCHAR(120),
 serial_number VARCHAR(120) UNIQUE, location VARCHAR(150),
 purchase_date DATE, warranty_expiry DATE,
 maintenance_interval_days INT DEFAULT 90,
 status VARCHAR(30) NOT NULL DEFAULT 'AVAILABLE',
 department_id INT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_equipment_status(status),
 CONSTRAINT fk_equipment_department FOREIGN KEY (department_id) REFERENCES departments(id)
) ENGINE=InnoDB;

CREATE TABLE maintenance (
 id INT AUTO_INCREMENT PRIMARY KEY,
 equipment_id INT NOT NULL,
 maintenance_type VARCHAR(30) NOT NULL DEFAULT 'PREVENTIVE',
 scheduled_date DATE NOT NULL,
 completed_date DATE,
 status VARCHAR(30) NOT NULL DEFAULT 'SCHEDULED',
 technician_id INT NULL,
 work_description TEXT,
 downtime_hours DOUBLE DEFAULT 0,
 cost DECIMAL(12,2) DEFAULT 0,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 INDEX idx_maintenance_due(status,scheduled_date),
 FOREIGN KEY (equipment_id) REFERENCES equipment(id),
 FOREIGN KEY (technician_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE service_requests (
 id INT AUTO_INCREMENT PRIMARY KEY,
 equipment_id INT NOT NULL,
 reported_by_id INT NOT NULL,
 assigned_to_id INT NULL,
 issue_description TEXT NOT NULL,
 priority VARCHAR(20) NOT NULL DEFAULT 'MEDIUM',
 status VARCHAR(30) NOT NULL DEFAULT 'OPEN',
 reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 started_at DATETIME NULL,
 resolved_at DATETIME NULL,
 downtime_hours DOUBLE DEFAULT 0,
 repair_notes TEXT,
 INDEX idx_ticket_status(status,priority),
 FOREIGN KEY (equipment_id) REFERENCES equipment(id),
 FOREIGN KEY (reported_by_id) REFERENCES users(id),
 FOREIGN KEY (assigned_to_id) REFERENCES users(id)
) ENGINE=InnoDB;

CREATE TABLE spare_parts (
 id INT AUTO_INCREMENT PRIMARY KEY,
 part_code VARCHAR(50) NOT NULL UNIQUE,
 part_name VARCHAR(150) NOT NULL,
 quantity INT NOT NULL DEFAULT 0,
 minimum_stock INT NOT NULL DEFAULT 5,
 unit_price DECIMAL(12,2) DEFAULT 0
) ENGINE=InnoDB;

CREATE TABLE parts_usage (
 id INT AUTO_INCREMENT PRIMARY KEY,
 part_id INT NOT NULL,
 maintenance_id INT NULL,
 service_request_id INT NULL,
 quantity_used INT NOT NULL,
 used_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (part_id) REFERENCES spare_parts(id),
 FOREIGN KEY (maintenance_id) REFERENCES maintenance(id),
 FOREIGN KEY (service_request_id) REFERENCES service_requests(id)
) ENGINE=InnoDB;

CREATE TABLE audit_logs (
 id INT AUTO_INCREMENT PRIMARY KEY,
 user_id INT NULL,
 action VARCHAR(120) NOT NULL,
 entity_type VARCHAR(80), entity_id INT, details TEXT,
 created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users(id)
) ENGINE=InnoDB;
