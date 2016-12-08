# coding: utf-8
from sqlalchemy import Column, Float, Integer, Table, Text, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class CostByState(Base):
    __tablename__ = 'cost_by_state'

    id = Column(Integer, primary_key=True, server_default=text("nextval('cost_by_state_id_seq'::regclass)"))
    state = Column(Text)
    phase1 = Column(Float(53))
    phase2 = Column(Float(53))
    phase3 = Column(Float(53))
    phase4 = Column(Float(53))


t_maxavgppl = Table(
    'maxavgppl', metadata,
    Column('max', Integer)
)


t_maxtrials = Table(
    'maxtrials', metadata,
    Column('max', Integer)
)


t_maxtrialsperphase = Table(
    'maxtrialsperphase', metadata,
    Column('max', Integer)
)


class ReputationFactor(Base):
    __tablename__ = 'reputation_factors'

    id = Column(Integer, primary_key=True, server_default=text("nextval('reputation_factors_id_seq'::regclass)"))
    name = Column(Text)
    location = Column(Text)
    no_of_trials = Column(Integer)
    no_of_trials_per_phase = Column(Integer)
    avg_people_per_phase = Column(Integer)
    grants = Column(Integer)
    publication_count = Column(Integer)


class Test(Base):
    __tablename__ = 'test'

    id = Column(Integer, primary_key=True, server_default=text("nextval('test_id_seq'::regclass)"))
    one = Column(Text)
    two = Column(Text)
    three = Column(Text)


class Top25(Base):
    __tablename__ = 'top_25'

    id = Column(Integer, primary_key=True, server_default=text("nextval('top_25_id_seq'::regclass)"))
    name = Column(Text)
    location = Column(Text)
    no_of_trials = Column(Integer)
    no_of_trials_per_phase = Column(Integer)
    avg_people_per_phase = Column(Integer)
    grants = Column(Integer)
    publication_count = Column(Integer)


class TrialDatum(Base):
    __tablename__ = 'trial_data'

    id = Column(Integer, primary_key=True, server_default=text("nextval('trial_data_id_seq'::regclass)"))
    name = Column(Text)
    location = Column(Text)
    phase = Column(Integer)
    no_of_people = Column(Integer)
