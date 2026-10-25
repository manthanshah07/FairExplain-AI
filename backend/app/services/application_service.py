"""
FairExplain AI — Application Service
======================================
Business service orchestrating application creation, updates, and profile assembly.
"""

from __future__ import annotations

import uuid
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.academic_record import AcademicRecord
from app.models.application import Application, ApplicationStatus
from app.models.financial_profile import FinancialProfile
from app.models.user import User, UserRole
from app.repositories.application_repository import ApplicationRepository
from app.schemas.application import (
    AcademicRecordInput,
    ApplicationCreateRequest,
    ApplicationResponseData,
    FinancialProfileInput,
)


class ApplicationService:
    """Service handling application workflows and profile storage."""

    @staticmethod
    async def create_application(
        req: ApplicationCreateRequest,
        db: AsyncSession,
        current_user: User | None = None,
    ) -> ApplicationResponseData:
        """Create user (if needed), application, academic record, and financial profile."""
        app_repo = ApplicationRepository(db)

        # 1. Resolve or create user
        user: User | None = current_user
        if not user and req.user_id:
            res = await db.execute(select(User).where(User.id == req.user_id))
            user = res.scalar_one_or_none()

        if not user:
            # Check by email
            res = await db.execute(select(User).where(User.email.ilike(req.email.strip())))
            user = res.scalar_one_or_none()

        if not user:
            # Generate secure random password for non-authenticated intake
            secure_random_pwd = uuid.uuid4().hex + uuid.uuid4().hex
            user = User(
                name=req.name.strip(),
                email=req.email.strip().lower(),
                hashed_password=hash_password(secure_random_pwd),
                role=UserRole.student,
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.flush()

        # 2. Create Application
        application = await app_repo.create_application(
            user_id=user.id, status=ApplicationStatus.submitted
        )

        # 3. Create AcademicRecord
        acad = AcademicRecord(
            application_id=application.id,
            cgpa=req.academic_record.cgpa,
            tenth_percent=req.academic_record.tenth_percent,
            twelfth_percent=req.academic_record.twelfth_percent,
            backlogs=req.academic_record.backlogs,
        )
        db.add(acad)

        # 4. Create FinancialProfile
        fin = FinancialProfile(
            application_id=application.id,
            household_income=req.financial_profile.household_income,
            existing_emi=req.financial_profile.existing_emi,
            tuition_fee=req.financial_profile.tuition_fee,
            requested_loan=req.financial_profile.requested_loan,
        )
        db.add(fin)

        await db.commit()

        return ApplicationResponseData(
            application_id=application.id,
            user_id=user.id,
            status=application.status.value if hasattr(application.status, "value") else str(application.status),
            academic_record=req.academic_record,
            financial_profile=req.financial_profile,
            created_at=application.created_at,
        )

    @staticmethod
    async def get_application(
        application_id: uuid.UUID, db: AsyncSession
    ) -> ApplicationResponseData | None:
        """Retrieve application by ID with related academic and financial records."""
        app_repo = ApplicationRepository(db)
        app = await app_repo.get_with_relations(application_id)
        if not app:
            return None

        acad_dto = None
        if app.academic_record:
            acad_dto = AcademicRecordInput(
                cgpa=app.academic_record.cgpa,
                tenth_percent=app.academic_record.tenth_percent,
                twelfth_percent=app.academic_record.twelfth_percent,
                backlogs=app.academic_record.backlogs,
            )

        fin_dto = None
        if app.financial_profile:
            fin_dto = FinancialProfileInput(
                household_income=app.financial_profile.household_income,
                existing_emi=app.financial_profile.existing_emi,
                tuition_fee=app.financial_profile.tuition_fee,
                requested_loan=app.financial_profile.requested_loan,
            )

        return ApplicationResponseData(
            application_id=app.id,
            user_id=app.user_id,
            status=app.status.value if hasattr(app.status, "value") else str(app.status),
            academic_record=acad_dto,
            financial_profile=fin_dto,
            created_at=app.created_at,
        )
