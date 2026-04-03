@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserRegister, db: Session = Depends(get_db)):

    # ---------------------------------------------------
    # 🔍 Check if user already exists (OUTSIDE try block)
    # ---------------------------------------------------
    existing_user = db.query(User).filter(User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # ---------------------------------------------------
        # 🧱 Create user
        # ---------------------------------------------------
        user = User(
            email=payload.email,
            hashed_password=hash_password(payload.password),
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # ---------------------------------------------------
        # ✅ Safe return (Pydantic v2)
        # ---------------------------------------------------
        return UserOut.model_validate(user)

    # ---------------------------------------------------
    # 🔁 Handle DB uniqueness race condition
    # ---------------------------------------------------
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # ---------------------------------------------------
    # 💥 Unexpected errors (FULL DEBUG MODE)
    # ---------------------------------------------------
    except Exception as e:
        db.rollback()

        print("\n🔥 REGISTER ERROR START")
        traceback.print_exc()
        print("🔥 REGISTER ERROR END\n")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )