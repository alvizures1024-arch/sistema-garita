from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from pydantic import BaseModel
from typing import Optional
import os, time

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY   = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM    = "HS256"

def get_engine(retries=5, delay=3):
    for i in range(retries):
        try:
            engine = create_engine(DATABASE_URL)
            engine.connect()
            return engine
        except Exception as e:
            print(f"DB no lista ({i+1}/{retries}): {e}")
            time.sleep(delay)
    raise Exception("No se pudo conectar a la DB")

engine       = get_engine()
SessionLocal = sessionmaker(bind=engine)
Base         = declarative_base()

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True)
    username      = Column(String(50), unique=True)
    email         = Column(String(100), unique=True)
    password_hash = Column(String(255))
    created_at    = Column(DateTime, default=datetime.utcnow)
    is_active     = Column(Boolean, default=True)

class Registro(Base):
    __tablename__ = "registros"
    id        = Column(Integer, primary_key=True)
    placa     = Column(String(20), nullable=False)
    tipo      = Column(String(10), nullable=False)
    conductor = Column(String(100), nullable=False)
    motivo    = Column(String(200), nullable=False)
    usuario   = Column(String(50), nullable=False)
    fecha     = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)

def crear_token(username: str):
    expire = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario(token: str, db: Session):
    try:
        payload  = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user     = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(401, "Token inválido")
        return user
    except JWTError:
        raise HTTPException(401, "Token inválido")

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

class RegistroRequest(BaseModel):
    placa:     str
    tipo:      str
    conductor: str
    motivo:    str
    token:     str

class RegistroUpdateRequest(BaseModel):
    placa:     str
    tipo:      str
    conductor: str
    motivo:    str
    token:     str

app = FastAPI(title="Sistema de Garita")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", status_code=201)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Usuario ya existe")
    user = User(username=req.username, email=req.email,
                password_hash=pwd_context.hash(req.password))
    db.add(user)
    db.commit()
    return {"message": "Usuario creado"}

@app.post("/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not pwd_context.verify(req.password, user.password_hash):
        raise HTTPException(401, "Credenciales incorrectas")
    return {"access_token": crear_token(user.username), "username": user.username}

@app.post("/registros", status_code=201)
def crear_registro(req: RegistroRequest, db: Session = Depends(get_db)):
    user = obtener_usuario(req.token, db)
    if req.tipo not in ("entrada", "salida"):
        raise HTTPException(400, "Tipo debe ser entrada o salida")
    r = Registro(
        placa=req.placa.upper().strip(),
        tipo=req.tipo,
        conductor=req.conductor.strip(),
        motivo=req.motivo.strip(),
        usuario=user.username
    )
    db.add(r)
    db.commit()
    db.refresh(r)
    return {"id": r.id, "message": "Registro guardado"}

@app.get("/registros")
def listar_registros(token: str, fecha: Optional[str] = None, db: Session = Depends(get_db)):
    obtener_usuario(token, db)
    q = db.query(Registro)
    if fecha:
        try:
            dia = datetime.strptime(fecha, "%Y-%m-%d")
            q   = q.filter(Registro.fecha >= dia,
                           Registro.fecha < dia + timedelta(days=1))
        except ValueError:
            raise HTTPException(400, "Formato de fecha inválido, usa YYYY-MM-DD")
    registros = q.order_by(Registro.fecha.desc()).all()
    return [
        {
            "id":        r.id,
            "placa":     r.placa,
            "tipo":      r.tipo,
            "conductor": r.conductor,
            "motivo":    r.motivo,
            "usuario":   r.usuario,
            "fecha":     r.fecha.strftime("%d/%m/%Y %H:%M")
        }
        for r in registros
    ]

@app.get("/registros/stats")
def stats_hoy(token: str, db: Session = Depends(get_db)):
    obtener_usuario(token, db)
    hoy      = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    entradas = db.query(Registro).filter(Registro.fecha >= hoy, Registro.tipo == "entrada").count()
    salidas  = db.query(Registro).filter(Registro.fecha >= hoy, Registro.tipo == "salida").count()
    total    = db.query(Registro).filter(Registro.fecha >= hoy).count()
    return {"entradas": entradas, "salidas": salidas, "total": total}

@app.put("/registros/{id}")
def actualizar_registro(id: int, req: RegistroUpdateRequest, db: Session = Depends(get_db)):
    obtener_usuario(req.token, db)
    r = db.query(Registro).filter(Registro.id == id).first()
    if not r:
        raise HTTPException(404, "Registro no encontrado")
    r.placa     = req.placa.upper().strip()
    r.tipo      = req.tipo
    r.conductor = req.conductor.strip()
    r.motivo    = req.motivo.strip()
    db.commit()
    db.refresh(r)
    return {"id": r.id, "message": "Registro actualizado"}

@app.delete("/registros/{id}")
def eliminar_registro(id: int, token: str, db: Session = Depends(get_db)):
    obtener_usuario(token, db)
    r = db.query(Registro).filter(Registro.id == id).first()
    if not r:
        raise HTTPException(404, "Registro no encontrado")
    db.delete(r)
    db.commit()
    return {"message": "Registro eliminado"}
