from sqlalchemy import create_engine

# Format: mysql+mysqlconnector://<username>:<password>@<host>/<dbname>
engine = create_engine(
    "mysql+mysqlconnector://root:my-secret-pw@localhost/footballplayers_analysis",
    echo=False  # Set to False to disable SQL query logging
)

def add(object):
    """
    Add an object to the database session.
    """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        session.add(object)
        session.commit()
    except Exception as e:
        print(f"Error adding object: {e}")
        session.rollback()
    finally:
        session.close()

def get_session():
    """
    Get a new session for database operations.
    """
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    return Session()
