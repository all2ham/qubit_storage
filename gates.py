from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship

class Gate(Base):
    __tablename__ = 'gates'
    gate_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    qubit_id = Column(Integer, ForeignKey('qubits.qubit_id',ondelete='SET NULL'))
    qubit_version = Column(Integer, ForeignKey('qubit_versions.version_id',ondelete='SET NULL'))
    amplitude = Column(Float)
    width = Column(Float)
    phase = Column(Float)
    versions = relationship("Gate_Version")