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
    def get_next_version(cls, session: Session, model_name: str, project_ids: list[int], parent_model: Model = None) -> str:
        # Step 1: Check if the parent_model is None
        if parent_model is None:
            return "0"  # Return version "0" for base models without a parent

        # Step 2: Check if the parent_model's version is "0"
        if parent_model.version == "0":
            # Major version increment for models directly trained from the base model
            sibling_versions = session.query(Model.version).join(project_model_link).filter(
                project_model_link.c.model_name == model_name,
                project_model_link.c.project_id.in_(project_ids),
                Model.parent_model_id == parent_model.id,
                Model.version != "0"
            ).all()

            # Filter versions that do not contain a dot
            major_versions = [v[0]
                              for v in sibling_versions if '.' not in v[0]]
            major_versions = [int(v) for v in major_versions]
            highest_major_version = max(major_versions, default=0)
            return str(highest_major_version + 1)

        # Step 3: Hierarchical sub-version increment for models trained from non-base models
        current_version = parent_model.version
        child_versions = session.query(Model.version).join(project_model_link).filter(
            project_model_link.c.model_name == model_name,
            project_model_link.c.project_id.in_(project_ids),
            Model.parent_model_id == parent_model.id,
            Model.version.like(f"{current_version}.%")
        ).all()
        if not child_versions:
            return cls.extend_version(current_version)

        # Parse child_versions to lists of integers
        child_versions = [list(map(int, v[0].split('.')))
                          for v in child_versions]

        # Default value for highest_sub_version should be a parsed version of current_version + ".0"
        default_sub_version = list(
            map(int, (current_version + ".0").split('.')))
        highest_sub_version = max(child_versions, default=default_sub_version)

        return cls.increment_version('.'.join(map(str, highest_sub_version)))
