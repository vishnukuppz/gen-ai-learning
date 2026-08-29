from fastapi import FastAPI

# Initialize the FastAPI application
app = FastAPI()


class UserTable:
    def __init__(self, user_id, name, email):
        self.user_id = user_id
        self.name = name
        self.email = email

userDb = [
    UserTable(1, "Kuppusamy M", "kuppu@gmail.com"),
    UserTable(2, "Vishnu", "vishnu@gmail.com")
]

@app.get("/getUserDetails/{user_id}")
def get_user_details(user_id : int):
    for user in userDb:
        if user.user_id == user_id:
            return {"user_id": user.user_id, "name": user.name, "email": user.email}
    return {"error": "User not found"}

