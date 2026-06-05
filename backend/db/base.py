from backend.db.session import Base

# Import all models so Alembic sees them
from backend.models.user import User
from backend.models.generated_sites import GeneratedSite
from backend.models.subscription import Subscription
from backend.models.refresh_token import RefreshToken
