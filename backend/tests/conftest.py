"""
Pytest configuration and fixtures
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User, UserRole
from faker import Faker

fake = Faker()

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a test database session"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.close()
        # Drop tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client"""
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user"""
    from app.core.security import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        full_name="Test User",
        role=UserRole.OPERATOR,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin_user(db: Session) -> User:
    """Create a test admin user"""
    from app.core.security import get_password_hash
    
    user = User(
        username="admin",
        email="admin@example.com",
        hashed_password=get_password_hash("adminpassword123"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Create authentication headers for test user"""
    access_token = create_access_token(
        data={"sub": str(test_user.user_id), "role": test_user.role.value}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def admin_auth_headers(test_admin_user: User) -> dict:
    """Create authentication headers for admin user"""
    access_token = create_access_token(
        data={"sub": str(test_admin_user.user_id), "role": test_admin_user.role.value}
    )
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def test_well(db: Session, test_user: User) -> dict:
    """Create a test well"""
    from app.models.well import Well
    
    well = Well(
        well_id="test-well-1",
        name="Test Well 1",
        location="Test Location",
        latitude=30.0,
        longitude=50.0,
        well_type="ESP",
        is_active=True,
        created_by=test_user.user_id
    )
    db.add(well)
    db.commit()
    db.refresh(well)
    return {
        "well_id": well.well_id,
        "name": well.name,
        "location": well.location,
        "latitude": well.latitude,
        "longitude": well.longitude,
        "well_type": well.well_type,
        "is_active": well.is_active
    }


@pytest.fixture
def test_sensor(db: Session, test_well: dict) -> dict:
    """Create a test sensor"""
    from app.models.sensor import Sensor
    
    sensor = Sensor(
        sensor_id="test-sensor-1",
        well_id=test_well["well_id"],
        sensor_type="temperature",
        name="Temperature Sensor 1",
        unit="Celsius",
        min_value=0.0,
        max_value=100.0,
        is_active=True
    )
    db.add(sensor)
    db.commit()
    db.refresh(sensor)
    return {
        "sensor_id": sensor.sensor_id,
        "well_id": sensor.well_id,
        "sensor_type": sensor.sensor_type,
        "name": sensor.name,
        "unit": sensor.unit,
        "min_value": sensor.min_value,
        "max_value": sensor.max_value,
        "is_active": sensor.is_active
    }


@pytest.fixture
def fake_well_data() -> dict:
    """Generate fake well data"""
    return {
        "name": fake.company() + " Well",
        "location": fake.address(),
        "latitude": float(fake.latitude()),
        "longitude": float(fake.longitude()),
        "well_type": fake.random_element(elements=("ESP", "PCP", "Gas Lift", "Rod Pump")),
        "is_active": True
    }


@pytest.fixture
def fake_sensor_data(test_well: dict) -> dict:
    """Generate fake sensor data"""
    sensor_types = ["temperature", "pressure", "current", "vibration", "flow_rate"]
    return {
        "well_id": test_well["well_id"],
        "sensor_type": fake.random_element(elements=sensor_types),
        "name": fake.word().capitalize() + " Sensor",
        "unit": fake.random_element(elements=("Celsius", "PSI", "Ampere", "Hz", "GPM")),
        "min_value": 0.0,
        "max_value": 100.0,
        "is_active": True
    }

