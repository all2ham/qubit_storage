from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

class Qubit_Version(Base):
    __tablename__ = 'qubit_versions'
    # note: I've decided to use qubit_id as the primary key to fit
    # the 'device_id' and 'gate_id' pattern, and the suggested use of qubit_id
    # I've changed to 'id_on_device'
    version_id = Column(Integer, primary_key=True)
    id_on_device = Column(Integer)
    device_id = Column(String(60), ForeignKey('devices.device_id',ondelete='SET NULL'))
    qubit_id = Column(Integer, ForeignKey('qubits.qubit_id',ondelete='SET NULL'))
    resonance_freq = Column(Float)
    T1 = Column(Float)
    T2 = Column(Float)
    action = Column(String(10))
    #todo use enum instead of string for security
    gates = relationship("Gate")
    gate_versions = relationship("Gate_Version")
    updated_on = Column(DateTime(timezone=True), default=func.now())