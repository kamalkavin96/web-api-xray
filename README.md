# web-api-xray

![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-Framework-009688?logo=fastapi&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-Browser_Automation-45ba4b?logo=playwright&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10+-yellow?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Docker Compose](https://img.shields.io/badge/Docker%20Compose-Supported-2496ED?logo=docker)
![Swagger](https://img.shields.io/badge/Swagger-UI-85EA2D?logo=swagger&logoColor=black)
![REST API](https://img.shields.io/badge/API-REST-orange)
![Chromium](https://img.shields.io/badge/Browser-Chromium-lightgrey?logo=googlechrome)
![Open Source](https://img.shields.io/badge/Open%20Source-Yes-brightgreen)





![Web API Xray](assets/web-api-xray.png)


Web API Xray is a FastAPI-based service that uses Playwright and Docker to launch a real browser, observe network traffic, and capture backend API requests and responses from JavaScript-rendered web pages.



## 🔌 API Endpoints

Base URL:
```
http://localhost:7860
```

---

## 1️⃣ Capture a Specific Target API

### POST `/capture/target`

Captures **one specific backend API request/response** by matching a URL substring and HTTP method.

### Request Body
```json
{
  "goto_url": "https://example.com",
  "capture_url_contains": "/api/search",
  "method": "GET",
  "timeout_ms": 15000
}
```

### Request Fields
| Field | Type | Required | Description |
|-----|-----|-----|-----|
| goto_url | string | ✅ | Page URL to open |
| capture_url_contains | string | ✅ | Substring to match API URL |
| method | string | ❌ | HTTP method (default: GET) |
| timeout_ms | number | ❌ | Max wait time in ms |

### Success Response
```json
{
  "status": "success",
  "url": "https://example.com/api/search?q=test",
  "status_code": 200,
  "headers": {
    "content-type": "application/json",
    "cache-control": "no-cache"
  },
  "data": {
    "results": [
      { "id": 1, "name": "Item A" },
      { "id": 2, "name": "Item B" }
    ]
  }
}
```

### Error Response
```json
{
  "detail": "Target API not captured"
}
```

---

## 2️⃣ Capture All Network Requests & Responses (Basic)

### POST `/capture/all`

### Request Body
```json
{
  "goto_url": "https://example.com",
  "timeout_ms": 15000
}
```

### Success Response
```json
{
  "status": "success",
  "events": [
    { "type": "request", "method": "GET", "url": "https://example.com/api/init" },
    { "type": "response", "status": 200, "url": "https://example.com/api/init" }
  ]
}
```

---

## 3️⃣ Capture Full Network Details (Advanced)

### POST `/capture/full`

### Request Body
```json
{
  "goto_url": "https://example.com",
  "timeout_ms": 15000
}
```

### Success Response
```json
{
  "status": "success",
  "events": [
    {
      "type": "request",
      "url": "https://example.com/api/data",
      "method": "POST",
      "headers": { "content-type": "application/json" },
      "post_data": "{\"query\":\"test\"}",
      "resource_type": "xhr",
      "timestamp": 1710000000.123
    },
    {
      "type": "response",
      "url": "https://example.com/api/data",
      "status": 200,
      "status_text": "OK",
      "headers": { "content-type": "application/json" },
      "body": "{\"success\":true}",
      "timestamp": 1710000000.456
    }
  ]
}
```

---

## 🐳 Docker Commands

### Build Image
```bash
docker build -t web-api-xray .
```

### Run Container
```bash
docker run -d --name web-api-xray -p 7860:7860 web-api-xray
```

### Stop Container
```bash
docker stop web-api-xray
```
```

---

## 📘 API Docs

- Swagger UI: http://localhost:7860/docs
- OpenAPI: http://localhost:7860/openapi.json
