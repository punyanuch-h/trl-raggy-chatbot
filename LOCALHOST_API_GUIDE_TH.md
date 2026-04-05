# คู่มือรันโปรเจกต์และทดสอบ API บน localhost

เอกสารนี้อัปเดตให้ตรงกับ implementation ปัจจุบันของโปรเจกต์ โดย endpoint `/raggy/trl` จะส่งกลับ `answer_markdown` เพียง field เดียว

## 1. สิ่งที่ต้องมี

- Python 3.11 หรือ 3.12
- PowerShell บน Windows
- OpenAI API Key
- Pinecone API Key

## 2. Clone โปรเจกต์และเข้าโฟลเดอร์

```powershell
git clone <repo-url>
cd trl-raggy-chatbot
```

## 3. สร้าง virtual environment และติดตั้ง dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

ถ้า PowerShell block การ activate ให้รัน:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## 4. สร้างไฟล์ `.env`

สร้างไฟล์ `.env` ที่ root ของโปรเจกต์:

```env
JWT_PUBLIC_KEY=
JWT_PUBLIC_KEY_V1=
JWT_PUBLIC_KEY_FILE=
JWT_AUDIENCE=
JWT_ISSUER=
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_INDEX_NAME=raggy-bot-trl
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1
```

หมายเหตุ:
- `main.py` โหลดค่าจาก `.env` อัตโนมัติสำหรับการรัน local
- ถ้าใช้ endpoint อื่นแทน OpenAI ตรงๆ สามารถเปลี่ยน `OPENAI_BASE_URL` ได้
- ไม่ควร commit `.env` ที่มี secret จริง

## 5. เตรียมข้อมูลสำหรับ RAG

วางไฟล์ PDF ลงใน:
- `source/` สำหรับเอกสารทั่วไป
- `source/private/` สำหรับเอกสารที่ admin เท่านั้นควรเข้าถึงได้

จากนั้น re-index ข้อมูลเข้า Pinecone:

```powershell
python reindex.py
```

## 6. รัน API บน localhost

```powershell
python main.py
```

เมื่อรันสำเร็จ API จะเปิดที่:
- `http://127.0.0.1:8080`
- Swagger UI: `http://127.0.0.1:8080/docs`

หมายเหตุ:
- local default port จริงคือ `8080`
- ตอน deploy cloud ระบบจะใช้ค่า `PORT` จาก environment แทน

## 7. ใช้ JWT token สำหรับทดสอบ

API นี้ต้องส่ง `Authorization: Bearer <token>` ทุกครั้ง

ถ้า JWT จาก `trl-backend` มี claim `aud` หรือ `iss` และคุณต้องการให้ API ตรวจค่าเหล่านี้ด้วย ให้ตั้งค่า:
- `JWT_AUDIENCE` ให้ตรงกับค่า `aud`
- `JWT_ISSUER` ให้ตรงกับค่า `iss`

ถ้าไม่ได้ตั้งค่า `JWT_AUDIENCE` ระบบจะยังรับ token ที่มี `aud` ได้อยู่ แต่จะไม่บังคับตรวจความตรงกันของ audience ในโหมด local

โปรเจ็กต์นี้รองรับ `RS256` เท่านั้น:
- ให้นำ token จริงจาก `trl-backend` login flow มาใช้
- ให้ใส่ RSA public key ลงใน `JWT_PUBLIC_KEY`
- ถ้ามี `kid` ใน header เช่น `kid: "v1"` สามารถใส่ key เฉพาะตัวนั้นใน `JWT_PUBLIC_KEY_V1` ได้
- หรือจะเก็บ public key ไว้ในไฟล์ PEM แล้วตั้ง `JWT_PUBLIC_KEY_FILE` แทนก็ได้

ตัวอย่าง:

```env
JWT_PUBLIC_KEY_V1="-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQE...
-----END PUBLIC KEY-----"
JWT_AUDIENCE=trl-frontend
JWT_ISSUER=trl-backend
```

เก็บ token ไว้ในตัวแปร:

```powershell
$TOKEN = "วาง-token-ที่สร้างได้ตรงนี้"
```

## 8. ทดสอบเรียก API จาก localhost

### วิธีที่ 1: ผ่าน Swagger UI

เปิด:

```text
http://127.0.0.1:8080/docs
```

จากนั้น:
1. เลือก `POST /raggy/trl`
2. กด `Try it out`
3. กรอก `Authorization` เป็น `Bearer <token>`
4. ใส่ request body:

```json
{
  "query": "What are TRL levels 1 to 9?"
}
```

### วิธีที่ 2: ผ่าน PowerShell

```powershell
$headers = @{
    Authorization = "Bearer $TOKEN"
    "Content-Type" = "application/json"
}

$body = @{
    query = "What are TRL levels 1 to 9?"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8080/raggy/trl" -Method Post -Headers $headers -Body $body
```

## 9. ตัวอย่าง response ปัจจุบัน

```json
{
  "answer_markdown": "## TRL Response\n\nTRL 1 begins with basic principles and early observation."
}
```

คำอธิบาย:
- `answer_markdown` คือคำตอบหลักของ API
- output ถูกออกแบบให้ frontend render เป็น markdown ได้โดยตรง
- markdown ที่คาดหวังคือ heading ระดับ 2, ย่อหน้าสั้น, และ bullet list แบบปลอดภัย

## 10. ทดสอบ local test environment

รัน test ทั้งชุดมาตรฐาน:

```powershell
.\run_tests.bat
```

หรือรันเฉพาะส่วนที่เกี่ยวกับ endpoint นี้:

```powershell
.\.venv\Scripts\pytest.exe tests\test_api.py tests\test_integration.py tests\test_response_formatter.py tests\test_prompts.py
```

## 11. ปัญหาที่พบบ่อย

### 11.1 `.env` ไม่ถูกอ่าน

ให้ตรวจสอบว่า:
- เปิดใช้ virtual environment แล้ว
- มีไฟล์ `.env` อยู่ที่ root ของโปรเจกต์
- ชื่อ key ใน `.env` สะกดถูกต้อง

### 11.2 API ตอบกลับเป็นข้อความขอให้ล็อกอินใหม่

มักเกิดจาก JWT token ไม่ถูกต้อง หมดอายุ หรือไม่ได้ส่ง header `Authorization`

รูปแบบที่ถูกต้อง:

```text
Authorization: Bearer <your-token>
```

### 11.3 API รันได้ แต่คำตอบไม่ตรงเอกสาร

ให้ตรวจสอบว่า:
- มีไฟล์ PDF ใน `source/` หรือ `source/private/`
- เคยรัน `python reindex.py` แล้ว
- Pinecone index ตรงกับค่า `PINECONE_INDEX_NAME`

## 12. สรุปคำสั่งที่ใช้บ่อย

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python reindex.py
python main.py
.\run_tests.bat
```
