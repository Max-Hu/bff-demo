import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from app.main import app
from app.models import TriggerRequest, StatusResponse, LogResponse

client = TestClient(app)


class TestScanAPI:
    """Test cases for scan API endpoints"""
    
    def setup_method(self):
        """Setup test method"""
        self.api_key = "test-api-key"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    @patch('app.jenkins_client.jenkins_client.trigger_job')
    def test_trigger_scan_success(self, mock_trigger_job):
        """Test successful scan trigger"""
        # Mock Jenkins response
        mock_trigger_job.return_value = {
            "status": "triggered",
            "job_name": "test-scan",
            "build_number": 123,
            "jenkins_url": "http://jenkins/job/test-scan/123"
        }
        
        request_data = {
            "job_name": "test-scan",
            "parameters": {
                "nexusURL": "https://nexus.company.com/artifact/projectX/1.0.0"
            }
        }
        
        response = client.post(
            "/api/scan/trigger",
            json=request_data,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "triggered"
        assert data["job_name"] == "test-scan"
        assert data["build_number"] == 123
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    def test_trigger_scan_unauthorized(self):
        """Test scan trigger without API key"""
        request_data = {
            "job_name": "test-scan",
            "parameters": {"test": "value"}
        }
        
        response = client.post("/api/scan/trigger", json=request_data)
        
        assert response.status_code == 401
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    @patch('app.jenkins_client.jenkins_client.get_build_status')
    def test_get_scan_status_success(self, mock_get_status):
        """Test successful status retrieval"""
        # Mock Jenkins response
        mock_get_status.return_value = {
            "status": "IN_PROGRESS",
            "progress_percent": 50.0,
            "start_time": "2023-01-01T10:00:00",
            "estimated_end_time": None
        }
        
        response = client.get(
            "/api/scan/status?job_name=test-scan&build_number=123",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["progress_percent"] == 50.0
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    @patch('app.jenkins_client.jenkins_client.get_build_logs')
    def test_get_scan_logs_success(self, mock_get_logs):
        """Test successful log retrieval"""
        # Mock Jenkins response
        mock_get_logs.return_value = "Build started\nStep 1 completed\nStep 2 completed"
        
        response = client.get(
            "/api/scan/log?job_name=test-scan&build_number=123",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["lines"]) == 3
        assert "Build started" in data["lines"]
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    @patch('app.database.db_manager.store_scan_result')
    @patch('app.jenkins_client.jenkins_client.get_build_logs')
    def test_callback_success(self, mock_get_logs, mock_store_result):
        """Test successful callback processing"""
        # Mock database response
        mock_store_result.return_value = True
        mock_get_logs.return_value = "Build logs content"
        
        callback_data = {
            "job_name": "test-scan",
            "build_number": 123,
            "status": "SUCCESS",
            "results": {
                "report_url": "http://jenkins/job/test-scan/123/report.html",
                "risk_score": "medium"
            },
            "timestamp": "2023-01-01T12:00:00"
        }
        
        response = client.post(
            "/api/scan/callback",
            json=callback_data,
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "received"
    
    @patch('app.auth.settings.api_key', 'test-api-key')
    @patch('app.database.db_manager.get_scan_result')
    def test_get_scan_result_success(self, mock_get_result):
        """Test successful result retrieval"""
        # Mock database response
        mock_get_result.return_value = {
            "job_name": "test-scan",
            "build_number": 123,
            "status": "SUCCESS",
            "results": {
                "report_url": "http://jenkins/job/test-scan/123/report.html",
                "risk_score": "medium"
            },
            "timestamp": "2023-01-01T12:00:00"
        }
        
        response = client.get(
            "/api/scan/result?job_name=test-scan&build_number=123",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_name"] == "test-scan"
        assert data["build_number"] == 123
        assert data["status"] == "SUCCESS"


if __name__ == "__main__":
    pytest.main([__file__]) 