from uuid import uuid4
import json
from fastapi import (
    FastAPI,
    WebSocket,
    WebSocketDisconnect,
    Request,
    Depends,
    HTTPException,
)
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from models import Base, User
from database import engine, SessionLocal
from schemas import UserSchema
from sqlalchemy.orm import Session
from web_socket import ConnectionManager

Base.metadata.create_all(bind=engine)

app = FastAPI()
# Specify the directory for templates
templates = Jinja2Templates(directory="templates")

manager = ConnectionManager()


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/chats", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("client.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(request: Request, db: Session = Depends(get_db)) -> UserSchema:
    """
    Register a new user
    """
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    confirm_password = form_data.get("confirmPassword")

    # Validate passwords match
    if password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match.")

    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists.")

    # Generate a unique ID
    user_id = str(uuid4())  # Convert UUID to string

    # Create user schema
    UserSchema(id=user_id, email=email, password=password)

    # Create new user model instance
    new_user = User(id=user_id, email=email, password=password)  # Explicitly set the ID

    # Add and commit to database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    response = RedirectResponse(url="/chats", status_code=303)
    response.set_cookie(
        key="user_id",
        value=new_user.id,
        max_age=24 * 3600,  # expires in 60 seconds
    )

    return response


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    client_id = user_id
    try:
        await manager.connect(websocket, client_id)
        while True:
            data = await websocket.receive_text()
            _data = json.loads(data)
            message_type = _data.get("type")
            if message_type == "broadcast":
                await manager.broadcast(_data.get("message"), _data.get("sender"))
            await manager.send_personal_message(
                _data.get("message"), client_id, _data.get("recipient")
            )
    except WebSocketDisconnect:
        await manager.disconnect(client_id)
