from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship

class Device(Base):
    __tablename__ = 'devices'
    device_id = Column(String(60), primary_key=True)
    device_description = Column(String(255))
    qubits = relationship("Qubit")
    versioned_qubits = relationship("Qubit_Version")