@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):

    hashed_password = get_password_hash(user.password)

    db_user = User(
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user