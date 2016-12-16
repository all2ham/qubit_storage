from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship

class Qubit(Base):
    __tablename__ = 'qubits'
    # note: I've decided to use qubit_id as the primary key to fit
    # the 'device_id' and 'gate_id' pattern, and the suggested use of qubit_id
    # I've changed to 'id_on_device'
    qubit_id = Column(Integer, primary_key=True)
    id_on_device = Column(Integer)
    device_id = Column(String(60), ForeignKey('devices.device_id',ondelete='SET NULL'))
    resonance_freq = Column(Float)
    T1 = Column(Float)
    T2 = Column(Float)
    gates = relationship("Gate")
    versions = relationship("Qubit_Version")