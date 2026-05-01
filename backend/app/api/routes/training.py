from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
import os
import sys
from app.db.database import get_db, SessionLocal
from app.models.product import TrainingSession, DetectionLog
from app.models.user import User
from app.schemas import TrainingSessionCreate, TrainingSessionResponse
from app.core.security import get_current_user
from datetime import datetime

# Add ml_pipeline to path
ml_pipeline_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ml-pipeline')
if ml_pipeline_path not in sys.path:
    sys.path.insert(0, ml_pipeline_path)

try:
    from training.train import YOLOTrainer
except ImportError as e:
    print(f"Warning: Could not import YOLOTrainer from ml_pipeline: {e}")
    try:
        from app.services.yolo_trainer import YOLOTrainer
    except ImportError as e2:
        print(f"Warning: Could not import YOLOTrainer from services: {e2}")
        YOLOTrainer = None

router = APIRouter()

@router.post("/start-training", response_model=TrainingSessionResponse)
async def start_training(
    training: TrainingSessionCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start a new training session"""
    
    # Check if user is admin
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can start training sessions"
        )
    
    # Count dataset size (detection logs)
    dataset_size = db.query(DetectionLog).count()
    
    if dataset_size < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Need at least 10 detection samples to start training"
        )
    
    # Create training session
    training_session = TrainingSession(
        name=training.name,
        status="pending",
        epochs=training.epochs,
        batch_size=training.batch_size,
        dataset_size=dataset_size
    )
    
    db.add(training_session)
    db.commit()
    db.refresh(training_session)
    
    # Add background task to start training
    background_tasks.add_task(
        train_yolo_model,
        training_session.id
    )
    
    return training_session

@router.get("/sessions", response_model=list[TrainingSessionResponse])
async def get_training_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all training sessions"""
    
    sessions = db.query(TrainingSession).order_by(TrainingSession.created_at.desc()).all()
    return sessions

@router.get("/sessions/{session_id}", response_model=TrainingSessionResponse)
async def get_training_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Get training session details"""
    
    session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found"
        )
    
    return session

async def train_yolo_model(session_id: int):
    """Background task to train YOLO model from detection logs"""
    db = SessionLocal()
    try:
        session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if not session:
            return

        session.status = "running"
        session.started_at = datetime.now()
        db.commit()

        if YOLOTrainer is None:
            session.status = "failed"
            session.training_log = "YOLOTrainer not available - ml_pipeline import failed"
            db.commit()
            return

        detection_logs = db.query(DetectionLog).all()
        if not detection_logs:
            session.status = "failed"
            session.training_log = "No detection logs found for training"
            db.commit()
            return

        yolo_logs = []
        for log in detection_logs:
            image_path = log.image_path
            if not os.path.exists(image_path):
                candidate = os.path.join(os.getcwd(), image_path)
                if os.path.exists(candidate):
                    image_path = candidate

            yolo_logs.append({
                "image_path": image_path,
                "detected_brand": log.detected_brand or "Other_Shoe",
                "detection_metadata": log.detection_metadata or {}
            })

        trainer = YOLOTrainer()
        dataset_path = trainer.prepare_dataset(yolo_logs)
        result = trainer.train(dataset_path, epochs=session.epochs, batch_size=session.batch_size)

        if result.get("success"):
            session.status = "completed"
            session.completed_at = datetime.now()
            session.accuracy = result.get("results", {}).get("accuracy")
            session.loss = result.get("results", {}).get("loss")
            session.model_path = result.get("model_path")
            session.training_log = "Training completed successfully"
        else:
            session.status = "failed"
            session.training_log = result.get("error", "Training failed")

        db.commit()

    except Exception as e:
        session = db.query(TrainingSession).filter(TrainingSession.id == session_id).first()
        if session:
            session.status = "failed"
            session.training_log = str(e)
            db.commit()
    finally:
        db.close()
