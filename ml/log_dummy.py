import mlflow

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("demo-experiment")

with mlflow.start_run(run_name="test-run"):
    mlflow.log_param("param1", 42)
    mlflow.log_metric("metric1", 0.95)
    mlflow.log_metric("metric2", 0.89)

print("Logged dummy data to MLflow!")
