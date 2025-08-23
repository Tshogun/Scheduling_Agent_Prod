import sys
import os
import asyncio
import json
import logging
import time
import uuid
from typing import Dict

import grpc
from fastapi import FastAPI
import pika

# Add the local proto folder to sys.path to import generated protobuf classes correctly
sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))

import service_pb2 # type: ignore
import service_pb2_grpc # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Python AI Service", version="1.0.0")

# In-memory job storage (use Redis in production)
job_storage: Dict[str, dict] = {}

class AIServiceImplementation(service_pb2_grpc.AIServiceServicer):
    def __init__(self):
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        self._setup_rabbitmq()

    def _setup_rabbitmq(self):
        """Setup RabbitMQ connection"""
        try:
            rabbitmq_url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")
            connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_url))
            channel = connection.channel()

            # Declare queues
            channel.queue_declare(queue='optimization_tasks', durable=True)
            channel.queue_declare(queue='optimization_results', durable=True)

            self.rabbitmq_connection = connection
            self.rabbitmq_channel = channel
            logger.info("RabbitMQ connection established")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def Ping(self, request, context):
        """Health check endpoint"""
        logger.info(f"Ping received: {request.message}")
        return service_pb2.PingResponse(
            message=f"Pong: {request.message}",
            timestamp=int(time.time())
        )

    def GetCompletion(self, request, context):
        """Mock LLM completion (replace with actual OpenAI call)"""
        logger.info(f"Completion request: {request.prompt[:50]}...")

        # Mock response (replace with actual LLM call)
        mock_completion = f"This is a mock response to: {request.prompt[:30]}..."

        return service_pb2.CompletionResponse(
            completion=mock_completion,
            tokens_used=len(mock_completion.split()),
            model=request.model or "mock-model"
        )

    def SolveOptimization(self, request, context):
        """Queue optimization task"""
        job_id = str(uuid.uuid4())

        # Store job info
        job_info = {
            "job_id": job_id,
            "status": "queued",
            "problem_type": request.problem_type,
            "constraints_json": request.constraints_json,
            "objectives_json": request.objectives_json,
            "timeout_seconds": request.timeout_seconds,
            "created_at": int(time.time()),
            "result_json": None,
            "error_message": None,
            "completed_at": None
        }
        job_storage[job_id] = job_info

        # Queue the task (if RabbitMQ is available)
        if self.rabbitmq_channel:
            try:
                message = json.dumps({
                    "job_id": job_id,
                    "problem_type": request.problem_type,
                    "constraints": request.constraints_json,
                    "objectives": request.objectives_json,
                    "timeout": request.timeout_seconds
                })

                self.rabbitmq_channel.basic_publish(
                    exchange='',
                    routing_key='optimization_tasks',
                    body=message,
                    properties=pika.BasicProperties(delivery_mode=2)  # Make message persistent
                )
                logger.info(f"Queued optimization job: {job_id}")

                # Start async processing (mock)
                asyncio.create_task(self._process_optimization_mock(job_id))

            except Exception as e:
                logger.error(f"Failed to queue job: {e}")
                job_info["status"] = "failed"
                job_info["error_message"] = str(e)
        else:
            # Process synchronously if no RabbitMQ
            result = self._solve_optimization_mock(request)
            job_info.update({
                "status": "completed",
                "result_json": result,
                "completed_at": int(time.time())
            })

        return service_pb2.OptimizationResponse(
            job_id=job_id,
            status=job_info["status"],
            result_json=job_info.get("result_json", ""),
            error_message=job_info.get("error_message", "")
        )

    def GetJobStatus(self, request, context):
        """Get job status"""
        job_info = job_storage.get(request.job_id)

        if not job_info:
            return service_pb2.JobStatusResponse(
                job_id=request.job_id,
                status="not_found",
                error_message="Job not found"
            )

        return service_pb2.JobStatusResponse(
            job_id=job_info["job_id"],
            status=job_info["status"],
            result_json=job_info.get("result_json", ""),
            error_message=job_info.get("error_message", ""),
            created_at=job_info["created_at"],
            completed_at=job_info.get("completed_at", 0)
        )

    def _solve_optimization_mock(self, request):
        """Mock optimization solver"""
        # Replace with actual OR-Tools implementation
        result = {
            "solution": "mock_solution",
            "objective_value": 42.0,
            "status": "optimal",
            "variables": {"x": 1, "y": 2}
        }
        return json.dumps(result)

    async def _process_optimization_mock(self, job_id: str):
        """Mock async optimization processing"""
        await asyncio.sleep(2)  # Simulate processing time

        if job_id in job_storage:
            job_storage[job_id].update({
                "status": "completed",
                "result_json": json.dumps({"mock": "result", "job_id": job_id}),
                "completed_at": int(time.time())
            })

# Global service instance
ai_service = AIServiceImplementation()

# FastAPI routes (for direct HTTP access)
@app.get("/")
async def root():
    return {"message": "Python AI Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "grpc": "running",
            "rabbitmq": "connected" if ai_service.rabbitmq_connection else "disconnected"
        }
    }

@app.get("/jobs/{job_id}")
async def get_job_status_http(job_id: str):
    """HTTP endpoint for job status"""
    job_info = job_storage.get(job_id)
    if not job_info:
        return {"error": "Job not found"}, 404
    return job_info

# gRPC server setup
async def serve_grpc():
    server = grpc.aio.server()
    service_pb2_grpc.add_AIServiceServicer_to_server(ai_service, server)

    grpc_port = os.getenv("PYTHON_GRPC_PORT", "50051")
    listen_addr = f"[::]:{grpc_port}"
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    await server.wait_for_termination()

# Main async entrypoint to run both FastAPI and gRPC
async def main():
    import uvicorn

    grpc_task = asyncio.create_task(serve_grpc())

    config = uvicorn.Config(app, host="0.0.0.0", port=int(os.getenv("PYTHON_PORT", "8000")), log_level="info")
    server = uvicorn.Server(config)

    api_task = asyncio.create_task(server.serve())

    await asyncio.gather(grpc_task, api_task)

if __name__ == "__main__":
    asyncio.run(main())
