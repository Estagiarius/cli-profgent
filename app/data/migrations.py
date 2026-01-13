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
from sqlalchemy import text, inspect
import logging

def migrate_database(engine):
    """
    Checks for necessary schema migrations and applies them.
    Currently handles:
    1. Adding 'grading_period' to the 'assessments' table.
    2. Adding performance indexes to the 'grades' table.
    3. Adding performance indexes to the 'incidents' table.
    4. Adding performance indexes to 'class_enrollments' and 'class_subjects'.
    5. Adding performance indexes to 'attendance', 'assessments', and 'lessons'.
    6. Adding BNCC columns to 'courses', 'lessons', and 'assessments'.
    """
    try:
        inspector = inspect(engine)
        # --- 1. Migration for 'grading_period' in 'assessments' ---
        columns_assessments = [col['name'] for col in inspector.get_columns('assessments')]

        # --- 1. Migration for 'grading_period' in 'assessments' ---
        columns_assessments = [col['name'] for col in inspector.get_columns('assessments')]

        if 'grading_period' not in columns_assessments:
            logging.info("Applying migration: Adding 'grading_period' column to 'assessments' table.")
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE assessments ADD COLUMN grading_period INTEGER DEFAULT 1 NOT NULL"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'grading_period' column already exists.")

        # --- BNCC Migrations ---

        # 1. Course: bncc_expected
        columns_courses = [col['name'] for col in inspector.get_columns('courses')]
        if 'bncc_expected' not in columns_courses:
            logging.info("Applying migration: Adding 'bncc_expected' column to 'courses' table.")
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE courses ADD COLUMN bncc_expected TEXT"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'bncc_expected' column already exists.")

        # 2. Lesson: bncc_codes
        columns_lessons = [col['name'] for col in inspector.get_columns('lessons')]
        if 'bncc_codes' not in columns_lessons:
            logging.info("Applying migration: Adding 'bncc_codes' column to 'lessons' table.")
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE lessons ADD COLUMN bncc_codes TEXT"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'bncc_codes' column already exists.")

        # 3. Assessment: bncc_codes (using existing columns_assessments list, but need to re-fetch if altered? No, local list.)
        # Wait, if I alter table above (grading_period), inspector cache might be stale?
        # But here I check 'bncc_codes' in the list I fetched *before* potential alter.
        # If grading_period was added, it doesn't affect existence of bncc_codes check.
        # But if I add grading_period, and then check bncc_codes, safely separated.

        if 'bncc_codes' not in columns_assessments:
            logging.info("Applying migration: Adding 'bncc_codes' column to 'assessments' table.")
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE assessments ADD COLUMN bncc_codes TEXT"))
            logging.info("Migration applied successfully.")
        else:
            logging.info("Schema check: 'bncc_codes' column already exists.")
    except Exception as e:
        logging.error(f"Migration failed: {e}")
        raise e
