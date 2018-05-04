from app import db
import json, uuid

default_settings = {
    "profile": {
        "first_name": "",
        "last_name": ""
    },
    "privacy": {
        "visibility": "public"
    }
}

class Base(db.Model):

    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class User(Base):

    __tablename__ = "users"

    username = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    groups = db.Column(db.Text, nullable=False)
    settings = db.Column(db.Text, nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def __init__(self, username, email, password):
        global default_settings

        self.username = username
        self.email = email
        self.password = password
        self.groups = "[]"
        self.settings = json.dumps(default_settings)
        self.verified = False

    def get_settings(self):
        global default_settings

        settings = {}

        try:
            settings = json.loads(self.settings)
        except:
            pass

        for section in default_settings.keys():
            if section not in settings:
                settings[section] = default_settings[section]

        for section in settings:
            for key in default_settings[section].keys():
                if key not in settings[section]:
                    settings[section][key] = default_settings[section][key]

        return settings

    def serialize(self, full=False):
        data = {
            "id": self.id,
            "username": self.username,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "groups": json.loads(self.groups)
        }

        if full:
            data["email"] = self.email
            data["settings"] = self.get_settings()
            data["verified"] = self.verified

        return data

class EmailVerification(Base):

    __tablename__ = "email_verifications"

    code = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.Text, nullable=False)

    def __init__(self, user):
        self.code = str(uuid.uuid4()).replace("-", "")
        self.user_id = user.id
        self.email = user.email

class PasswordReset(Base):

    __tablename__ = "password_resets"

    code = db.Column(db.String(32), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)

    def __init__(self, user):
        self.code = str(uuid.uuid4()).replace("-", "")
        self.user_id = user.id
