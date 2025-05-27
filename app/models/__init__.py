from .analise import AnaliseIA
from .feedback import FeedbackUsuario
from sqlalchemy.orm import relationship

AnaliseIA.feedbacks = relationship("FeedbackUsuario", back_populates="analise")
