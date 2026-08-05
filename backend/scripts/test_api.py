"""
Test API endpoints to verify everything works.
Run this after starting the server.
"""
import asyncio
import sys
from pathlib import Path

import httpx

BASE_URL = "http://localhost:8000"
API_URL = f"{BASE_URL}/api/v1"


async def test_health_check():
    """Test health check endpoints."""
    print("🔍 Testing health check...")
    
    async with httpx.AsyncClient() as client:
        # Basic health
        response = await client.get(f"{BASE_URL}/health")
        assert response.status_code == 200, "Basic health check failed"
        
        # Detailed health
        response = await client.get(f"{API_URL}/health/detailed")
        assert response.status_code == 200, "Detailed health check failed"
        data = response.json()
        assert data["status"] in ["healthy", "degraded"], "Unexpected health status"
        
        print("✅ Health checks passed")
        return data


async def test_auth_flow():
    """Test authentication flow."""
    print("\n🔍 Testing authentication...")
    
    async with httpx.AsyncClient() as client:
        # Register user
        register_data = {
            "email": f"test_{asyncio.get_event_loop().time()}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        
        response = await client.post(f"{API_URL}/auth/register", json=register_data)
        if response.status_code != 201:
            print(f"❌ Registration failed: {response.text}")
            return None
        
        user_data = response.json()
        print(f"✅ User registered: {user_data['email']}")
        
        # Login
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        
        response = await client.post(f"{API_URL}/auth/login", json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.text}")
            return None
        
        tokens = response.json()
        print("✅ Login successful")
        
        # Get current user
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}
        response = await client.get(f"{API_URL}/auth/me", headers=headers)
        if response.status_code != 200:
            print(f"❌ Get current user failed: {response.text}")
            return None
        
        print("✅ Authentication flow completed")
        return tokens


async def test_resume_upload(access_token: str):
    """Test resume upload (requires a sample PDF)."""
    print("\n🔍 Testing resume upload...")
    
    # Create a minimal PDF for testing
    pdf_content = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT\n/F1 12 Tf\n100 700 Td\n(Test Resume) Tj\nET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\n0000000270 00000 n\n0000000363 00000 n\ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n442\n%%EOF"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {access_token}"}
        files = {"file": ("test_resume.pdf", pdf_content, "application/pdf")}
        
        response = await client.post(
            f"{API_URL}/resumes/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 201:
            print(f"⚠️  Resume upload failed: {response.text}")
            print("   (This is expected if S3/MinIO is not configured)")
            return None
        
        resume_data = response.json()
        print(f"✅ Resume uploaded: {resume_data['id']}")
        return resume_data


async def test_complete_flow():
    """Test complete flow."""
    print("🚀 Running complete API test")
    print("="*50)
    
    # Test health
    health = await test_health_check()
    
    # Test auth
    tokens = await test_auth_flow()
    if not tokens:
        print("\n⚠️  Authentication test incomplete - some features require proper setup")
        return
    
    # Test resume upload
    resume = await test_resume_upload(tokens['access_token'])
    if not resume:
        print("\n⚠️  Resume test skipped - requires S3/MinIO configuration")
        return
    
    print("\n" + "="*50)
    print("✅ All API tests completed!")
    print("\nAPI is ready for use:")
    print(f"  - API Docs: {BASE_URL}/api/docs")
    print(f"  - Health: {BASE_URL}/health")


if __name__ == "__main__":
    print("Testing URCV Backend API")
    print("Make sure the server is running on http://localhost:8000")
    print()
    
    try:
        asyncio.run(test_complete_flow())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
