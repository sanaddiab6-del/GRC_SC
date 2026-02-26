"""
Security Training & Awareness Database Models

ISO 27001 A.6.3 (Awareness, education and training).
NCA ECC-HR (Human Resources Security).
Bilingual training content and competency tracking.
"""

from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import Uuid, Column, Integer, String, Text, DateTime, Boolean, JSON, ForeignKey, Enum as SQLEnum, Float
from sqlalchemy.orm import relationship
from enum import Enum

from core.database import Base


class TrainingType(str, Enum):
    """Training delivery methods"""
    ONLINE_COURSE = "online_course"
    CLASSROOM = "classroom"
    WORKSHOP = "workshop"
    WEBINAR = "webinar"
    SIMULATION = "simulation"
    PHISHING_TEST = "phishing_test"
    TABLE_TOP_EXERCISE = "table_top_exercise"
    CERTIFICATION_PREP = "certification_prep"


class TrainingStatus(str, Enum):
    """Training lifecycle status"""
    DRAFT = "draft"
    PUBLISHED = "published"
    ACTIVE = "active"
    ARCHIVED = "archived"


class EnrollmentStatus(str, Enum):
    """User enrollment status"""
    ENROLLED = "enrolled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"
    WAIVED = "waived"


class TrainingCourse(Base):
    """
    Security training courses and awareness programs.
    ISO 27001 A.6.3 compliance.
    """
    __tablename__ = "training_courses"

    course_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(50), unique=True, nullable=False)  # Format: TRAIN-{CATEGORY}-{NUMBER}
    
    # Course details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    learning_objectives_en = Column(JSON, nullable=False)  # List of learning objectives
    learning_objectives_ar = Column(JSON, nullable=False)
    
    # Training configuration
    training_type = Column(SQLEnum(TrainingType, native_enum=False), nullable=False)
    category = Column(String(100), nullable=False)  # "security_awareness", "privacy", "compliance", "technical", "governance"
    difficulty_level = Column(String(50), nullable=False)  # "beginner", "intermediate", "advanced"
    duration_minutes = Column(Integer, nullable=False)
    
    # Requirements
    is_mandatory = Column(Boolean, nullable=False, default=False)
    required_for_roles = Column(JSON, nullable=True)  # List of role names/IDs
    prerequisites = Column(JSON, nullable=True)  # List of prerequisite course IDs
    validity_days = Column(Integer, nullable=True)  # Days before recertification required (None = lifetime)
    passing_score = Column(Integer, nullable=False, default=80)  # Percentage required to pass
    
    # Content
    content_url_en = Column(String(1000), nullable=True)  # SCORM package or video URL
    content_url_ar = Column(String(1000), nullable=True)
    materials_json = Column(JSON, nullable=True)  # List of downloadable materials
    
    # Compliance mapping
    iso27001_controls = Column(JSON, nullable=True)
    nca_ecc_controls = Column(JSON, nullable=True)
    pdpl_articles = Column(JSON, nullable=True)
    sdaia_ai_principles = Column(JSON, nullable=True)
    
    # Course management
    instructor_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    status = Column(SQLEnum(TrainingStatus, native_enum=False), nullable=False, default=TrainingStatus.DRAFT)
    published_date = Column(DateTime, nullable=True)
    last_updated_date = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Statistics
    total_enrollments = Column(Integer, nullable=False, default=0)
    total_completions = Column(Integer, nullable=False, default=0)
    average_score = Column(Float, nullable=True)
    average_completion_time_minutes = Column(Integer, nullable=True)
    
    # Metadata
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    instructor = relationship("User", foreign_keys=[instructor_id])
    enrollments = relationship("TrainingEnrollment", back_populates="course")
    assessments = relationship("TrainingAssessment", back_populates="course")


class TrainingEnrollment(Base):
    """
    User enrollment in training courses.
    Tracks individual learning progress.
    """
    __tablename__ = "training_enrollments"

    enrollment_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("training_courses.course_id"), nullable=False)
    user_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    
    # Enrollment details
    enrolled_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    enrollment_method = Column(String(50), nullable=False)  # "auto_assigned", "self_enrolled", "manager_assigned"
    assigned_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    due_date = Column(DateTime, nullable=True)
    
    # Progress tracking
    status = Column(SQLEnum(EnrollmentStatus, native_enum=False), nullable=False, default=EnrollmentStatus.ENROLLED)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    progress_percentage = Column(Integer, nullable=False, default=0)  # 0-100
    time_spent_minutes = Column(Integer, nullable=False, default=0)
    
    # Assessment results
    attempts_count = Column(Integer, nullable=False, default=0)
    best_score = Column(Integer, nullable=True)  # Percentage
    passing_score_required = Column(Integer, nullable=False, default=80)
    passed = Column(Boolean, nullable=False, default=False)
    
    # Certificate
    certificate_issued = Column(Boolean, nullable=False, default=False)
    certificate_number = Column(String(100), nullable=True, unique=True)
    certificate_issued_at = Column(DateTime, nullable=True)
    certificate_expires_at = Column(DateTime, nullable=True)
    
    # Reminders
    reminder_sent_at = Column(DateTime, nullable=True)
    overdue_notification_sent = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("TrainingCourse", back_populates="enrollments")
    user = relationship("User", foreign_keys=[user_id])
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    attempts = relationship("TrainingAttempt", back_populates="enrollment")


class TrainingAssessment(Base):
    """
    Quiz/assessment questions for training courses.
    Supports multiple question types.
    """
    __tablename__ = "training_assessments"

    assessment_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("training_courses.course_id"), nullable=False)
    
    # Question details (bilingual)
    question_en = Column(Text, nullable=False)
    question_ar = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # "multiple_choice", "true_false", "multi_select"
    
    # Options and answers (bilingual)
    options_en = Column(JSON, nullable=True)  # List of answer options
    options_ar = Column(JSON, nullable=True)
    correct_answer = Column(JSON, nullable=False)  # Index(es) of correct answer(s)
    
    # Explanation (bilingual)
    explanation_en = Column(Text, nullable=True)
    explanation_ar = Column(Text, nullable=True)
    
    # Configuration
    points = Column(Integer, nullable=False, default=1)
    order_number = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("TrainingCourse", back_populates="assessments")


class TrainingAttempt(Base):
    """
    Individual quiz/assessment attempts.
    Tracks user responses and scoring.
    """
    __tablename__ = "training_attempts"

    attempt_id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("training_enrollments.enrollment_id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    
    # Attempt details
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    time_spent_minutes = Column(Integer, nullable=True)
    
    # Responses (JSON array of {assessment_id, selected_answer, is_correct, points_earned})
    responses_json = Column(JSON, nullable=False)
    
    # Scoring
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False, default=0)
    score_percentage = Column(Integer, nullable=False, default=0)
    points_earned = Column(Integer, nullable=False, default=0)
    points_possible = Column(Integer, nullable=False)
    passed = Column(Boolean, nullable=False, default=False)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    enrollment = relationship("TrainingEnrollment", back_populates="attempts")


class AwarenessCampaign(Base):
    """
    Security awareness campaigns and communications.
    ISO 27001 A.6.3 (Awareness, education and training).
    """
    __tablename__ = "awareness_campaigns"

    campaign_id = Column(Integer, primary_key=True, index=True)
    campaign_code = Column(String(50), unique=True, nullable=False)  # Format: CAMP-{YYYYMM}-{NUMBER}
    
    # Campaign details (bilingual)
    title_en = Column(String(500), nullable=False)
    title_ar = Column(String(500), nullable=False)
    description_en = Column(Text, nullable=False)
    description_ar = Column(Text, nullable=False)
    message_en = Column(Text, nullable=False)
    message_ar = Column(Text, nullable=False)
    
    # Campaign type
    campaign_type = Column(String(100), nullable=False)  # "email", "poster", "video", "newsletter", "phishing_simulation"
    category = Column(String(100), nullable=False)  # "password_security", "social_engineering", "data_protection", "physical_security"
    
    # Targeting
    target_audience = Column(JSON, nullable=False)  # List of departments/roles
    target_user_ids = Column(JSON, nullable=True)  # Specific users if not organization-wide
    
    # Schedule
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    delivery_frequency = Column(String(50), nullable=True)  # "one_time", "weekly", "monthly"
    
    # Content
    content_url = Column(String(1000), nullable=True)
    attachments_json = Column(JSON, nullable=True)
    
    # Effectiveness tracking
    total_sent = Column(Integer, nullable=False, default=0)
    total_opened = Column(Integer, nullable=False, default=0)
    total_clicked = Column(Integer, nullable=False, default=0)
    total_completed_action = Column(Integer, nullable=False, default=0)
    
    # Phishing simulation metrics (if applicable)
    total_phishing_clicks = Column(Integer, nullable=True)
    total_reported_phishing = Column(Integer, nullable=True)
    
    # Campaign management
    created_by_id = Column(Uuid(as_uuid=True), ForeignKey("users.user_id"), nullable=False)
    status = Column(String(50), nullable=False, default="draft")  # draft, scheduled, active, completed, cancelled
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by = relationship("User")


class CompetencyMatrix(Base):
    """
    Role-based security competency requirements.
    ISO 27001 A.6.2 (Terms and conditions of employment).
    """
    __tablename__ = "competency_matrix"

    competency_id = Column(Integer, primary_key=True, index=True)
    
    # Role identification
    role_name = Column(String(200), nullable=False)
    department = Column(String(200), nullable=True)
    
    # Required training
    required_courses = Column(JSON, nullable=False)  # List of course IDs
    optional_courses = Column(JSON, nullable=True)  # List of optional course IDs
    
    # Certifications
    required_certifications = Column(JSON, nullable=True)  # List of required external certs (CISSP, CISM, etc.)
    preferred_certifications = Column(JSON, nullable=True)
    
    # Competency levels (bilingual)
    competency_description_en = Column(Text, nullable=True)
    competency_description_ar = Column(Text, nullable=True)
    
    # Requirements
    minimum_training_hours_per_year = Column(Integer, nullable=False, default=8)
    recertification_period_days = Column(Integer, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
