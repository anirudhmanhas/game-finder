import random
from database import SessionLocal
from models import Game

# TODO: In the future, replace this placeholder generation logic with real data
# from external APIs like IGDB (https://api.igdb.com/) or RAWG (https://rawg.io/apidocs)

ADJECTIVES = ["Epic", "Dark", "Super", "Neon", "Cyber", "Magic", "Lost", "Final", "Space", "Ancient"]
NOUNS = ["Quest", "Knight", "City", "Legends", "Echo", "Frontier", "Kingdom", "Odyssey", "Origins", "Reborn"]
GENRES = ["RPG", "Action", "Puzzle", "Strategy", "Shooter", "Platformer", "Simulation", "Sports", "Racing", "Adventure"]
PLATFORMS = ["PC", "PS5", "PS4", "Xbox Series X", "Nintendo Switch", "Mobile", "Web"]
TAGS = ["Multiplayer", "Co-op", "Singleplayer", "Roguelike", "Open World", "Pixel Art", "Story Rich", "Difficult", "Relaxing"]

def generate_random_game():
    title = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}"
    num_genres = random.randint(1, 3)
    num_platforms = random.randint(1, 4)
    num_tags = random.randint(2, 5)
    
    return Game(
        title=title,
        description=f"An amazing {title.lower()} experience where players explore uncharted territories.",
        genres=random.sample(GENRES, num_genres),
        platforms=random.sample(PLATFORMS, num_platforms),
        tags=random.sample(TAGS, num_tags),
        release_year=random.randint(2010, 2026),
        source="seed_script",
        external_url="https://example.com"
    )

def seed_database():
    db = SessionLocal()
    try:
        # Check if we already have games
        if db.query(Game).count() > 0:
            print("Database already seeded with games.")
            return

        print("Seeding database with 200 diverse sample games...")
        games_to_insert = [generate_random_game() for _ in range(200)]
        db.bulk_save_objects(games_to_insert)
        db.commit()
        print("Successfully seeded 200 games!")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
