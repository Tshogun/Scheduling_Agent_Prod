package main

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	pb "go-orchestrator/internal/proto" // Adjust import path
)

type Server struct {
	pythonClient pb.AIServiceClient
	grpcConn     *grpc.ClientConn
}

type HealthResponse struct {
	Status    string                 `json:"status"`
	Services  map[string]interface{} `json:"services"`
	Timestamp time.Time              `json:"timestamp"`
}

func main() {
	// Initialize server
	server := &Server{}

  // Connect to Python gRPC service
	if err := server.connectToPythonService(); err != nil {
		log.Printf("Warning: Could not connect to Python service: %v", err)
	}

	// Setup HTTP router
	r := gin.Default()
	r.Use(cors.Default())

	// Health check endpoint
	r.GET("/health", server.healthCheck)

	// API routes
	api := r.Group("/api/v1")
	{
		api.GET("/ping", server.ping)
		api.POST("/completion", server.getCompletion)
		api.POST("/optimize", server.optimize)
		api.GET("/job/:id", server.getJobStatus)
	}

	// Start HTTP server
	port := getEnv("GO_PORT", "8080")
	log.Printf("Starting Go Orchestrator on port %s", port)
	log.Fatal(r.Run(":" + port))
}

func (s *Server) connectToPythonService() error {
	pythonAddr := getEnv("PYTHON_GRPC_ADDR", "localhost:50051")
	conn, err := grpc.NewClient(pythonAddr, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return err
	}

	s.grpcConn = conn
	s.pythonClient = pb.NewAIServiceClient(conn)

	// Test connection
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	_, err = s.pythonClient.Ping(ctx, &pb.PingRequest{Message: "connection test"})
	if err != nil {
		return err
	}

  log.Println("Successfully connected to Python gRPC service")
	return nil
}

func (s *Server) healthCheck(c *gin.Context) {
	response := HealthResponse{
		Status:    "healthy",
		Timestamp: time.Now(),
		Services:  make(map[string]interface{}),
	}

	// Check Python service
	if s.pythonClient != nil {
		ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
		defer cancel()
   
    _, err := s.pythonClient.Ping(ctx, &pb.PingRequest{Message: "health check"})
		if err != nil {
			response.Services["python"] = map[string]interface{}{
				"status": "unhealthy",
				"error":  err.Error(),
			}
		} else {
			response.Services["python"] = map[string]interface{}{
				"status": "healthy",
			}
		}
	} else {
		response.Services["python"] = map[string]interface{}{
			"status": "disconnected",
		}
	}

	c.JSON(http.StatusOK, response)
}

func (s *Server) ping(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"message":   "pong from Go orchestrator",
		"timestamp": time.Now(),
	})
}

func (s *Server) getCompletion(c *gin.Context) {
	var req struct {
		Prompt    string `json:"prompt" binding:"required"`
		Model     string `json:"model"`
		MaxTokens int32  `json:"max_tokens"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if s.pythonClient == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Python service not available"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	grpcReq := &pb.CompletionRequest{
		Prompt:    req.Prompt,
		Model:     req.Model,
		MaxTokens: req.MaxTokens,
	}

	resp, err := s.pythonClient.GetCompletion(ctx, grpcReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"completion":  resp.Completion,
		"tokens_used": resp.TokensUsed,
		"model":       resp.Model,
	})
}

func (s *Server) optimize(c *gin.Context) {
	var req struct {
		ProblemType     string `json:"problem_type" binding:"required"`
		ConstraintsJSON string `json:"constraints_json"`
		ObjectivesJSON  string `json:"objectives_json"`
		TimeoutSeconds  int32  `json:"timeout_seconds"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if s.pythonClient == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Python service not available"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	grpcReq := &pb.OptimizationRequest{
		ProblemType:     req.ProblemType,
		ConstraintsJson: req.ConstraintsJSON,
		ObjectivesJson:  req.ObjectivesJSON,
		TimeoutSeconds:  req.TimeoutSeconds,
	}

	resp, err := s.pythonClient.SolveOptimization(ctx, grpcReq)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"job_id": resp.JobId,
		"status": resp.Status,
		"result": resp.ResultJson,
	})
}

func (s *Server) getJobStatus(c *gin.Context) {
	jobID := c.Param("id")

  if s.pythonClient == nil {
		c.JSON(http.StatusServiceUnavailable, gin.H{"error": "Python service not available"})
		return
	}

	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	resp, err := s.pythonClient.GetJobStatus(ctx, &pb.JobStatusRequest{JobId: jobID})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"job_id":       resp.JobId,
		"status":       resp.Status,
		"result":       resp.ResultJson,
		"error":        resp.ErrorMessage,
		"created_at":   resp.CreatedAt,
		"completed_at": resp.CompletedAt,
	})
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}