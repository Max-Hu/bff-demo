import requests
import logging
from typing import Dict, Optional, Any
from datetime import datetime
from .config import settings

logger = logging.getLogger(__name__)
# Ensure this logger can show debug messages
logger.setLevel(logging.DEBUG)


class JenkinsClient:
    """Jenkins API client for triggering jobs and getting status"""
    
    def __init__(self):
        self.base_url = settings.jenkins_url.rstrip('/')
        self.auth = None
        logger.info(f"Using base URL: {self.base_url}")
        logger.debug(f"Using username: {settings.jenkins_username} and token: {settings.jenkins_token}")
        # Setup authentication if credentials provided
        if settings.jenkins_username and settings.jenkins_token:
            logger.debug(f"Using username: {settings.jenkins_username} and token: {settings.jenkins_token}")
            self.auth = (settings.jenkins_username, settings.jenkins_token)
        elif settings.jenkins_username and settings.jenkins_password:
            logger.debug(f"Using username: {settings.jenkins_username} and password: {settings.jenkins_password}")
            self.auth = (settings.jenkins_username, settings.jenkins_password)
    
    def trigger_job(self, job_name: str, parameters: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Trigger a Jenkins job with parameters"""
        try:
            # Build the trigger URL
            trigger_url = f"{self.base_url}/job/{job_name}/buildWithParameters"
            
            # Prepare request data
            data = parameters.copy()
            
            # Add token from config
            data['token'] = settings.jenkins_token
            logger.info(f"Using data: {data}")
            logger.debug(f"Using config token: {settings.jenkins_token[:8]}...")
            
            # Make the request
            response = requests.post(
                trigger_url,
                data=data,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 201:
                # Get the build number from the Location header
                location_header = response.headers.get('Location', '')
                build_number = self._extract_build_number(location_header)
                
                if build_number:
                    return {
                        "status": "triggered",
                        "job_name": job_name,
                        "build_number": build_number,
                        "jenkins_url": f"{self.base_url}/job/{job_name}/{build_number}"
                    }
                else:
                    logger.error("Could not extract build number from response")
                    return None
            else:
                logger.error(f"Failed to trigger job: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error triggering Jenkins job: {e}")
            return None
    
    def get_build_status(self, job_name: str, build_number: int) -> Optional[Dict[str, Any]]:
        """Get the status of a specific build"""
        try:
            # Get build info
            build_url = f"{self.base_url}/job/{job_name}/{build_number}/api/json"
            
            response = requests.get(
                build_url,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 200:
                build_info = response.json()
                
                # Map Jenkins status to our status
                status_mapping = {
                    "IN_PROGRESS": "IN_PROGRESS",
                    "SUCCESS": "SUCCESS",
                    "FAILURE": "FAILURE",
                    "ABORTED": "ABORTED",
                    "UNSTABLE": "FAILURE"
                }
                
                status = status_mapping.get(build_info.get('result'), "IN_PROGRESS")
                
                # Calculate progress (simplified)
                progress = 0
                if status == "SUCCESS":
                    progress = 100
                elif status == "FAILURE" or status == "ABORTED":
                    progress = 100
                else:
                    # Estimate progress based on timestamp
                    start_time = build_info.get('timestamp', 0)
                    if start_time:
                        elapsed = (datetime.now().timestamp() * 1000) - start_time
                        # Assume average build time of 10 minutes
                        progress = min(90, (elapsed / (10 * 60 * 1000)) * 100)
                
                return {
                    "status": status,
                    "progress_percent": progress,
                    "start_time": datetime.fromtimestamp(build_info.get('timestamp', 0) / 1000),
                    "estimated_end_time": None  # Could be calculated based on historical data
                }
            else:
                logger.error(f"Failed to get build status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting build status: {e}")
            return None
    
    def get_build_logs(self, job_name: str, build_number: int, tail: Optional[int] = None) -> Optional[str]:
        """Get build logs"""
        try:
            # Build the log URL
            log_url = f"{self.base_url}/job/{job_name}/{build_number}/consoleText"
            
            response = requests.get(
                log_url,
                auth=self.auth,
                timeout=30
            )
            
            if response.status_code == 200:
                logs = response.text
                
                # Return only last N lines if tail is specified
                if tail:
                    lines = logs.split('\n')
                    logs = '\n'.join(lines[-tail:])
                
                return logs
            else:
                logger.error(f"Failed to get build logs: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting build logs: {e}")
            return None
    
    def _extract_build_number(self, location_header: str) -> Optional[int]:
        """Extract build number from Location header"""
        try:
            # Location header format: http://jenkins/job/jobname/123/
            parts = location_header.rstrip('/').split('/')
            if len(parts) > 0:
                build_number_str = parts[-1]
                return int(build_number_str)
        except (ValueError, IndexError):
            pass
        return None
    
    def test_connection(self) -> bool:
        """Test Jenkins connection"""
        try:
            response = requests.get(
                f"{self.base_url}/api/json",
                auth=self.auth,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Jenkins connection test failed: {e}")
            return False


# Global Jenkins client instance
jenkins_client = JenkinsClient() 