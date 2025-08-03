from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
import logging

from ..models import (
    TriggerRequest, TriggerResponse,
    StatusResponse, LogResponse,
    CallbackRequest, CallbackResponse,
    ResultResponse, ErrorResponse
)
from ..auth import get_current_user
from ..jenkins_client import jenkins_client
from ..database import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])


@router.post("/trigger", response_model=TriggerResponse)
async def trigger_scan(
    request: TriggerRequest,
    current_user: dict = Depends(get_current_user)
):
    """Trigger a Jenkins scan job"""
    try:
        logger.info(f"Triggering scan job: {request.job_name}")
        
        # Trigger the Jenkins job
        result = jenkins_client.trigger_job(request.job_name, request.parameters)
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to trigger Jenkins job")
        
        return TriggerResponse(**result)
        
    except Exception as e:
        logger.error(f"Error triggering scan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=StatusResponse)
async def get_scan_status(
    job_name: str = Query(..., description="Jenkins job name"),
    build_number: int = Query(..., description="Build number"),
    current_user: dict = Depends(get_current_user)
):
    """Get the status of a scan build"""
    try:
        logger.info(f"Getting status for {job_name}#{build_number}")
        
        # Get status from Jenkins
        status = jenkins_client.get_build_status(job_name, build_number)
        
        if not status:
            raise HTTPException(status_code=404, detail="Build not found")
        
        return StatusResponse(**status)
        
    except Exception as e:
        logger.error(f"Error getting scan status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/log", response_model=LogResponse)
async def get_scan_log(
    job_name: str = Query(..., description="Jenkins job name"),
    build_number: int = Query(..., description="Build number"),
    tail: Optional[int] = Query(None, description="Number of lines to return from end"),
    current_user: dict = Depends(get_current_user)
):
    """Get the logs for a scan build"""
    try:
        logger.info(f"Getting logs for {job_name}#{build_number}")
        
        # Get logs from Jenkins
        logs = jenkins_client.get_build_logs(job_name, build_number, tail)
        
        if logs is None:
            raise HTTPException(status_code=404, detail="Build logs not found")
        
        # Split logs into lines
        lines = logs.split('\n') if logs else []
        
        return LogResponse(lines=lines)
        
    except Exception as e:
        logger.error(f"Error getting scan logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/callback", response_model=CallbackResponse)
async def receive_callback(
    request: CallbackRequest,
    current_user: dict = Depends(get_current_user)
):
    """Receive callback from Jenkins after scan completion"""
    try:
        logger.info(f"Received callback for {request.job_name}#{request.build_number}")
        
        # Store the scan result in database
        success = db_manager.store_scan_result(
            request.job_name,
            request.build_number,
            request.status,
            request.results
        )
        
        if not success:
            logger.error("Failed to store scan result in database")
            raise HTTPException(status_code=500, detail="Failed to store scan result")
        
        # Store logs if available
        logs = jenkins_client.get_build_logs(request.job_name, request.build_number)
        if logs:
            db_manager.store_scan_log(request.job_name, request.build_number, logs)
        
        return CallbackResponse(status="received")
        
    except Exception as e:
        logger.error(f"Error processing callback: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/result", response_model=ResultResponse)
async def get_scan_result(
    job_name: str = Query(..., description="Jenkins job name"),
    build_number: int = Query(..., description="Build number"),
    current_user: dict = Depends(get_current_user)
):
    """Get the final stored scan result"""
    try:
        logger.info(f"Getting result for {job_name}#{build_number}")
        
        # Get result from database
        result = db_manager.get_scan_result(job_name, build_number)
        
        if not result:
            raise HTTPException(status_code=404, detail="Scan result not found")
        
        return ResultResponse(**result)
        
    except Exception as e:
        logger.error(f"Error getting scan result: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 