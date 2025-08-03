from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TriggerRequest(BaseModel):
    """Request model for triggering a Jenkins job"""
    job_name: str = Field(..., description="Name of the Jenkins job to trigger")
    parameters: Dict[str, str] = Field(..., description="Job parameters")


class TriggerResponse(BaseModel):
    """Response model for job trigger"""
    status: str = Field(..., description="Trigger status")
    job_name: str = Field(..., description="Job name")
    build_number: int = Field(..., description="Build number")
    jenkins_url: str = Field(..., description="Jenkins build URL")


class StatusResponse(BaseModel):
    """Response model for build status"""
    status: str = Field(..., description="Build status", enum=["IN_PROGRESS", "SUCCESS", "FAILURE", "ABORTED"])
    progress_percent: Optional[float] = Field(None, description="Progress percentage")
    start_time: Optional[datetime] = Field(None, description="Build start time")
    estimated_end_time: Optional[datetime] = Field(None, description="Estimated end time")


class LogResponse(BaseModel):
    """Response model for build logs"""
    lines: List[str] = Field(..., description="Log lines")


class CallbackRequest(BaseModel):
    """Request model for Jenkins callback"""
    job_name: str = Field(..., description="Job name")
    build_number: int = Field(..., description="Build number")
    status: str = Field(..., description="Build status", enum=["SUCCESS", "FAILURE"])
    results: Dict[str, str] = Field(..., description="Scan results")
    timestamp: Optional[datetime] = Field(None, description="Callback timestamp")


class CallbackResponse(BaseModel):
    """Response model for callback acknowledgment"""
    status: str = Field(..., description="Callback status")


class ResultResponse(BaseModel):
    """Response model for final scan result"""
    job_name: str = Field(..., description="Job name")
    build_number: int = Field(..., description="Build number")
    status: str = Field(..., description="Final status")
    results: Dict[str, str] = Field(..., description="Final results")
    timestamp: datetime = Field(..., description="Result timestamp")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details") 