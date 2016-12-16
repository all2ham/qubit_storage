# DB_Versioning Programming Exercise
#
# This program connects to a postgresql database using AlchemySQL and creates 5 tables for device, qubit
# and gate storage, as well as qubit and gate versioning.
# The database models are located in the following files:
#        - devices.py
#        - qubits.py
#        - gates.py
#        - qubit_versions.py
#        - gate_versions.py

from sqlalchemy import create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from  sqlalchemy.sql.expression import func, select

import datetime
import base
import random
import string

import devices
import gates
import qubits
import qubit_versions
import gate_versions

engine = create_engine('postgresql://househound:H0uS3hOuNd@localhost:5432/qubit_storage')
Session = sessionmaker(bind=engine)
session = Session()

if not engine.dialect.has_table(engine.connect(), "devices"):  # If database does not exist, create.
    execfile('init_db.py')
    print'Database was initialized and seeded.'

### create
def store_device(unique_id,description):
    session.add(devices.Device(device_id=unique_id,
                               device_description=description))
    session.commit()

def store_qubit(id_on_device,device_id,resonance_freq,T1,T2):
    session.add(qubits.Qubit(id_on_device=id_on_device,
                             device_id=device_id,
                             resonance_freq=resonance_freq,
                             T1=T1,
                             T2=T2))
    q = session.query(qubits.Qubit).filter(qubits.Qubit.device_id==device_id,qubits.Qubit.id_on_device==id_on_device).one()
    session.add(qubit_versions.Qubit_Version(id_on_device=id_on_device,
                                             device_id=device_id,
                                             qubit_id=q.qubit_id,
                                             resonance_freq=resonance_freq,
                                             T1=T1,
                                             T2=T2,
                                             action='CREATE'))
    session.commit()


def store_gate(name,qubit_id,amplitude,width,phase):
    session.add(gates.Gate(name=name,
                           qubit_id=qubit_id,
                           amplitude=amplitude,
                           width=width,
                           phase=phase))
    q = session.query(gates.Gate).filter(gates.Gate.qubit_id==qubit_id,gates.Gate.name==name).one()
    session.add(gate_versions.Gate_Version(name=name,
                                           qubit_id=qubit_id,
                                           gate_id=q.gate_id,
                                           amplitude=amplitude,
                                           width=width,
                                           phase=phase,
                                           action='CREATE'))
    session.commit()


### update
def update_device(device_id, new_description=False):
    # no versioning
    try:
        q = session.query(devices.Device).filter(devices.Device.device_id==device_id).one()
        if new_description:
            q.device_description = new_description
        session.commit()
    except:
        print 'device named \''+str(device_id)+'\' not found'

def update_qubit(qubit_id,**kwargs):
    try:
        qubit_query = session.query(qubits.Qubit).filter(qubits.Qubit.qubit_id==qubit_id).one()
        for k,v in kwargs.iteritems():
            if k == 'new_resonance_freq':
                qubit_query.resonance_freq = v
            if k == 'new_T1':
                qubit_query.T1 = v
            if k == 'new_T2':
                qubit_query.T2 = v
        # Store update in qubit_versions table.
        session.add(qubit_versions.Qubit_Version(id_on_device=qubit_query.id_on_device,
                                                 device_id=qubit_query.device_id,
                                                 qubit_id=qubit_query.qubit_id,
                                                 resonance_freq=qubit_query.resonance_freq,
                                                 T1=qubit_query.T1,
                                                 T2=qubit_query.T2,
                                                 action='UPDATE'))
        # Version all current gates with new qubit version.
        gate_version_query = session.query(gates.Gate).filter_by(qubit_id=qubit_query.qubit_id).all()
        qubit_version_query = session.query(qubit_versions.Qubit_Version).filter(qubit_versions.Qubit_Version.qubit_id==qubit_query.qubit_id).order_by(qubit_versions.Qubit_Version.updated_on.desc()).first()
        for row in gate_version_query:
            session.add(gate_versions.Gate_Version(name=row.name,
                                                   qubit_id=row.qubit_id,
                                                   gate_id=row.gate_id,
                                                   qubit_version = qubit_version_query.version_id,
                                                   amplitude=row.amplitude,
                                                   width=row.width,
                                                   phase=row.phase,
                                                   action='QUPDATE'))
        session.commit()
    except:
        print 'qubit with id \''+str(qubit_id)+'\' not found'

def update_gate(gate_id,new_amp=False,new_width=False,new_phase=False):
    try:
        gate_query = session.query(gates.Gate).filter(gates.Gate.gate_id==gate_id).one()
        qubit_version_query = session.query(qubit_versions.Qubit_Version).filter(qubit_versions.Qubit_Version.qubit_id==gate_query.qubit_id).order_by(qubit_versions.Qubit_Version.updated_on.desc()).first()
        if new_amp:
            gate_query.amplitude=new_amp
        if new_width:
            gate_query.width=new_width
        if new_phase:
            gate_query.phase=new_phase
        # Store update in gate_versions table.
        session.add(gate_versions.Gate_Version(name=gate_query.name,
                                               qubit_id=gate_query.qubit_id,
                                               gate_id=gate_query.gate_id,
                                               qubit_version = qubit_version_query.version_id,
                                               amplitude=gate_query.amplitude,
                                               width=gate_query.width,
                                               phase=gate_query.phase,
                                               action='UPDATE'))
        session.commit()
    except:
        print 'gate with id \''+str(gate_id)+'\' not found'

### delete
def delete_device(device_id):
    try:
        session.query(devices.Device).filter(devices.Device.device_id==device_id).one().delete()
        session.commit()
    except:
        print 'device named \''+str(device_id)+'\' not found'
def delete_qubit(qubit_id):
    try:
        q = session.query(qubits.Qubit).filter(qubits.Qubit.qubit_id==qubit_id).one()
        # Store delete event in qubit_versions table.
        session.add(qubit_versions.Qubit_Version(id_on_device=q.id_on_device,
                                                 device_id=q.device_id,
                                                 qubit_id=q.qubit_id,
                                                 resonance_freq=q.resonance_freq,
                                                 T1=q.T1,
                                                 T2=q.T2,
                                                 action='DELETE'))
        session.delete(q)
        session.commit()
    except:
        print 'qubit with id \''+str(qubit_id)+'\' not found'

def delete_gate(gate_id):
    try:
        q = session.query(gates.Gate).filter(gates.Gate.gate_id==gate_id).one()
        # Store delete event in gate_versions table.
        session.add(gate_versions.Gate_Version(name=q.name,
                                               qubit_id=q.qubit_id,
                                               gate_id=q.gate_id,
                                               amplitude=q.amplitude,
                                               width=q.width,
                                               phase=q.phase,
                                               action='DELETE'))
        session.delete(q)
        session.commit()
    except:
        print 'gate with id \''+str(gate_id)+'\' not found'

# End of core functions.
# The following part of this file is a seeding function and various functions that can
# be used to test the core functionality as well as examples for CRUD operations that need to be made.

def randomstring(chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(10))

def seed_db():
    for i in range(5):
        store_device(randomstring(),randomstring())
        for j in range(5):
            q=session.query(devices.Device)[(i)]
            print(q)
            store_qubit(j,q.device_id,random.uniform(10,100),random.uniform(10,100),random.uniform(10,100))
            print('storedq')
            for k in range(20):
                store_gate(randomstring(),j+1,random.uniform(10,100),random.uniform(10,100),random.uniform(10,100))

# seed_db()

def list_devices():
    for d in session.query(devices.Device):
        print d.device_id.encode('ascii') + ':', d.device_description.encode('ascii')

def get_device(id):
    d = session.query(devices.Device).filter(devices.Device.device_id==id).one()
    q_list = session.query(qubits.Qubit).filter(qubits.Qubit.device_id==id).all()
    print d.device_id.encode('ascii') + ':', d.device_description.encode('ascii')
    for q in q_list:
        print q.qubit_id, q.id_on_device, q.resonance_freq, q.T1, q.T2

def get_q_history(id):
    for v in session.query(qubit_versions.Qubit_Version).filter(qubit_versions.Qubit_Version.qubit_id==id).all():
        print v.version_id, v.qubit_id, v.id_on_device, v.resonance_freq, v.T1, v.T2, v.action, v.updated_on

def recover_q_version(qubit_version):
    q = session.query(qubit_versions.Qubit_Version).filter(qubit_versions.Qubit_Version.version_id==qubit_version).one()
    print q.version_id, q.qubit_id, q.id_on_device, q.resonance_freq, q.T1, q.T2, q.action, q.updated_on
    for g in session.query(gate_versions.Gate_Version).filter(gate_versions.Gate_Version.qubit_version==qubit_version):
        print g.version_id, g.name, g.qubit_id, g.gate_id, g.qubit_version, g.amplitute, g.width, g.phase, g.action, g.updated_on


# list_devices()
#get_device('SRDLOURWFE')

# update_qubit(5,55,False,False)
# update_qubit(13,65,False,False)
# update_qubit(5,75,False,False)
# update_gate(1,100,300,False)

# get_q_history(5)

# recover_q_version(44)

# delete_gate(2)
# delete_qubit(2)

#todo error handling
#todo indexing for optimization
#todo if qubits/gates are not needed after being orphaned, cascade deletes through foreign keys
#todo composite keys
#todo testing