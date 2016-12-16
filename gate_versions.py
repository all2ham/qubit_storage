from sqlalchemy import *
from base import Base
from sqlalchemy.sql import func

class Gate_Version(Base):
    __tablename__ = 'gate_versions'
    version_id = Column(Integer, primary_key=True)
    name = Column(String(50))
    qubit_id = Column(Integer, ForeignKey('qubits.qubit_id',ondelete='SET NULL'))
    gate_id = Column(Integer, ForeignKey('gates.gate_id',ondelete='SET NULL'))
    qubit_version = Column(Integer, ForeignKey('qubit_versions.version_id'))
    amplitude = Column(Float)
    width = Column(Float)
    phase = Column(Float)
    action = Column(String(10))
    #todo use enum instead of string for security
    updated_on = Column(DateTime(timezone=True), default=func.now())