from database import init_db, DBSession
from models import User, Strategy, StrategyStatus, TradingMode
from auth import hash_password

def test_database():
    print("🔧 Testing database setup...")
    init_db()
    with DBSession() as db:
        print("📝 Creating test user...")
        test_user = User(username="testuser", email="test@example.com", password_hash=hash_password("testpassword123"))
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        print(f"✅ User created: {test_user.username} (ID: {test_user.id})")
        
        print("📝 Creating test strategy...")
        test_strategy = Strategy(
            user_id=test_user.id, name="Test RSI Strategy", description="Simple RSI test",
            exchange="binance", trading_pair="BTC/USDT", timeframe="1h",
            parameters={"rsi_period": 14}, stop_loss_pct=2.0, take_profit_pct=5.0,
            status=StrategyStatus.DRAFT, trading_mode=TradingMode.PAPER
        )
        db.add(test_strategy)
        db.commit()
        db.refresh(test_strategy)
        print(f"✅ Strategy created: {test_strategy.name} (ID: {test_strategy.id})")
        
        print("🔍 Testing queries...")
        strategies = db.query(Strategy).filter(Strategy.user_id == test_user.id).all()
        print(f"✅ Found {len(strategies)} strategies")
        
        print("🧹 Cleaning up...")
        db.delete(test_strategy)
        db.delete(test_user)
        db.commit()
        print("✅ Test data cleaned")
    print("\n✨ All tests passed! Database ready.")

if __name__ == "__main__":
    test_database()
