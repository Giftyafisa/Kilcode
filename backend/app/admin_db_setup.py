from sqlalchemy import create_engine, text
from app.core.config import settings

def setup_admin_db():
    # Create engine
    engine = create_engine(settings.ADMIN_DATABASE_URL)
    
    # Create tables
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email VARCHAR NOT NULL UNIQUE,
                name VARCHAR NOT NULL,
                hashed_password VARCHAR NOT NULL,
                country VARCHAR(7) NOT NULL,
                phone VARCHAR NOT NULL UNIQUE,
                balance FLOAT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                is_active BOOLEAN,
                is_verified BOOLEAN
            );

            CREATE TABLE IF NOT EXISTS betting_codes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                bookmaker VARCHAR,
                code VARCHAR,
                odds FLOAT CHECK (odds >= 1.0),
                stake FLOAT NOT NULL CHECK (stake > 0),
                potential_winnings FLOAT NOT NULL CHECK (potential_winnings >= stake),
                status VARCHAR(7),
                admin_note VARCHAR,
                rejection_reason VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                result_updated_at TIMESTAMP,
                price FLOAT,
                current_analysis_id INTEGER,
                analysis_status VARCHAR DEFAULT 'pending',
                market_data JSONB,
                win_probability FLOAT,
                expected_odds FLOAT,
                valid_until TIMESTAMP,
                min_stake FLOAT,
                tags JSONB,
                marketplace_status VARCHAR DEFAULT 'draft',
                is_published BOOLEAN DEFAULT FALSE,
                category VARCHAR DEFAULT 'General'
            );

            CREATE TABLE IF NOT EXISTS activities (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                activity_type VARCHAR,
                description VARCHAR,
                activity_metadata JSONB,
                created_at TIMESTAMP,
                country VARCHAR,
                status VARCHAR
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount FLOAT NOT NULL,
                fee FLOAT NOT NULL,
                type VARCHAR NOT NULL,
                payment_method VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                payment_reference VARCHAR NOT NULL UNIQUE,
                betting_code_id INTEGER REFERENCES betting_codes(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                title VARCHAR NOT NULL,
                message VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                notification_data JSONB,
                read BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS payments (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                amount FLOAT NOT NULL,
                currency VARCHAR,
                reference VARCHAR,
                status VARCHAR,
                payment_method VARCHAR,
                payment_data JSONB,
                type VARCHAR DEFAULT 'registration',
                verified_by INTEGER,
                verified_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                phone VARCHAR
            );

            CREATE TABLE IF NOT EXISTS admins (
                id SERIAL PRIMARY KEY,
                email VARCHAR NOT NULL UNIQUE,
                hashed_password VARCHAR NOT NULL,
                full_name VARCHAR,
                country VARCHAR(10) NOT NULL,
                role VARCHAR(20),
                is_active BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                analysis_stats JSONB DEFAULT '{"total_analyzed": 0, "approved": 0, "rejected": 0, "pending": 0, "accuracy_rate": 0.0}',
                payment_stats JSONB DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS code_analyses (
                id SERIAL PRIMARY KEY,
                betting_code_id INTEGER NOT NULL REFERENCES betting_codes(id),
                analyst_id INTEGER NOT NULL REFERENCES admins(id),
                status VARCHAR(11),
                risk_level VARCHAR(6),
                confidence_score FLOAT,
                expert_analysis TEXT,
                ai_analysis JSONB,
                odds_validation JSONB,
                stake_validation JSONB,
                pattern_validation JSONB,
                recommended_price FLOAT,
                market_category VARCHAR,
                country VARCHAR(10) NOT NULL,
                bookmaker VARCHAR NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP,
                completed_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS analysis_comments (
                id SERIAL PRIMARY KEY,
                analysis_id INTEGER NOT NULL REFERENCES code_analyses(id),
                admin_id INTEGER NOT NULL REFERENCES admins(id),
                comment TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS code_views (
                id SERIAL PRIMARY KEY,
                code_id INTEGER NOT NULL REFERENCES betting_codes(id) ON DELETE CASCADE,
                viewer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );

            CREATE TABLE IF NOT EXISTS code_purchases (
                id SERIAL PRIMARY KEY,
                code_id INTEGER NOT NULL REFERENCES betting_codes(id) ON DELETE CASCADE,
                buyer_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                amount FLOAT NOT NULL,
                currency VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                purchased_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
            );

            CREATE TABLE IF NOT EXISTS code_ratings (
                id SERIAL PRIMARY KEY,
                code_id INTEGER NOT NULL REFERENCES betting_codes(id) ON DELETE CASCADE,
                rater_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
                rating FLOAT NOT NULL,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
                updated_at TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS payment_admin_activities (
                id SERIAL PRIMARY KEY,
                admin_id INTEGER NOT NULL REFERENCES admins(id),
                payment_id INTEGER NOT NULL REFERENCES payments(id),
                action VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                processing_time FLOAT,
                activity_metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                country VARCHAR(10) NOT NULL,
                note TEXT,
                payment_method VARCHAR,
                amount FLOAT,
                currency VARCHAR(3),
                user_id INTEGER NOT NULL REFERENCES users(id),
                user_balance_before FLOAT,
                user_balance_after FLOAT
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS ix_users_id ON users(id);
            CREATE INDEX IF NOT EXISTS ix_betting_codes_id ON betting_codes(id);
            CREATE INDEX IF NOT EXISTS ix_activities_activity_type ON activities(activity_type);
            CREATE INDEX IF NOT EXISTS ix_activities_id ON activities(id);
            CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions(id);
            CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications(id);
            CREATE INDEX IF NOT EXISTS ix_admins_id ON admins(id);
            CREATE INDEX IF NOT EXISTS ix_code_analyses_id ON code_analyses(id);
            CREATE INDEX IF NOT EXISTS ix_analysis_comments_id ON analysis_comments(id);
            CREATE INDEX IF NOT EXISTS ix_code_views_id ON code_views(id);
            CREATE INDEX IF NOT EXISTS ix_code_purchases_id ON code_purchases(id);
            CREATE INDEX IF NOT EXISTS ix_code_ratings_id ON code_ratings(id);
            CREATE INDEX IF NOT EXISTS idx_code_views_code_id ON code_views(code_id);
            CREATE INDEX IF NOT EXISTS idx_code_purchases_code_id ON code_purchases(code_id);
            CREATE INDEX IF NOT EXISTS idx_code_ratings_code_id ON code_ratings(code_id);
            CREATE INDEX IF NOT EXISTS ix_payment_admin_activities_id ON payment_admin_activities(id);
        """))
        
        conn.commit()

if __name__ == "__main__":
    setup_admin_db() 