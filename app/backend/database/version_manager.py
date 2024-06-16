from sqlalchemy import and_, or_
from app.backend.database.schema import Model, project_model_link
from app.backend.dtos.create_request import CreateModelDTO
from sqlalchemy.orm import Session


class VersionManager:

    @classmethod
    def increment_version(cls, version: str) -> str:
        parts = list(map(int, version.split('.')))
        parts[-1] += 1
        return '.'.join(map(str, parts))

    @staticmethod
    def extend_version(version: str) -> str:
        return version + '.1'

    @classmethod
    def get_next_version(cls, session: Session, model_dto: CreateModelDTO, parent_model: Model = None) -> str:
        # Step 1: Check if the parent_model is None
        if parent_model is None:
            return "0"  # Return version "0" for base models without a parent

        # Step 2: Check if the parent_model's version is "0"
        if parent_model.version == "0":
            # Major version increment for models directly trained from the base model
            sibling_versions = session.query(Model.version).join(project_model_link).filter(
                project_model_link.c.model_name == model_dto.model_name,
                project_model_link.c.project_id.in_(model_dto.project_ids),
                Model.version != "0"
            ).all()
            highest_version = max((int(v[0])
                                  for v in sibling_versions), default=0)
            return cls.increment_version(str(highest_version))

        # Step 3: Hierarchical sub-version increment for models trained from non-base models
        current_version = parent_model.version
        child_versions = session.query(Model.version).join(project_model_link).filter(
            project_model_link.c.model_name == model_dto.model_name,
            project_model_link.c.project_id.in_(model_dto.project_ids),
            Model.version.like(f"{current_version}.%")
        ).all()
        if not child_versions:
            return cls.extend_version(current_version)
        highest_sub_version = max(
            (int(v[0]) for v in child_versions), default=int(current_version + ".0"))
        return cls.increment_version(str(highest_sub_version))
