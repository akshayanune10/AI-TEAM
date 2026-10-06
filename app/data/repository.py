"""
Data repository layer providing clean CRUD abstractions and domain conversions.
"""

import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from app.data.database import SessionLocal, init_db
from app.data.entities import (
    StudentEntity,
    SkillEntity,
    AvailabilityEntity,
    WorkStyleEntity,
    PreferenceEntity,
    ProjectEntity,
    RequirementEntity,
    GenerationRunEntity,
    TeamEntity,
    TeamMemberEntity,
    TeamConflictEntity,
    TeamExplanationEntity,
    TeamConstraintEntity,
    PeerFeedbackEntity,
)
from app.models.student import (
    Student,
    StudentCreate,
    StudentSkill,
    SkillCategory,
    SkillSource,
    TimeSlotAvailability,
    WorkStyle,
    StudentPreference,
)
from app.models.project import (
    Project,
    ProjectCreate,
    ProjectRequirement,
)
from app.models.team import (
    Team,
    TeamMemberAssignment,
    TeamScoreBreakdown,
    TeamConflict,
    ConflictSeverity,
    StudentExplanation,
    TeamExplanation,
    TeamConstraint,
    ConstraintType,
    GenerationRun,
)
from app.models.feedback import (
    PeerFeedback,
    PeerFeedbackCreate,
)


class DataRepository:
    """Manages database transactions and entity mapping."""

    def __init__(self, db_session: Optional[Session] = None):
        init_db()
        self._db = db_session

    @property
    def db(self) -> Session:
        if self._db is not None:
            return self._db
        return SessionLocal()

    # --- Student Operations ---

    def create_student(self, student_in: StudentCreate) -> Student:
        db = self.db
        try:
            student_ent = StudentEntity(
                student_id_str=student_in.student_id_str,
                name=student_in.name,
                email=student_in.email,
                department=student_in.department,
                academic_year=student_in.academic_year,
                experience_level=student_in.experience_level,
                gpa=student_in.gpa,
                bio=student_in.bio,
                resume_filename=student_in.resume_filename,
            )
            db.add(student_ent)
            db.flush()

            # Add Skills
            for sk in student_in.skills:
                sk_ent = SkillEntity(
                    student_id=student_ent.id,
                    name=sk.name,
                    category=sk.category.value if hasattr(sk.category, "value") else str(sk.category),
                    proficiency=sk.proficiency,
                    source=sk.source.value if hasattr(sk.source, "value") else str(sk.source),
                    confidence=sk.confidence,
                )
                db.add(sk_ent)

            # Add Availability
            for av in student_in.availability:
                av_ent = AvailabilityEntity(
                    student_id=student_ent.id,
                    day=av.day,
                    slot=av.slot,
                    is_available=av.is_available,
                )
                db.add(av_ent)

            # Add WorkStyle
            ws = student_in.work_style
            ws_ent = WorkStyleEntity(
                student_id=student_ent.id,
                primary_role=ws.primary_role,
                secondary_role=ws.secondary_role,
                collaboration_mode=ws.collaboration_mode,
                communication_preference=ws.communication_preference,
                leadership_inclination=ws.leadership_inclination,
                planning_orientation=ws.planning_orientation,
            )
            db.add(ws_ent)

            # Add Preferences
            for pref in student_in.preferences:
                pref_ent = PreferenceEntity(
                    student_id=student_ent.id,
                    project_id=pref.project_id,
                    rank=pref.rank,
                )
                db.add(pref_ent)

            db.commit()
            db.refresh(student_ent)
            return self._map_student(student_ent)
        except Exception:
            db.rollback()
            raise

    def get_all_students(self) -> List[Student]:
        db = self.db
        students = db.query(StudentEntity).order_by(StudentEntity.id.asc()).all()
        return [self._map_student(s) for s in students]

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        db = self.db
        student = db.query(StudentEntity).filter(StudentEntity.id == student_id).first()
        return self._map_student(student) if student else None

    def delete_student(self, student_id: int) -> bool:
        db = self.db
        try:
            ent = db.query(StudentEntity).filter(StudentEntity.id == student_id).first()
            if ent:
                db.delete(ent)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            raise

    def _map_student(self, ent: StudentEntity) -> Student:
        skills = [
            StudentSkill(
                name=s.name,
                category=SkillCategory(s.category),
                proficiency=s.proficiency,
                source=SkillSource(s.source),
                confidence=s.confidence,
            )
            for s in ent.skills
        ]
        availability = [
            TimeSlotAvailability(day=a.day, slot=a.slot, is_available=a.is_available)
            for a in ent.availabilities
        ]
        ws = ent.work_style
        work_style = (
            WorkStyle(
                primary_role=ws.primary_role,
                secondary_role=ws.secondary_role,
                collaboration_mode=ws.collaboration_mode,
                communication_preference=ws.communication_preference,
                leadership_inclination=ws.leadership_inclination,
                planning_orientation=ws.planning_orientation,
            )
            if ws
            else WorkStyle()
        )
        preferences = [
            StudentPreference(project_id=p.project_id, rank=p.rank)
            for p in ent.preferences
        ]

        return Student(
            id=ent.id,
            student_id_str=ent.student_id_str,
            name=ent.name,
            email=ent.email,
            department=ent.department,
            academic_year=ent.academic_year,
            experience_level=ent.experience_level,
            gpa=ent.gpa,
            bio=ent.bio or "",
            resume_filename=ent.resume_filename,
            skills=skills,
            preferences=preferences,
            availability=availability,
            work_style=work_style,
        )

    # --- Project Operations ---

    def create_project(self, project_in: ProjectCreate) -> Project:
        db = self.db
        try:
            proj_ent = ProjectEntity(
                title=project_in.title,
                description=project_in.description,
                domain=project_in.domain,
                target_team_size=project_in.target_team_size,
                min_team_size=project_in.min_team_size,
                max_team_size=project_in.max_team_size,
            )
            db.add(proj_ent)
            db.flush()

            for req in project_in.requirements:
                req_ent = RequirementEntity(
                    project_id=proj_ent.id,
                    skill_name=req.skill_name,
                    category=req.category.value if hasattr(req.category, "value") else str(req.category),
                    required_level=req.required_level,
                    importance_weight=req.importance_weight,
                    is_mandatory=req.is_mandatory,
                )
                db.add(req_ent)

            db.commit()
            db.refresh(proj_ent)
            return self._map_project(proj_ent)
        except Exception:
            db.rollback()
            raise

    def get_all_projects(self) -> List[Project]:
        db = self.db
        projects = db.query(ProjectEntity).order_by(ProjectEntity.id.asc()).all()
        return [self._map_project(p) for p in projects]

    def get_project_by_id(self, project_id: int) -> Optional[Project]:
        db = self.db
        p = db.query(ProjectEntity).filter(ProjectEntity.id == project_id).first()
        return self._map_project(p) if p else None

    def update_project_requirements(self, project_id: int, requirements: List[ProjectRequirement]) -> Optional[Project]:
        db = self.db
        try:
            proj = db.query(ProjectEntity).filter(ProjectEntity.id == project_id).first()
            if not proj:
                return None
            
            # Clear old requirements
            db.query(RequirementEntity).filter(RequirementEntity.project_id == project_id).delete()
            
            # Add updated requirements
            for req in requirements:
                req_ent = RequirementEntity(
                    project_id=project_id,
                    skill_name=req.skill_name,
                    category=req.category.value if hasattr(req.category, "value") else str(req.category),
                    required_level=req.required_level,
                    importance_weight=req.importance_weight,
                    is_mandatory=req.is_mandatory,
                )
                db.add(req_ent)

            db.commit()
            db.refresh(proj)
            return self._map_project(proj)
        except Exception:
            db.rollback()
            raise

    def delete_project(self, project_id: int) -> bool:
        db = self.db
        try:
            ent = db.query(ProjectEntity).filter(ProjectEntity.id == project_id).first()
            if ent:
                db.delete(ent)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            raise

    def _map_project(self, ent: ProjectEntity) -> Project:
        reqs = [
            ProjectRequirement(
                id=r.id,
                skill_name=r.skill_name,
                category=SkillCategory(r.category),
                required_level=r.required_level,
                importance_weight=r.importance_weight,
                is_mandatory=r.is_mandatory,
            )
            for r in ent.requirements
        ]
        return Project(
            id=ent.id,
            title=ent.title,
            description=ent.description,
            domain=ent.domain,
            target_team_size=ent.target_team_size,
            min_team_size=ent.min_team_size,
            max_team_size=ent.max_team_size,
            status=ent.status,
            requirements=reqs,
        )

    # --- Constraints Operations ---

    def add_constraint(self, constraint: TeamConstraint) -> TeamConstraint:
        db = self.db
        try:
            ent = TeamConstraintEntity(
                constraint_type=constraint.constraint_type.value,
                student_id_1=constraint.student_id_1,
                student_id_2=constraint.student_id_2,
                target_project_id=constraint.target_project_id,
                note=constraint.note,
            )
            db.add(ent)
            db.commit()
            db.refresh(ent)
            return TeamConstraint(
                id=ent.id,
                constraint_type=ConstraintType(ent.constraint_type),
                student_id_1=ent.student_id_1,
                student_id_2=ent.student_id_2,
                target_project_id=ent.target_project_id,
                note=ent.note,
            )
        except Exception:
            db.rollback()
            raise

    def get_all_constraints(self) -> List[TeamConstraint]:
        db = self.db
        ents = db.query(TeamConstraintEntity).all()
        return [
            TeamConstraint(
                id=e.id,
                constraint_type=ConstraintType(e.constraint_type),
                student_id_1=e.student_id_1,
                student_id_2=e.student_id_2,
                target_project_id=e.target_project_id,
                note=e.note,
            )
            for e in ents
        ]

    def delete_constraint(self, constraint_id: int) -> bool:
        db = self.db
        try:
            ent = db.query(TeamConstraintEntity).filter(TeamConstraintEntity.id == constraint_id).first()
            if ent:
                db.delete(ent)
                db.commit()
                return True
            return False
        except Exception:
            db.rollback()
            raise

    def clear_all_constraints(self):
        db = self.db
        db.query(TeamConstraintEntity).delete()
        db.commit()

    # --- Generation Run & Team Persistence ---

    def save_generation_run(self, run: GenerationRun) -> GenerationRun:
        db = self.db
        try:
            run_ent = GenerationRunEntity(
                algorithm=run.algorithm,
                weights_json=json.dumps(run.weights),
                average_score=run.average_score,
                fairness_std_dev=run.fairness_std_dev,
                runtime_ms=run.runtime_ms,
                is_finalized=run.is_finalized,
            )
            db.add(run_ent)
            db.flush()

            for team in run.teams:
                team_ent = TeamEntity(
                    run_id=run_ent.id,
                    project_id=team.project_id,
                    team_name=team.team_name,
                    score_json=team.score.model_dump_json(),
                    is_approved=team.is_approved,
                )
                db.add(team_ent)
                db.flush()

                # Add members
                for member in team.members:
                    mem_ent = TeamMemberEntity(
                        team_id=team_ent.id,
                        student_id=member.student_id,
                        is_locked=member.is_locked,
                        assigned_role=member.assigned_role,
                    )
                    db.add(mem_ent)

                # Add conflicts
                for conflict in team.conflicts:
                    conf_ent = TeamConflictEntity(
                        team_id=team_ent.id,
                        conflict_type=conflict.conflict_type,
                        severity=conflict.severity.value,
                        description=conflict.description,
                        repair_suggestion=conflict.repair_suggestion,
                    )
                    db.add(conf_ent)

                # Add explanation
                if team.explanation:
                    exp = team.explanation
                    exp_ent = TeamExplanationEntity(
                        team_id=team_ent.id,
                        summary=exp.summary,
                        strengths_json=json.dumps(exp.strengths),
                        tradeoffs_json=json.dumps(exp.tradeoffs),
                        student_explanations_json=json.dumps([s.model_dump() for s in exp.student_explanations]),
                    )
                    db.add(exp_ent)

            db.commit()
            db.refresh(run_ent)
            run.id = run_ent.id
            return run
        except Exception:
            db.rollback()
            raise

    def get_latest_generation_run(self) -> Optional[GenerationRun]:
        db = self.db
        run_ent = db.query(GenerationRunEntity).order_by(GenerationRunEntity.id.desc()).first()
        if not run_ent:
            return None
        return self._map_generation_run(run_ent)

    def _map_generation_run(self, ent: GenerationRunEntity) -> GenerationRun:
        teams = []
        for t_ent in ent.teams:
            score = TeamScoreBreakdown.model_validate_json(t_ent.score_json)
            members = [
                TeamMemberAssignment(
                    student_id=m.student_id,
                    student_name=m.student.name if m.student else f"Student #{m.student_id}",
                    student_id_str=m.student.student_id_str if m.student else f"ID-{m.student_id}",
                    is_locked=m.is_locked,
                    assigned_role=m.assigned_role,
                    experience_level=m.student.experience_level if m.student else 3,
                )
                for m in t_ent.members
            ]
            conflicts = [
                TeamConflict(
                    conflict_type=c.conflict_type,
                    severity=ConflictSeverity(c.severity),
                    description=c.description,
                    repair_suggestion=c.repair_suggestion,
                )
                for c in t_ent.conflicts
            ]

            explanation = None
            if t_ent.explanation:
                exp_ent = t_ent.explanation
                student_exps = [
                    StudentExplanation(**s_data)
                    for s_data in json.loads(exp_ent.student_explanations_json)
                ]
                explanation = TeamExplanation(
                    summary=exp_ent.summary,
                    strengths=json.loads(exp_ent.strengths_json),
                    tradeoffs=json.loads(exp_ent.tradeoffs_json),
                    student_explanations=student_exps,
                )

            teams.append(
                Team(
                    id=t_ent.id,
                    project_id=t_ent.project_id,
                    project_title=t_ent.project.title if t_ent.project else f"Project #{t_ent.project_id}",
                    team_name=t_ent.team_name,
                    members=members,
                    score=score,
                    conflicts=conflicts,
                    explanation=explanation,
                    is_approved=t_ent.is_approved,
                )
            )

        return GenerationRun(
            id=ent.id,
            timestamp=ent.timestamp.isoformat(),
            algorithm=ent.algorithm,
            weights=json.loads(ent.weights_json),
            teams=teams,
            average_score=ent.average_score,
            fairness_std_dev=ent.fairness_std_dev,
            runtime_ms=ent.runtime_ms,
            is_finalized=ent.is_finalized,
        )

    # --- Peer Feedback ---

    def create_peer_feedback(self, feedback_in: PeerFeedbackCreate) -> PeerFeedback:
        db = self.db
        try:
            ent = PeerFeedbackEntity(
                team_id=feedback_in.team_id,
                evaluator_student_id=feedback_in.evaluator_student_id,
                target_student_id=feedback_in.target_student_id,
                collaboration_rating=feedback_in.collaboration_rating,
                communication_rating=feedback_in.communication_rating,
                task_completion_rating=feedback_in.task_completion_rating,
                overall_satisfaction=feedback_in.overall_satisfaction,
                comments=feedback_in.comments,
            )
            db.add(ent)
            db.commit()
            db.refresh(ent)
            return PeerFeedback(
                id=ent.id,
                team_id=ent.team_id,
                evaluator_student_id=ent.evaluator_student_id,
                target_student_id=ent.target_student_id,
                collaboration_rating=ent.collaboration_rating,
                communication_rating=ent.communication_rating,
                task_completion_rating=ent.task_completion_rating,
                overall_satisfaction=ent.overall_satisfaction,
                comments=ent.comments or "",
                created_at=ent.created_at.isoformat(),
            )
        except Exception:
            db.rollback()
            raise

    def get_feedback_for_team(self, team_id: int) -> List[PeerFeedback]:
        db = self.db
        ents = db.query(PeerFeedbackEntity).filter(PeerFeedbackEntity.team_id == team_id).all()
        return [
            PeerFeedback(
                id=e.id,
                team_id=e.team_id,
                evaluator_student_id=e.evaluator_student_id,
                target_student_id=e.target_student_id,
                collaboration_rating=e.collaboration_rating,
                communication_rating=e.communication_rating,
                task_completion_rating=e.task_completion_rating,
                overall_satisfaction=e.overall_satisfaction,
                comments=e.comments or "",
                created_at=e.created_at.isoformat(),
            )
            for e in ents
        ]

    def clear_database(self):
        """Clears all records for clean testing or resets."""
        db = self.db
        try:
            db.query(PeerFeedbackEntity).delete()
            db.query(TeamConflictEntity).delete()
            db.query(TeamExplanationEntity).delete()
            db.query(TeamMemberEntity).delete()
            db.query(TeamEntity).delete()
            db.query(GenerationRunEntity).delete()
            db.query(TeamConstraintEntity).delete()
            db.query(PreferenceEntity).delete()
            db.query(WorkStyleEntity).delete()
            db.query(AvailabilityEntity).delete()
            db.query(SkillEntity).delete()
            db.query(StudentEntity).delete()
            db.query(RequirementEntity).delete()
            db.query(ProjectEntity).delete()
            db.commit()
        except Exception:
            db.rollback()
            raise
