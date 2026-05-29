from shared.database.base import Base, engine
from shared.models.tenant import TenantModel
from shared.models.lead import LeadModel, QualificationScoreModel
from shared.models.conversation import ConversationModel, MessageModel
from shared.models.appointment import AppointmentModel
from shared.models.workflow import WorkflowModel, WorkflowExecutionModel


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()
