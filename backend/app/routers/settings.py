from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from app.database import get_db
from app.models import User, UserTopic, Section
from app.auth_deps import get_current_user

router = APIRouter(prefix="/user", tags=["settings"])

class SettingsUpdate(BaseModel):
    sections: List[int]  # list of section IDs
    topics: List[str]    # list of custom strings

@router.get("/settings")
def get_user_settings(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Read topics
    topics = [t.topic for t in db.query(UserTopic).filter(UserTopic.user_id == current_user.id).all()]
    # Read sections
    section_ids = [sec.id for sec in current_user.sections] if hasattr(current_user, 'sections') else []

    return {"sections": section_ids, "topics": topics}

@router.put("/settings")
def update_user_settings(
    settings: SettingsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Fetch the actual Section objects corresponding to the IDs sent by frontend
    new_sections = db.query(Section).filter(Section.id.in_(settings.sections)).all()

    # Update the user's sections directly
    current_user.sections = new_sections

    # Update custom topics: clear old ones and insert new ones
    db.query(UserTopic).filter(UserTopic.user_id == current_user.id).delete()
    for topic_name in settings.topics:
        new_topic = UserTopic(user_id=current_user.id, topic=topic_name)
        db.add(new_topic)

    db.commit()
    return {"message": "Settings updated successfully"}
