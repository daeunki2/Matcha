
import os

from app.auth.google_oauth import oauth

ft = oauth.register(
    name="ft",
    client_id=os.environ["FT_CLIENT_ID"],
    client_secret=os.environ["FT_CLIENT_SECRET"],
    authorize_url="https://api.intra.42.fr/oauth/authorize",
    access_token_url="https://api.intra.42.fr/oauth/token",
    client_kwargs={"scope": "public"},
)
