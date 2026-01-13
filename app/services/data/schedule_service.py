from datetime import datetime, date
from sqlalchemy.orm import joinedload
from app.models.schedule import TimeSlot, WeeklySchedule
from app.models.class_subject import ClassSubject
from app.models.class_ import Class
from app.models.course import Course
from app.models.lesson import Lesson
from .base_service import BaseDataService

class ScheduleService(BaseDataService):
    def create_time_slot(self, day_of_week: int, period_index: int, start_time: str, end_time: str) -> dict | None:
        try:
             start = datetime.strptime(start_time, "%H:%M").time()
             end = datetime.strptime(end_time, "%H:%M").time()
        except ValueError:
             raise ValueError("Horários devem estar no formato HH:MM.")

        with self._get_db() as db:
            existing = db.query(TimeSlot).filter(
                TimeSlot.day_of_week == day_of_week,
                TimeSlot.period_index == period_index
            ).first()

            if existing:
                raise ValueError("Já existe um período configurado para este dia com este índice.")

            new_slot = TimeSlot(
                day_of_week=day_of_week,
                period_index=period_index,
                start_time=start,
                end_time=end
            )
            db.add(new_slot)
            db.flush()
            db.refresh(new_slot)
            return {
                "id": new_slot.id,
                "day_of_week": new_slot.day_of_week,
                "period_index": new_slot.period_index,
                "start_time": new_slot.start_time.strftime("%H:%M"),
                "end_time": new_slot.end_time.strftime("%H:%M")
            }

    def get_time_slots(self, day_of_week: int = None) -> list[dict]:
        with self._get_db() as db:
            query = db.query(TimeSlot)
            if day_of_week is not None:
                query = query.filter(TimeSlot.day_of_week == day_of_week)

            slots = query.order_by(TimeSlot.day_of_week, TimeSlot.period_index).all()

            return [{
                "id": s.id,
                "day_of_week": s.day_of_week,
                "period_index": s.period_index,
                "start_time": s.start_time.strftime("%H:%M"),
                "end_time": s.end_time.strftime("%H:%M")
            } for s in slots]

    def delete_time_slot(self, slot_id: int):
        with self._get_db() as db:
            db.query(WeeklySchedule).filter(WeeklySchedule.time_slot_id == slot_id).delete()
            db.query(TimeSlot).filter(TimeSlot.id == slot_id).delete()

    def create_schedule_assignment(self, time_slot_id: int, class_subject_id: int) -> dict | None:
        with self._get_db() as db:
            existing = db.query(WeeklySchedule).filter(WeeklySchedule.time_slot_id == time_slot_id).first()
            if existing:
                db.delete(existing)
                db.flush()

            assignment = WeeklySchedule(time_slot_id=time_slot_id, class_subject_id=class_subject_id)
            db.add(assignment)
            db.flush()
            db.refresh(assignment)
            return {"id": assignment.id}

    def get_full_schedule_grid(self) -> dict:
        with self._get_db() as db:
            results = (db.query(
                            TimeSlot.id, TimeSlot.day_of_week, TimeSlot.period_index, TimeSlot.start_time, TimeSlot.end_time,
                            WeeklySchedule.id.label('schedule_id'),
                            ClassSubject.id.label('subject_id'),
                            Class.id.label('class_id'), Class.name.label('class_name'),
                            Course.course_name
                       )
                       .outerjoin(WeeklySchedule, TimeSlot.id == WeeklySchedule.time_slot_id)
                       .outerjoin(ClassSubject, WeeklySchedule.class_subject_id == ClassSubject.id)
                       .outerjoin(Class, ClassSubject.class_id == Class.id)
                       .outerjoin(Course, ClassSubject.course_id == Course.id)
                       .order_by(TimeSlot.day_of_week, TimeSlot.period_index)
                       .all())

            grid = {}
            for row in results:
                day = row.day_of_week
                if day not in grid:
                    grid[day] = []

                item = {
                    "slot_id": row.id,
                    "period_index": row.period_index,
                    "start_time": row.start_time.strftime("%H:%M"),
                    "end_time": row.end_time.strftime("%H:%M"),
                    "assignment": None
                }

                if row.schedule_id and row.class_id and row.course_name:
                    item["assignment"] = {
                        "class_id": row.class_id,
                        "class_name": row.class_name,
                        "course_name": row.course_name,
                        "class_subject_id": row.subject_id
                    }

                grid[day].append(item)

            return grid

    def get_lesson_for_schedule(self, class_subject_id: int, date_val: date) -> dict | None:
        with self._get_db() as db:
            lesson = db.query(Lesson).filter(
                Lesson.class_subject_id == class_subject_id,
                Lesson.date == date_val
            ).first()

            if lesson:
                return {"id": lesson.id, "title": lesson.title, "content": lesson.content, "date": lesson.date.isoformat(), "bncc_codes": lesson.bncc_codes}
            return None
