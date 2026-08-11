# OpenRCA_DTH

## 📌 Giới thiệu

OpenRCA_DTH là ứng dụng hỗ trợ phân tích sự cố sử dụng AI Agent.
Dự án sử dụng Streamlit làm giao diện, PostgreSQL làm cơ sở dữ liệu và Gemini API để hỗ trợ phân tích.

---

# ⚙️ Cài đặt

## 1. Clone repository

```bash
git clone https://github.com/<username>/OpenRCA_DTH.git

cd OpenRCA_DTH
```

---

## 2. Tạo môi trường ảo

```bash
python -m venv .venv
```

Kích hoạt môi trường:

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 3. Cài đặt thư viện

```bash
pip install -r requirements.txt
```

---

# 🗄️ Database Setup

## 1. Tạo database PostgreSQL

```sql
CREATE DATABASE openrca;
```

---

## 2. Import database

File database:

```
openrca_database.sql
```

Import bằng lệnh:

```bash
psql -U <username> -d openrca -f openrca_database.sql
```

Sau khi import thành công, kiểm tra bảng:

```sql
\dt
```

---

# 🔐 Environment Variables

Tạo file `.env` trong thư mục gốc của project:

```env
DATABASE_HOST=<database_host>

DATABASE_PORT=5432

DATABASE_NAME=openrca

DATABASE_USER=<username>

DATABASE_PASSWORD=<password>

GOOGLE_API_KEY=<gemini_api_key>
```

---

# ▶️ Chạy ứng dụng

Chạy Streamlit:

```bash
streamlit run app.py
```

Ứng dụng sẽ chạy tại:

```
http://localhost:8501
```

---

# 📥 Input

## Incident Input

Người dùng nhập thông tin sự cố:

| Field       | Mô tả                  |
| ----------- | ---------------------- |
| Title       | Tiêu đề sự cố          |
| Description | Mô tả chi tiết sự cố   |
| Severity    | Mức độ nghiêm trọng    |
| Category    | Loại sự cố             |
| Timestamp   | Thời gian xảy ra sự cố |

---

## Investigation Metrics Input

Dữ liệu metrics được lưu trong bảng:

```
investigation_metrics
```

Bao gồm các thông tin phục vụ quá trình phân tích sự cố.

Ví dụ:

| Field        | Mô tả              |
| ------------ | ------------------ |
| metric_name  | Tên chỉ số         |
| metric_value | Giá trị đo được    |
| timestamp    | Thời gian ghi nhận |

---

# 📂 Cấu trúc file quan trọng

```
OpenRCA_DTH/

├── app.py

├── openrca_database.sql

├── requirements.txt

├── .env

├── pages/

└── src/
```
