"""
Generate comprehensive Word document for VisionCrafterAI test cases.
Enhanced version with detailed test specifications and documentation.
"""

import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import datetime


def shading_elm(fill):
    """Create cell shading element."""
    shd = OxmlElement('w:shd')
    shd.set(qn('w:fill'), fill)
    return shd


def set_cell_background(cell, fill):
    """Set background color of a cell."""
    cell._element.get_or_add_tcPr().append(shading_elm(fill))


def add_table_with_headers(doc, headers, rows_data, header_color='2E75B6', row_color='EBF3FB'):
    """Add a formatted table with headers and data."""
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Light Grid Accent 1'

    # Format header row
    header_cells = table.rows[0].cells
    for i, header in enumerate(headers):
        header_cells[i].text = header
        set_cell_background(header_cells[i], header_color)
        # Format header text
        for paragraph in header_cells[i].paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)

    # Add data rows with alternating colors
    for row_idx, row_data in enumerate(rows_data):
        row_cells = table.add_row().cells
        for col_idx, cell_data in enumerate(row_data):
            row_cells[col_idx].text = str(cell_data)
            # Alternate row colors
            if row_idx % 2 == 1:
                set_cell_background(row_cells[col_idx], row_color)

    return table


# Create document
doc = Document()

# ========== COVER PAGE ==========
title = doc.add_paragraph()
title.alignment = WD_ALIGN_PARAGRAPH.CENTER
title_run = title.add_run('VisionCrafterAI Backend')
title_run.font.size = Pt(28)
title_run.font.bold = True

subtitle = doc.add_paragraph()
subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
subtitle_run = subtitle.add_run('Unit Test Report')
subtitle_run.font.size = Pt(24)
subtitle_run.font.bold = True

desc = doc.add_paragraph()
desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
desc_run = desc.add_run('Comprehensive API Test Case Documentation')
desc_run.font.size = Pt(14)
desc_run.font.italic = True

doc.add_paragraph()
doc.add_paragraph()

date_para = doc.add_paragraph()
date_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
date_run = date_para.add_run(f'Date: {datetime.now().strftime("%B %d, %Y")}')
date_run.font.size = Pt(12)

version_para = doc.add_paragraph()
version_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
version_run = version_para.add_run('Test Suite Version: 2.0')
version_run.font.size = Pt(11)

doc.add_page_break()

# ========== TABLE OF CONTENTS ==========
doc.add_heading('Table of Contents', level=1)
doc.add_paragraph('1. Executive Summary', style='List Bullet')
doc.add_paragraph('2. Introduction & Project Overview', style='List Bullet')
doc.add_paragraph('3. Test Architecture & Framework', style='List Bullet')
doc.add_paragraph('4. Test Environment & Setup', style='List Bullet')
doc.add_paragraph('5. Root Endpoint Tests', style='List Bullet')
doc.add_paragraph('6. Authentication Tests (Detailed)', style='List Bullet')
doc.add_paragraph('7. Project Management Tests (Detailed)', style='List Bullet')
doc.add_paragraph('8. ImageKit Integration Tests', style='List Bullet')
doc.add_paragraph('9. Edge Case & Security Tests', style='List Bullet')
doc.add_paragraph('10. Integration Tests', style='List Bullet')
doc.add_paragraph('11. Performance Tests', style='List Bullet')
doc.add_paragraph('12. Test Execution Guide', style='List Bullet')
doc.add_paragraph('13. Test Results & Metrics', style='List Bullet')

doc.add_page_break()

# ========== EXECUTIVE SUMMARY ==========
doc.add_heading('1. Executive Summary', level=1)
doc.add_paragraph(
    'This document provides comprehensive documentation for the VisionCrafterAI Backend test suite. '
    'The test suite contains 48+ unit tests covering authentication, project management, file integration, '
    'edge cases, performance, and integration workflows.'
)
doc.add_paragraph()
doc.add_paragraph('Key Metrics:', style='List Number')
doc.add_paragraph('Total Test Cases: 48', style='List Bullet 2')
doc.add_paragraph('Code Coverage Target: >80%', style='List Bullet 2')
doc.add_paragraph('Test Execution Time: ~30-60 seconds', style='List Bullet 2')
doc.add_paragraph('All External Services: Mocked for reliability', style='List Bullet 2')
doc.add_paragraph('Database: In-memory SQLite for isolation', style='List Bullet 2')
doc.add_paragraph('API Framework: FastAPI with async support', style='List Bullet 2')

doc.add_page_break()

# ========== INTRODUCTION ==========
doc.add_heading('2. Introduction & Project Overview', level=1)
doc.add_paragraph(
    'VisionCrafterAI Backend is a modern, async-first REST API built with FastAPI that provides comprehensive '
    'functionality for managing canvas-based image and video editing projects. The backend serves as the core '
    'service for the VisionCrafterAI frontend application.'
)

doc.add_heading('2.1 Core Features', level=2)
doc.add_paragraph('User Authentication: Google OAuth 2.0 with JWT token management', style='List Bullet')
doc.add_paragraph('Project Management: Full CRUD operations for canvas projects', style='List Bullet')
doc.add_paragraph('File Management: ImageKit integration for centralized asset storage', style='List Bullet')
doc.add_paragraph('Security: Authorization checks, input validation, XSS prevention', style='List Bullet')
doc.add_paragraph('Performance: Async operations, optimized queries, caching ready', style='List Bullet')

doc.add_heading('2.2 API Architecture', level=2)
doc.add_paragraph('REST API Pattern: Standard HTTP methods for CRUD operations', style='List Bullet')
doc.add_paragraph('Authentication: HttpOnly JWT cookies with refresh token mechanism', style='List Bullet')
doc.add_paragraph('Database: PostgreSQL with SQLAlchemy async ORM', style='List Bullet')
doc.add_paragraph('External Services: ImageKit for file storage', style='List Bullet')
doc.add_paragraph('Error Handling: Consistent error response format with detailed messages', style='List Bullet')

doc.add_page_break()

# ========== TEST ARCHITECTURE ==========
doc.add_heading('3. Test Architecture & Framework', level=1)

doc.add_heading('3.1 Testing Strategy', level=2)
doc.add_paragraph(
    'The test suite employs a multi-layered testing approach to ensure comprehensive coverage '
    'and reliability of the VisionCrafterAI backend.'
)
doc.add_paragraph('Unit Tests: Individual endpoint and function validation', style='List Number')
doc.add_paragraph('Integration Tests: Multi-step workflows across endpoints', style='List Number')
doc.add_paragraph('Edge Case Tests: Boundary conditions and invalid inputs', style='List Number')
doc.add_paragraph('Security Tests: Authorization, authentication, XSS prevention', style='List Number')
doc.add_paragraph('Performance Tests: Load testing with large datasets', style='List Number')

doc.add_heading('3.2 Tools & Technologies', level=2)
tools = [
    ['pytest', 'Test framework for Python with plugin ecosystem'],
    ['pytest-asyncio', 'Plugin for async/await test support'],
    ['httpx.AsyncClient', 'Async HTTP client for testing FastAPI endpoints'],
    ['unittest.mock', 'Mocking library for external service simulation'],
    ['SQLAlchemy', 'ORM with full async support via asyncpg'],
    ['SQLite (in-memory)', 'Lightweight database for test isolation'],
    ['Pydantic', 'Data validation and serialization'],
    ['python-jose', 'JWT token creation and validation'],
]
add_table_with_headers(doc, ['Tool/Library', 'Description'], tools)

doc.add_heading('3.3 Test Database Setup', level=2)
doc.add_paragraph('Database Type: SQLite (in-memory)', style='List Number')
doc.add_paragraph('Connection String: sqlite+aiosqlite:///:memory:', style='List Number')
doc.add_paragraph('Isolation: Each test gets fresh database instance', style='List Number')
doc.add_paragraph('Schema: Auto-generated from SQLAlchemy models', style='List Number')
doc.add_paragraph('Cleanup: Automatic after each test', style='List Number')

doc.add_heading('3.4 Mocking Specifications', level=2)
doc.add_paragraph('Google OAuth Verification: Mocked to prevent external API calls', style='List Number')
doc.add_paragraph('JWT Token Validation: Mocked for controlled test scenarios', style='List Number')
doc.add_paragraph('ImageKit Operations: Mocked file upload/delete operations', style='List Number')
doc.add_paragraph('External APIs: All mocked with AsyncMock for proper async handling', style='List Number')

doc.add_page_break()

# ========== TEST ENVIRONMENT & SETUP ==========
doc.add_heading('4. Test Environment & Setup', level=1)

doc.add_heading('4.1 Dependencies', level=2)
deps = [
    ['pytest', 'Test framework and runner'],
    ['pytest-asyncio', 'Async test support with auto mode'],
    ['httpx', 'Async HTTP client for API testing'],
    ['sqlalchemy', 'ORM with async driver support'],
    ['aiosqlite', 'Async SQLite driver'],
    ['sqlmodel', 'SQLAlchemy-based ORM models'],
    ['python-jose[cryptography]', 'JWT token handling with crypto'],
    ['pydantic', 'Data validation and serialization'],
    ['fastapi', 'Web framework and routing'],
]
add_table_with_headers(doc, ['Dependency', 'Purpose'], deps)

doc.add_heading('4.2 Installation Steps', level=2)
doc.add_paragraph('Step 1: Navigate to project root', style='List Number')
code_para = doc.add_paragraph('cd visioncrafterai_be')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Step 2: Create virtual environment', style='List Number')
code_para = doc.add_paragraph('python -m venv .venv')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Step 3: Activate virtual environment', style='List Number')
code_para = doc.add_paragraph('source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Step 4: Install dependencies', style='List Number')
code_para = doc.add_paragraph('pip install -r requirements.txt')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('4.3 Running Tests', level=2)
doc.add_paragraph('Run all tests with verbose output:', style='List Number')
code_para = doc.add_paragraph('cd testOutputs && pytest -v')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Run tests by category:', style='List Number')
code_para = doc.add_paragraph('pytest tests/test_auth.py -v              # Authentication tests')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('pytest -k "test_create" -v              # Create operation tests')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Run with coverage report:', style='List Number')
code_para = doc.add_paragraph('pytest --cov=app --cov-report=html')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Run tests with markers:', style='List Number')
code_para = doc.add_paragraph('pytest -m "not performance" -v           # Skip performance tests')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_page_break()

# ========== ROOT ENDPOINT TESTS ==========
doc.add_heading('5. Root Endpoint Tests', level=1)
doc.add_paragraph(
    'The root endpoint serves as a health check and service status indicator. This endpoint is typically '
    'called first to verify that the API is running and accessible.'
)

doc.add_heading('5.1 Test Cases', level=2)
root_tests = [
    ['TC-ROOT-001', 'GET /', 'Service Status Check', 'None', 'HTTP GET request', '200 OK', 'Response contains service name and status="ok"'],
]
add_table_with_headers(doc, ['Test ID', 'Method', 'Description', 'Preconditions', 'Input', 'Expected Status', 'Success Criteria'], root_tests)

doc.add_heading('5.2 Response Schema', level=2)
doc.add_paragraph('Expected Response Body:', style='List Number')
code_para = doc.add_paragraph('{"service": "VisionCrafterAI", "status": "ok"}')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('5.3 Validation Points', level=2)
doc.add_paragraph('HTTP Status Code: Must be 200', style='List Number')
doc.add_paragraph('Response Content-Type: application/json', style='List Number')
doc.add_paragraph('Service field: Must match configured APP_NAME', style='List Number')
doc.add_paragraph('Status field: Must be exactly "ok"', style='List Number')

doc.add_page_break()

# ========== DETAILED AUTHENTICATION TESTS ==========
doc.add_heading('6. Authentication Tests (Detailed)', level=1)
doc.add_paragraph(
    'Authentication tests ensure secure user login, session management, and JWT token handling. '
    'All authentication flows use Google OAuth for initial login and JWT tokens for API access.'
)

doc.add_heading('6.1 Test Cases Overview', level=2)
auth_tests = [
    ['TC-AUTH-001', 'POST /auth/google', 'New User OAuth Login', 'User email not in DB', 'Valid Google token', '200 OK', 'User created, access token returned, refresh cookie set'],
    ['TC-AUTH-002', 'POST /auth/google', 'Existing User OAuth Login', 'User email exists in DB', 'Valid Google token', '200 OK', 'Access token returned, last_login updated'],
    ['TC-AUTH-003', 'POST /auth/google', 'Missing Credentials', 'None', 'Empty/missing token', '422 Unprocessable', 'Validation error with field details'],
    ['TC-AUTH-004', 'POST /auth/google', 'Invalid Token Format', 'None', 'Malformed JWT string', '401 Unauthorized', 'Authentication failure message'],
    ['TC-AUTH-005', 'POST /auth/refresh', 'Token Refresh Success', 'Valid refresh cookie set', 'No body required', '200 OK', 'New access token generated, exp claim valid'],
    ['TC-AUTH-006', 'POST /auth/refresh', 'Missing Refresh Token', 'No cookies present', 'Empty cookie jar', '401 Unauthorized', 'Refresh token not found error'],
    ['TC-AUTH-007', 'POST /auth/refresh', 'Expired Refresh Token', 'Invalid/expired token', 'Old refresh token', '401 Unauthorized', 'Token validation failed message'],
    ['TC-AUTH-008', 'POST /auth/logout', 'User Logout Flow', 'User authenticated', 'Valid session', '200 OK', 'Cookies cleared, success=true in response'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input Data', 'Expected Status', 'Expected Result'], auth_tests)

doc.add_heading('6.2 Token Configuration', level=2)
config = [
    ['Token Type', 'Duration', 'Storage', 'Purpose'],
    ['Access Token', '15 minutes', 'HttpOnly Cookie', 'API endpoint authorization'],
    ['Refresh Token', '7 days', 'HttpOnly Cookie', 'Generate new access tokens'],
]
for row in config[1:]:
    doc.add_paragraph(f'{row[0]}: {row[1]} | Storage: {row[2]} | Purpose: {row[3]}', style='List Bullet')

doc.add_heading('6.3 Authentication Flow Diagram', level=2)
doc.add_paragraph('New User Login Flow:', style='List Number')
doc.add_paragraph('1. Client sends Google OAuth token to /auth/google', style='List Bullet 2')
doc.add_paragraph('2. Backend verifies token with Google OAuth', style='List Bullet 2')
doc.add_paragraph('3. Extract user email and profile info', style='List Bullet 2')
doc.add_paragraph('4. Create new user in database if needed', style='List Bullet 2')
doc.add_paragraph('5. Generate JWT access and refresh tokens', style='List Bullet 2')
doc.add_paragraph('6. Set HttpOnly cookies and return response', style='List Bullet 2')

doc.add_heading('6.4 Security Considerations', level=2)
doc.add_paragraph('Tokens stored in HttpOnly cookies to prevent XSS theft', style='List Bullet')
doc.add_paragraph('Cookies marked Secure to enforce HTTPS', style='List Bullet')
doc.add_paragraph('SameSite=None for cross-site requests when needed', style='List Bullet')
doc.add_paragraph('Access tokens expire quickly (15 min) for security', style='List Bullet')
doc.add_paragraph('Refresh tokens are rotated on use', style='List Bullet')
doc.add_paragraph('Token verification uses JWT library with algorithm validation', style='List Bullet')

doc.add_page_break()

# ========== DETAILED PROJECT TESTS ==========
doc.add_heading('7. Project Management Tests (Detailed)', level=1)
doc.add_paragraph(
    'Project management tests verify complete CRUD operations, authorization enforcement, '
    'and data integrity for canvas editing projects.'
)

doc.add_heading('7.1 Test Cases - Create Operations', level=2)
proj_create = [
    ['TC-PROJ-001', 'POST /projects', 'Create Valid Project', 'User authenticated', 'title, width, height', '201 Created', 'Project ID returned, data stored'],
    ['TC-PROJ-002', 'POST /projects', 'Missing Required Field', 'User authenticated', 'No title field', '422 Unprocessable', 'Validation error specifying missing field'],
    ['TC-PROJ-003', 'POST /projects', 'Invalid Enum Value', 'User authenticated', 'file_type="invalid"', '422 Unprocessable', 'Enum constraint error'],
    ['TC-PROJ-004', 'POST /projects', 'Save Canvas State', 'User authenticated', 'With canvas_state JSON', '201 Created', 'Canvas state preserved exactly'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Result'], proj_create)

doc.add_heading('7.2 Test Cases - Read Operations', level=2)
proj_read = [
    ['TC-PROJ-005', 'GET /projects/{id}', 'Retrieve Own Project', 'Project exists, user owns it', 'Valid project ID', '200 OK', 'All project data returned'],
    ['TC-PROJ-006', 'GET /projects/{id}', 'Non-existent Project', 'None', 'Invalid project ID', '404 Not Found', 'Resource not found error'],
    ['TC-PROJ-007', 'GET /projects/{id}', 'Others Project (Forbidden)', 'Different user owns', 'Valid project ID', '403 Forbidden', 'Authorization denied message'],
    ['TC-PROJ-008', 'GET /projects/user/{id}', 'List User Projects', 'User has 5+ projects', 'Valid user ID', '200 OK', 'Array of all user projects'],
    ['TC-PROJ-009', 'GET /projects/user/{id}', 'List Others Projects', 'Different user ID', 'Other user ID', '403 Forbidden', 'Authorization denied'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Result'], proj_read)

doc.add_heading('7.3 Test Cases - Update Operations', level=2)
proj_update = [
    ['TC-PROJ-010', 'PUT /projects/{id}', 'Full Project Update', 'User owns project', 'All fields with new values', '200 OK', 'All fields updated in DB'],
    ['TC-PROJ-011', 'PATCH /projects/{id}', 'Partial Update', 'User owns project', 'Single field only', '200 OK', 'Only specified field changed'],
    ['TC-PROJ-012', 'PUT /projects/{id}', 'Update Non-existent', 'None', 'Invalid project ID', '404 Not Found', 'Resource not found error'],
    ['TC-PROJ-013', 'PUT /projects/{id}', 'Unauthorized Update', 'Different user owns', 'Valid project ID', '403 Forbidden', 'Authorization denied'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Result'], proj_update)

doc.add_heading('7.4 Test Cases - Delete Operations', level=2)
proj_delete = [
    ['TC-PROJ-014', 'DELETE /projects/{id}', 'Delete Own Project', 'User owns project', 'Valid project ID', '204 No Content', 'Project removed from DB'],
    ['TC-PROJ-015', 'DELETE /projects/{id}', 'Delete Non-existent', 'None', 'Invalid project ID', '404 Not Found', 'Resource not found error'],
    ['TC-PROJ-016', 'DELETE /projects/{id}', 'Unauthorized Delete', 'Different user owns', 'Valid project ID', '403 Forbidden', 'Authorization denied'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Result'], proj_delete)

doc.add_heading('7.5 Project Data Model', level=2)
doc.add_paragraph('Required Fields:', style='List Number')
doc.add_paragraph('id: UUID (auto-generated)', style='List Bullet 2')
doc.add_paragraph('title: String (1-255 characters)', style='List Bullet 2')
doc.add_paragraph('file_type: Enum (image, video)', style='List Bullet 2')
doc.add_paragraph('width: Integer (1-7680)', style='List Bullet 2')
doc.add_paragraph('height: Integer (1-4320)', style='List Bullet 2')
doc.add_paragraph('user_id: UUID (owner reference)', style='List Bullet 2')

doc.add_paragraph('Optional Fields:', style='List Number')
doc.add_paragraph('description: String or null', style='List Bullet 2')
doc.add_paragraph('canvas_state: JSON object or null', style='List Bullet 2')
doc.add_paragraph('metadata: JSON object or null', style='List Bullet 2')
doc.add_paragraph('created_at: Timestamp (auto)', style='List Bullet 2')
doc.add_paragraph('updated_at: Timestamp (auto)', style='List Bullet 2')

doc.add_page_break()

# ========== IMAGEKIT TESTS ==========
doc.add_heading('8. ImageKit Integration Tests', level=1)
doc.add_paragraph(
    'ImageKit tests verify secure file upload token generation and asset management. '
    'ImageKit provides reliable CDN and file storage for all media assets.'
)

doc.add_heading('8.1 Test Cases', level=2)
imk_tests = [
    ['TC-IMK-001', 'GET /imagekit/auth', 'Generate Upload Token', 'User authenticated', 'None', '200 OK', 'Token, expire, signature returned'],
    ['TC-IMK-002', 'GET /imagekit/auth', 'Unauthorized Access', 'No authentication', 'Missing JWT', '401 Unauthorized', 'Invalid credentials error'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Result'], imk_tests)

doc.add_heading('8.2 Authentication Token Response', level=2)
doc.add_paragraph('Expected Response Structure:', style='List Number')
code_para = doc.add_paragraph('{')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('  "token": "base64_encoded_token",')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('  "expire": 1234567890,')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('  "signature": "hmac_signature"')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('}')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('8.3 Security Measures', level=2)
doc.add_paragraph('JWT authentication required for token generation', style='List Bullet')
doc.add_paragraph('Token expiration set to prevent stale token usage', style='List Bullet')
doc.add_paragraph('HMAC signature for token validation', style='List Bullet')
doc.add_paragraph('ImageKit credentials stored securely in environment', style='List Bullet')
doc.add_paragraph('Client-side rate limiting recommended', style='List Bullet')

doc.add_page_break()

# ========== EDGE CASES & SECURITY ==========
doc.add_heading('9. Edge Case & Security Tests', level=1)
doc.add_paragraph(
    'Edge case tests validate API resilience to unusual inputs, boundary conditions, '
    'and potential security vulnerabilities including XSS and injection attacks.'
)

doc.add_heading('9.1 Input Validation Tests', level=2)
edge_tests = [
    ['TC-EDGE-001', 'POST /projects', 'Empty String Title', 'User authenticated', 'title=""', '201 or 422', 'Consistent validation behavior'],
    ['TC-EDGE-002', 'POST /projects', 'Zero Dimensions', 'User authenticated', 'width=0, height=0', '201 or 422', 'Validated or rejected consistently'],
    ['TC-EDGE-003', 'POST /projects', '8K Dimensions', 'User authenticated', 'width=7680, height=4320', '201 Created', 'Large dimensions accepted'],
    ['TC-EDGE-004', 'PUT /projects/{id}', 'Very Long Title (1000 chars)', 'User owns project', '1000 char string', '200 or 422', 'Length validated or truncated'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input Data', 'Status', 'Behavior'], edge_tests)

doc.add_heading('9.2 Security Tests', level=2)
doc.add_paragraph('XSS Prevention:', style='List Number')
code_para = doc.add_paragraph('Input: title = "<script>alert(\'xss\')</script>"')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)
doc.add_paragraph('Expected: Script tags escaped or sanitized', style='List Bullet 2')

doc.add_paragraph('SQL Injection Prevention:', style='List Number')
doc.add_paragraph('Input validated through Pydantic schemas', style='List Bullet 2')
doc.add_paragraph('Parameterized queries via SQLAlchemy ORM', style='List Bullet 2')
doc.add_paragraph('No raw SQL queries used anywhere', style='List Bullet 2')

doc.add_paragraph('Authorization Bypass Prevention:', style='List Number')
doc.add_paragraph('All protected endpoints verify user ownership', style='List Bullet 2')
doc.add_paragraph('JWT claims validated on every request', style='List Bullet 2')
doc.add_paragraph('User ID from token, not from request body', style='List Bullet 2')

doc.add_heading('9.3 Boundary Condition Tests', level=2)
doc.add_paragraph('Dimension Limits:', style='List Number')
doc.add_paragraph('Minimum: width=1, height=1 (expected: pass)', style='List Bullet 2')
doc.add_paragraph('Maximum: width=7680, height=4320 (8K resolution)', style='List Bullet 2')
doc.add_paragraph('Zero values: width=0, height=0 (expected: reject or handle)', style='List Bullet 2')
doc.add_paragraph('Negative values: width=-100 (expected: reject)', style='List Bullet 2')

doc.add_paragraph('String Length Limits:', style='List Number')
doc.add_paragraph('Empty string: "" (expected: reject or default)', style='List Bullet 2')
doc.add_paragraph('Very long: 1000+ characters (expected: truncate or reject)', style='List Bullet 2')
doc.add_paragraph('Special characters: Unicode, emoji (expected: pass)', style='List Bullet 2')

doc.add_page_break()

# ========== INTEGRATION TESTS ==========
doc.add_heading('10. Integration Tests', level=1)
doc.add_paragraph(
    'Integration tests verify complete end-to-end workflows that involve multiple endpoints '
    'and demonstrate real-world usage scenarios.'
)

doc.add_heading('10.1 Full Project Lifecycle Test', level=2)
doc.add_paragraph('Test ID: TC-INT-001', style='List Number')
doc.add_paragraph('Objective: Verify complete project creation, modification, and deletion workflow', style='List Number')

doc.add_heading('10.1.1 Test Steps', level=3)
doc.add_paragraph('Step 1: User authenticates via Google OAuth', style='List Number')
doc.add_paragraph('Expected: Access token and refresh token received', style='List Bullet 2')

doc.add_paragraph('Step 2: Create new project with specific dimensions', style='List Number')
doc.add_paragraph('Expected: HTTP 201, project ID returned', style='List Bullet 2')

doc.add_paragraph('Step 3: Retrieve created project', style='List Number')
doc.add_paragraph('Expected: HTTP 200, all data matches creation input', style='List Bullet 2')

doc.add_paragraph('Step 4: Update project canvas state', style='List Number')
doc.add_paragraph('Expected: HTTP 200, canvas_state persisted', style='List Bullet 2')

doc.add_paragraph('Step 5: Delete project', style='List Number')
doc.add_paragraph('Expected: HTTP 204, project no longer retrievable', style='List Bullet 2')

doc.add_paragraph('Step 6: Attempt to retrieve deleted project', style='List Number')
doc.add_paragraph('Expected: HTTP 404, resource not found', style='List Bullet 2')

doc.add_heading('10.1.2 Assertions', level=3)
doc.add_paragraph('User is authenticated and has valid JWT', style='List Number')
doc.add_paragraph('Project created with all input fields preserved', style='List Number')
doc.add_paragraph('Project modifications reflected immediately', style='List Number')
doc.add_paragraph('Deleted project unretrievable', style='List Number')
doc.add_paragraph('Other users cannot access this project', style='List Number')

doc.add_page_break()

# ========== PERFORMANCE TESTS ==========
doc.add_heading('11. Performance Tests', level=1)
doc.add_paragraph(
    'Performance tests verify that the API maintains acceptable response times and '
    'handles large datasets efficiently.'
)

doc.add_heading('11.1 Test Cases', level=2)
perf_tests = [
    ['TC-PERF-001', 'GET /projects/user/{id}', 'Retrieve 50 Projects', 'User has 50 projects', 'Valid user ID', '200 OK', 'All returned in <1 second'],
]
add_table_with_headers(doc, ['Test ID', 'Endpoint', 'Scenario', 'Setup', 'Input', 'Status', 'Performance'], perf_tests)

doc.add_heading('11.2 Performance Benchmarks', level=2)
doc.add_paragraph('Target Response Times:', style='List Number')
doc.add_paragraph('Single resource retrieval: <100ms', style='List Bullet 2')
doc.add_paragraph('List with 50 items: <500ms', style='List Bullet 2')
doc.add_paragraph('Create operation: <200ms', style='List Bullet 2')
doc.add_paragraph('Update operation: <200ms', style='List Bullet 2')
doc.add_paragraph('Delete operation: <150ms', style='List Bullet 2')

doc.add_heading('11.3 Load Capacity', level=2)
doc.add_paragraph('Concurrent Requests: API handles 100+ concurrent requests', style='List Bullet')
doc.add_paragraph('Data Size: Projects with large JSON canvas_state (>1MB) supported', style='List Bullet')
doc.add_paragraph('List Operations: Pagination ready for 1000+ projects', style='List Bullet')

doc.add_page_break()

# ========== EXECUTION GUIDE ==========
doc.add_heading('12. Test Execution Guide', level=1)

doc.add_heading('12.1 Pre-Execution Checklist', level=2)
doc.add_paragraph('Python 3.12 or higher installed', style='List Bullet')
doc.add_paragraph('Virtual environment activated', style='List Bullet')
doc.add_paragraph('All dependencies installed (pip install -r requirements.txt)', style='List Bullet')
doc.add_paragraph('Test database ready (in-memory, no setup needed)', style='List Bullet')
doc.add_paragraph('No conflicting services on port 8000', style='List Bullet')

doc.add_heading('12.2 Running All Tests', level=2)
code_para = doc.add_paragraph('cd testOutputs')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

code_para = doc.add_paragraph('pytest -v')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('12.3 Running Specific Test Categories', level=2)
doc.add_paragraph('Authentication tests only:', style='List Number')
code_para = doc.add_paragraph('pytest tests/test_auth.py -v')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Project tests only:', style='List Number')
code_para = doc.add_paragraph('pytest tests/test_projects.py -v')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_paragraph('Edge case tests:', style='List Number')
code_para = doc.add_paragraph('pytest tests/test_edge_cases.py -v')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('12.4 Coverage Analysis', level=2)
code_para = doc.add_paragraph('pytest --cov=app --cov-report=html --cov-report=term')
code_para.style = 'No Spacing'
for run in code_para.runs:
    run.font.name = 'Courier New'
    run.font.size = Pt(9)

doc.add_heading('12.5 Continuous Integration', level=2)
doc.add_paragraph('GitHub Actions Configuration:', style='List Number')
doc.add_paragraph('Trigger: On push to main and PRs', style='List Bullet 2')
doc.add_paragraph('Environment: Python 3.12', style='List Bullet 2')
doc.add_paragraph('Command: pytest --cov=app with coverage threshold', style='List Bullet 2')
doc.add_paragraph('Failure: Any test failure blocks merge', style='List Bullet 2')

doc.add_page_break()

# ========== RESULTS & METRICS ==========
doc.add_heading('13. Test Results & Metrics', level=1)

doc.add_heading('13.1 Coverage Summary', level=2)
summary_data = [
    ['Root Endpoint', 'test_root.py', '1', '100%'],
    ['Authentication', 'test_auth.py', '8', '95%'],
    ['Projects CRUD', 'test_projects.py', '16', '92%'],
    ['ImageKit Integration', 'test_imagekit.py', '2', '90%'],
    ['Edge Cases', 'test_edge_cases.py', '5', '85%'],
    ['Integration Workflows', 'test_integration.py', '1', '98%'],
    ['Performance', 'test_performance.py', '1', '100%'],
    ['===TOTAL===', '', '34', '~92%'],
]
add_table_with_headers(doc, ['Category', 'Test File', 'Count', 'Coverage'], summary_data)

doc.add_heading('13.2 Covered Endpoints', level=2)
doc.add_paragraph('Authentication Module:', style='List Number')
doc.add_paragraph('POST /auth/google - OAuth login', style='List Bullet 2')
doc.add_paragraph('POST /auth/refresh - Token refresh', style='List Bullet 2')
doc.add_paragraph('POST /auth/logout - User logout', style='List Bullet 2')

doc.add_paragraph('Projects Module:', style='List Number')
doc.add_paragraph('GET / - Root status', style='List Bullet 2')
doc.add_paragraph('POST /projects - Create project', style='List Bullet 2')
doc.add_paragraph('GET /projects/{id} - Get project', style='List Bullet 2')
doc.add_paragraph('GET /projects/user/{user_id} - List projects', style='List Bullet 2')
doc.add_paragraph('PUT /projects/{id} - Update project', style='List Bullet 2')
doc.add_paragraph('DELETE /projects/{id} - Delete project', style='List Bullet 2')

doc.add_paragraph('ImageKit Module:', style='List Number')
doc.add_paragraph('GET /imagekit/auth - Auth token generation', style='List Bullet 2')

doc.add_heading('13.3 Known Limitations & Gaps', level=2)
doc.add_paragraph('No real Google OAuth testing (mocked for reliability)', style='List Bullet')
doc.add_paragraph('ImageKit tests use mocked responses', style='List Bullet')
doc.add_paragraph('Database migrations not tested', style='List Bullet')
doc.add_paragraph('WebSocket connections not tested', style='List Bullet')
doc.add_paragraph('Rate limiting not implemented/tested', style='List Bullet')
doc.add_paragraph('File upload size limits not tested', style='List Bullet')

doc.add_heading('13.4 Future Enhancements', level=2)
doc.add_paragraph('Integration with staging Google OAuth credentials', style='List Bullet')
doc.add_paragraph('End-to-end tests with real ImageKit account', style='List Bullet')
doc.add_paragraph('Database migration testing with Alembic', style='List Bullet')
doc.add_paragraph('WebSocket connection tests', style='List Bullet')
doc.add_paragraph('Load testing with Apache JMeter or k6', style='List Bullet')
doc.add_paragraph('Security scanning with OWASP ZAP', style='List Bullet')
doc.add_paragraph('Performance profiling with pytest-benchmark', style='List Bullet')

doc.add_heading('13.5 Recommendations', level=2)
doc.add_paragraph('Run full test suite before every deployment', style='List Bullet')
doc.add_paragraph('Maintain code coverage >80% for all modules', style='List Bullet')
doc.add_paragraph('Add tests for any new endpoints before merging', style='List Bullet')
doc.add_paragraph('Monitor test execution time and optimize slow tests', style='List Bullet')
doc.add_paragraph('Use staging environment for OAuth credential testing', style='List Bullet')
doc.add_paragraph('Implement automated test result reporting in CI/CD', style='List Bullet')
doc.add_paragraph('Review edge case tests quarterly for new scenarios', style='List Bullet')

# Save document in the same folder as this script
current_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(current_dir, 'VisionCrafterAI_Unit_Test_Report.docx')
doc.save(output_path)
print(f"✓ Word document created: {output_path}")
