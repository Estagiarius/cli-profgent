# Author: Victor Hugo Garcia de Oliveira
# Date: 2025-12-21
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
# Este arquivo de código-fonte está sujeito aos termos da Mozilla Public
# License, v. 2.0. Se uma cópia da MPL não foi distribuída com este
# arquivo, você pode obter uma em https://mozilla.org/MPL/2.0/.
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.seating_chart import SeatingChart, SeatAssignment
from app.models.student import Student
from app.models.class_enrollment import ClassEnrollment
from contextlib import contextmanager
import json

class SeatingChartService:
    def __init__(self, db_session: Session = None):
        self._db_session = db_session

    @contextmanager
    def _get_db(self):
        if self._db_session:
            yield self._db_session
        else:
            from app.data.database import SessionLocal
            db = SessionLocal()
            try:
                yield db
                db.commit()
            except Exception:
                db.rollback()
                raise
            finally:
                db.close()

    def create_seating_chart(self, class_id: int, name: str, rows: int, cols: int, layout_config: str = "{}") -> SeatingChart:
        with self._get_db() as db:
            chart = SeatingChart(
                class_id=class_id,
                name=name,
                rows=rows,
                columns=cols,
                layout_config=layout_config
            )
            db.add(chart)
            db.flush()
            db.refresh(chart)
            return chart

    def get_seating_charts_for_class(self, class_id: int) -> list[dict]:
        with self._get_db() as db:
            charts = db.query(SeatingChart).filter(SeatingChart.class_id == class_id).all()
            return [{"id": c.id, "name": c.name, "rows": c.rows, "columns": c.columns, "created_at": c.created_at} for c in charts]

    def get_seating_chart_details(self, chart_id: int) -> dict | None:
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if not chart:
                return None

            # Join to get Call Number from ClassEnrollment
            # We assume assignments are valid only if student is enrolled in the chart's class?
            # Ideally yes, but let's just get the call number for the chart's class.

            assignments_query = (db.query(
                                    SeatAssignment,
                                    Student.first_name,
                                    Student.last_name,
                                    ClassEnrollment.call_number
                                )
                                .join(Student, SeatAssignment.student_id == Student.id)
                                .outerjoin(ClassEnrollment, (ClassEnrollment.student_id == Student.id) & (ClassEnrollment.class_id == chart.class_id))
                                .filter(SeatAssignment.chart_id == chart_id)
                                .all())

            assignments_data = []
            for a, fname, lname, call_num in assignments_query:
                assignments_data.append({
                    "id": a.id,
                    "student_id": a.student_id,
                    "student_name": f"{fname} {lname}",
                    "call_number": call_num, # May be None if not enrolled anymore
                    "row_index": a.row_index,
                    "col_index": a.col_index
                })

            return {
                "id": chart.id,
                "name": chart.name,
                "rows": chart.rows,
                "columns": chart.columns,
                "layout_config": chart.layout_config,
                "assignments": assignments_data
            }

    def update_seating_chart_layout(self, chart_id: int, layout_config: str):
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if chart:
                chart.layout_config = layout_config
                db.commit()

    def save_seat_assignments(self, chart_id: int, assignments: list[dict]):
        """
        Replaces all assignments for a chart with the new list.
        assignments: list of dicts {student_id, row_index, col_index}
        """
        with self._get_db() as db:
            # Clear existing
            db.query(SeatAssignment).filter(SeatAssignment.chart_id == chart_id).delete()

            # Add new
            new_assignments = [
                SeatAssignment(
                    chart_id=chart_id,
                    student_id=a['student_id'],
                    row_index=a['row_index'],
                    col_index=a['col_index']
                ) for a in assignments
            ]
            if new_assignments:
                db.bulk_save_objects(new_assignments)
            db.commit()

    def delete_seating_chart(self, chart_id: int):
        with self._get_db() as db:
            chart = db.query(SeatingChart).filter(SeatingChart.id == chart_id).first()
            if chart:
                db.delete(chart)
                db.commit()
