from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.src.database import SessionLocal
from backend.src.db_models import UserTable, SkinTable, Marketplace
from backend.src.utils.validation_utils import hash_password
import random

FLOATS = ["Factory New", "Minimal Wear", "Field-Tested", "Well Worn", "Battle-Scarred"]

SKIN_TYPES = {
    "Bayonet Slaugther": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLzn4_v8ydP0POjV75oIuKSMWuZxuZi_uU7HyjhwUh-tm_Xydmuc3nGbwN2ApAmQeNfsUXtktOzYuLm5FPajN9bjXKpLQ8HVlE/280x210",
    "Bayonet Lore": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyLzn4_v8ydP0PG7V6ZsOf-dC3OvzeFktd5kSi26gBBp5D-AzNaqIHLBa1MpWcMjR-AI4EOxkt2xYuvk5Q2L2tkTnHqt3SlK5zErvbhU-sE7AQ/280x210",
    "Butterfly Doppler": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Z-ua6bbZrLOmsD2qvxeFmoO1sXRajnRw0tmy6lob-KT-JOgRzAsZ3RuNfs0a5x9HhYuLj4gbbg99NySr6iy4d6C9t4r0EUqF0qLqX0V8wFp5G5A/280x210",
    "Karambit Emerald": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1Q7uCvZaZkNM-SA1iVzOtkse1tcCSyhx8rtjSfn4vGLSLANkI-X8MjTLFYskTsw9bnZOuwsgSIj4sTniz-2i5A7yY6tbwGV6Nx-qGEjxaBb-MuPavopw/280x210",
    "Skeleton Fade": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1I5PeibbBiLs-SD1iWwOpzj-1gSCGn20kjt2-En9mpcCmQag8hXsciQeJYthW9kILkMLji4g3Ygo8Uznj6jX9XrnE8raC5r1M/280x210",
    "Talon Fade": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGIGz3UqlXOLrxM-vMGmW8VNxu5Dx60noTyL6kJ_m-B1M5vahf6lsK_WBMWaR_uh3tORWQyC0nQlpsmXcnNaoeHuTZwUiWMZzRrVZsxm9x9ThNrzj4QCPjdhNmHj73S9KujErvbhX2ACGeQ"
}

def seed():
    db: Session = SessionLocal()

    print(">> Creating USERS...")
    users = []
    for i in range(2):
        email = f"user{i+1}@gmail.com"
        user = db.query(UserTable).filter_by(email=email).first()
        if not user:
            user = UserTable(
                name=f"user{i+1}",
                email=email,
                password=hash_password("1234"),
                role="player",
                funds=1000
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        users.append(user)

    print(">> Creating SKINS...")
    created_skins = []
    for user in users:
        chosen_types = random.sample(list(SKIN_TYPES.keys()), 5)

        for _ in range(50):
            skin_type = random.choice(chosen_types)
            float_value = random.choice(FLOATS)

            # Verificar se skin já existe para este usuário
            skin_exists = db.query(SkinTable).filter_by(
                name=skin_type.split()[1],
                type=skin_type.split()[0],
                owner_id=user.id
            ).first()
            if skin_exists:
                continue

            skin = SkinTable(
                name=skin_type.split()[1],
                type=skin_type.split()[0],
                float_value=float_value,
                owner_id=user.id,
                link=SKIN_TYPES[skin_type]
            )
            db.add(skin)
            db.commit()
            db.refresh(skin)
            created_skins.append(skin)

    print(">> Adding 20 skins to marketplace...")
    existing_marketplace_skin_ids = {m.skin_id for m in db.query(Marketplace).all()}
    num_to_pick = min(20, len(created_skins))
    picked = [sk for sk in random.sample(created_skins, num_to_pick) if sk.id not in existing_marketplace_skin_ids]

    for sk in picked:
        m = Marketplace(
            skin_id=sk.id,
            value=round(random.uniform(50, 1000), 2)
        )
        db.add(m)
        db.commit()

    print(">> DONE SEEDING!")

if __name__ == "__main__":
    seed()
