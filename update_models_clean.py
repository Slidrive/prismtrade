import codecs

# Read backup with BOM handling
with open('models.py.backup', 'r', encoding='utf-8-sig') as f:
    content = f.read()

# Add api_keys relationship to User class
content = content.replace(
    "    trades = relationship('Trade', back_populates='user', cascade='all, delete-orphan')",
    "    trades = relationship('Trade', back_populates='user', cascade='all, delete-orphan')\n    api_keys = relationship('APIKey', back_populates='user', cascade='all, delete-orphan')"
)

# Add APIKey class after ExchangeConnection
apikey_class = """

class APIKey(Base):
    __tablename__ = 'api_keys'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    exchange = Column(String(50), nullable=False)
    encrypted_key = Column(Text, nullable=False)
    encrypted_secret = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    user = relationship('User', back_populates='api_keys')
"""

content = content.replace(
    "    user = relationship('User', back_populates='exchanges')",
    "    user = relationship('User', back_populates='exchanges')" + apikey_class
)

# Write WITHOUT BOM
with open('models.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ models.py updated!')
