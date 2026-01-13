from contextlib import contextmanager
from sqlalchemy.orm import Session
from app.data.database import get_db_session

class BaseDataService:
    """
    Base service class that handles database session management.
    All specialized data services should inherit from this class.
    """
    def __init__(self, db_session: Session = None):
        self._db_session = db_session

    @contextmanager
    def _get_db(self):
        """
        Context manager that yields a database session.
        If a session was injected in __init__, it uses that one.
        Otherwise, it creates a new session using get_db_session().
        """
        if self._db_session:
            yield self._db_session
        else:
            with get_db_session() as db:
                yield db
