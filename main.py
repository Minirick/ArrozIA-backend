from src.database.database import Base, engine
from fastapi import FastAPI
from src.routes.userRouter import USER_ROUTES

Base.metadata.create_all(engine)    

app=FastAPI()

# Incluir las rutas
app.include_router(USER_ROUTES)



































































































# @app.post('/logout')
# def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
#     token=dependencies
#     payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
#     user_id = payload['sub']
#     token_record = db.query(models.TokenTable).all()
#     info=[]
#     for record in token_record :
#         print("record",record)
#         if (datetime.utcnow() - record.created_date).days >1:
#             info.append(record.user_id)
#     if info:
#         existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
#         db.commit()
        
#     existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_toke==token).first()
#     if existing_token:
#         existing_token.status=False
#         db.add(existing_token)
#         db.commit()
#         db.refresh(existing_token)
#     return {"message":"Logout Successfully"} 