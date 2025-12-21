from app.auth.auth import create_user

if __name__ == "__main__":
    username = input("Username: ").strip()
    password = input("Password: ").strip()

    user = create_user(username, password)
    print(f"✅ User created: {user.username} (ID: {user.id})")
