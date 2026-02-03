#!/usr/bin/env python3
"""
Seed script to populate the database with sample data for development.

Usage:
    python scripts/seed_data.py

Requires DATABASE_URL environment variable or uses default local connection.
"""

import asyncio
import os
import sys
from decimal import Decimal
from uuid import uuid4

# Add paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# We need to import after path setup
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://newsroom_user:changeme_in_production@localhost:5432/elastic_newsroom"
)


async def create_users(session: AsyncSession):
    """Create sample users."""
    from shared.auth import hash_password

    # Import models dynamically to handle path issues
    from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, Text, Enum, text
    from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY, JSONB
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass

    # Define minimal models for seeding
    from sqlalchemy.orm import Mapped, mapped_column

    users_data = [
        {
            "id": uuid4(),
            "email": "alice@freelancer.com",
            "password_hash": hash_password("password123"),
            "role": "freelancer",
            "status": "active",
            "email_verified": True,
            "display_name": "Alice Chen",
            "bio": "Investigative journalist specializing in tech and finance. 10+ years of experience at major publications.",
            "home_city": "San Francisco",
            "home_state": "CA",
            "home_country": "US",
            "primary_beats": ["tech", "finance", "startups"],
            "secondary_beats": ["business", "economics"],
            "per_word_rate": Decimal("0.75"),
            "hourly_rate_min": Decimal("75.00"),
            "hourly_rate_max": Decimal("125.00"),
            "day_rate": Decimal("600.00"),
            "trust_score": Decimal("0.88"),
            "quality_score": Decimal("0.92"),
            "reliability_score": Decimal("0.85"),
        },
        {
            "id": uuid4(),
            "email": "bob@freelancer.com",
            "password_hash": hash_password("password123"),
            "role": "freelancer",
            "status": "active",
            "email_verified": True,
            "display_name": "Bob Martinez",
            "bio": "Political correspondent covering Washington DC. Former White House reporter.",
            "home_city": "Washington",
            "home_state": "DC",
            "home_country": "US",
            "primary_beats": ["politics", "government", "policy"],
            "secondary_beats": ["legal", "defense"],
            "per_word_rate": Decimal("1.00"),
            "hourly_rate_min": Decimal("100.00"),
            "hourly_rate_max": Decimal("175.00"),
            "day_rate": Decimal("800.00"),
            "trust_score": Decimal("0.95"),
            "quality_score": Decimal("0.97"),
            "reliability_score": Decimal("0.93"),
        },
        {
            "id": uuid4(),
            "email": "carol@freelancer.com",
            "password_hash": hash_password("password123"),
            "role": "freelancer",
            "status": "active",
            "email_verified": True,
            "display_name": "Carol Williams",
            "bio": "Health and science journalist. Medical degree background.",
            "home_city": "Boston",
            "home_state": "MA",
            "home_country": "US",
            "primary_beats": ["health", "science", "medicine"],
            "secondary_beats": ["tech", "research"],
            "per_word_rate": Decimal("0.65"),
            "hourly_rate_min": Decimal("60.00"),
            "hourly_rate_max": Decimal("100.00"),
            "day_rate": Decimal("500.00"),
            "trust_score": Decimal("0.82"),
            "quality_score": Decimal("0.88"),
            "reliability_score": Decimal("0.80"),
        },
        {
            "id": uuid4(),
            "email": "david@freelancer.com",
            "password_hash": hash_password("password123"),
            "role": "freelancer",
            "status": "active",
            "email_verified": True,
            "display_name": "David Park",
            "bio": "Local government reporter covering city politics and housing issues.",
            "home_city": "Los Angeles",
            "home_state": "CA",
            "home_country": "US",
            "primary_beats": ["local_government", "housing", "urban_planning"],
            "secondary_beats": ["politics", "real_estate"],
            "per_word_rate": Decimal("0.55"),
            "hourly_rate_min": Decimal("50.00"),
            "hourly_rate_max": Decimal("85.00"),
            "day_rate": Decimal("400.00"),
            "trust_score": Decimal("0.75"),
            "quality_score": Decimal("0.78"),
            "reliability_score": Decimal("0.82"),
        },
        {
            "id": uuid4(),
            "email": "editor@newsroom.com",
            "password_hash": hash_password("password123"),
            "role": "editor",
            "status": "active",
            "email_verified": True,
            "display_name": "Emma Thompson",
            "title": "Managing Editor",
        },
        {
            "id": uuid4(),
            "email": "senior.editor@newsroom.com",
            "password_hash": hash_password("password123"),
            "role": "editor",
            "status": "active",
            "email_verified": True,
            "display_name": "Frank Rodriguez",
            "title": "Senior Editor",
        },
    ]

    # Execute raw SQL for seeding
    for user in users_data:
        if user["role"] == "freelancer":
            await session.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, role, status, email_verified, created_at, updated_at)
                    VALUES (:id, :email, :password_hash, :role, :status, :email_verified, NOW(), NOW())
                    ON CONFLICT (email) DO NOTHING
                """),
                {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "password_hash": user["password_hash"],
                    "role": user["role"],
                    "status": user["status"],
                    "email_verified": user["email_verified"],
                }
            )

            await session.execute(
                text("""
                    INSERT INTO freelancer_profiles (
                        id, user_id, display_name, bio, home_city, home_state, home_country,
                        primary_beats, secondary_beats, per_word_rate, hourly_rate_min, hourly_rate_max,
                        day_rate, trust_score, quality_score, reliability_score,
                        availability_status, weekly_capacity_hours, willing_to_travel_miles,
                        identity_verified, portfolio_verified, created_at, updated_at
                    )
                    VALUES (
                        gen_random_uuid(), :user_id, :display_name, :bio, :home_city, :home_state, :home_country,
                        :primary_beats, :secondary_beats, :per_word_rate, :hourly_rate_min, :hourly_rate_max,
                        :day_rate, :trust_score, :quality_score, :reliability_score,
                        'available', 40, 50, true, true, NOW(), NOW()
                    )
                    ON CONFLICT DO NOTHING
                """),
                {
                    "user_id": str(user["id"]),
                    "display_name": user["display_name"],
                    "bio": user["bio"],
                    "home_city": user["home_city"],
                    "home_state": user["home_state"],
                    "home_country": user["home_country"],
                    "primary_beats": user["primary_beats"],
                    "secondary_beats": user["secondary_beats"],
                    "per_word_rate": user["per_word_rate"],
                    "hourly_rate_min": user["hourly_rate_min"],
                    "hourly_rate_max": user["hourly_rate_max"],
                    "day_rate": user["day_rate"],
                    "trust_score": user["trust_score"],
                    "quality_score": user["quality_score"],
                    "reliability_score": user["reliability_score"],
                }
            )
        else:
            # Editor
            await session.execute(
                text("""
                    INSERT INTO users (id, email, password_hash, role, status, email_verified, created_at, updated_at)
                    VALUES (:id, :email, :password_hash, :role, :status, :email_verified, NOW(), NOW())
                    ON CONFLICT (email) DO NOTHING
                """),
                {
                    "id": str(user["id"]),
                    "email": user["email"],
                    "password_hash": user["password_hash"],
                    "role": user["role"],
                    "status": user["status"],
                    "email_verified": user["email_verified"],
                }
            )

            await session.execute(
                text("""
                    INSERT INTO editor_profiles (id, user_id, display_name, title, created_at, updated_at)
                    VALUES (gen_random_uuid(), :user_id, :display_name, :title, NOW(), NOW())
                    ON CONFLICT DO NOTHING
                """),
                {
                    "user_id": str(user["id"]),
                    "display_name": user["display_name"],
                    "title": user.get("title", "Editor"),
                }
            )

    print(f"Created {len(users_data)} sample users")


async def create_newsrooms(session: AsyncSession):
    """Create sample newsrooms."""
    from sqlalchemy import text

    newsrooms_data = [
        {
            "name": "Tech Daily",
            "slug": "tech-daily",
            "domain": "techdaily.com",
            "cms_type": "wordpress",
            "payment_terms_days": 30,
        },
        {
            "name": "The Political Report",
            "slug": "political-report",
            "domain": "politicalreport.com",
            "cms_type": "ghost",
            "payment_terms_days": 15,
        },
        {
            "name": "Health Insider",
            "slug": "health-insider",
            "domain": "healthinsider.com",
            "cms_type": "wordpress",
            "payment_terms_days": 30,
        },
    ]

    for newsroom in newsrooms_data:
        await session.execute(
            text("""
                INSERT INTO newsrooms (id, name, slug, domain, cms_type, payment_terms_days, status, created_at, updated_at)
                VALUES (gen_random_uuid(), :name, :slug, :domain, :cms_type, :payment_terms_days, 'active', NOW(), NOW())
                ON CONFLICT (slug) DO NOTHING
            """),
            newsroom
        )

    print(f"Created {len(newsrooms_data)} sample newsrooms")


async def main():
    """Main seed function."""
    print(f"Connecting to database: {DATABASE_URL[:50]}...")

    engine = create_async_engine(DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            await create_users(session)
            await create_newsrooms(session)
            await session.commit()
            print("\nSeed data created successfully!")
            print("\nSample login credentials:")
            print("  Freelancer: alice@freelancer.com / password123")
            print("  Freelancer: bob@freelancer.com / password123")
            print("  Editor: editor@newsroom.com / password123")
        except Exception as e:
            await session.rollback()
            print(f"Error seeding data: {e}")
            raise

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
