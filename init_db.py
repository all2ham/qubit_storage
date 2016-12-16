from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker

import base

engine = create_engine('postgresql://househound:H0uS3hOuNd@localhost:5432/qubit_storage')
base.Base.metadata.create_all(engine, checkfirst=True)

