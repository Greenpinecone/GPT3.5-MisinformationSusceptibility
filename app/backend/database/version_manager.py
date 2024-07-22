"""
Version management module.

This module provides functionality to manage and increment model version strings.
It supports both vertical and horizontal versioning, similar to book chapters.

Classes:
    VersionManager: Manages the increment and extension of version strings for models.
"""


from sqlalchemy.orm import Session
from app.backend.database.schema import Model, project_model_link


class VersionManager:
    """
    A manager class for handling model version strings.

    The VersionManager class provides methods to increment and extend version strings,
    as well as to determine the next appropriate version for a model based on its parent
    and sibling versions within a project.

    Methods:
        increment_version(version: str) -> str: Increments the last part of a version string.
        extend_version(version: str) -> str: Extends a version string by adding '.1' to the end.
        get_next_version(session: Session, model_name: str, project_ids: list[int], parent_model: Model = None) -> str:
            Determines the next version for a model based on its parent model and sibling versions.

    INFO / TODO: Currently there is a problem if you import a global model into a project which has the same name as one of the current native models in the project (besides project prefix). This causes version confusion as soon as the imported model is trained, since then the resulting model is native to the current project, causing two models with the same name, even though they come from different model hierarchies. Due to the same name, the versioning will now consider both models for the next verion calculation, causing a wrong next version. This can be solved by providing unique hierarchy identifiers per model, that are also considered together with the project. This has not been fixed yet due to unimportance.
    """

    @classmethod
    def increment_version(cls, version: str) -> str:
        """
        Increments the last part of a version string.

        Args:
            version (str): The current version string.

        Returns:
            str: The incremented version string.
        """

        parts = list(map(int, version.split('.')))
        parts[-1] += 1
        return '.'.join(map(str, parts))

    @staticmethod
    def extend_version(version: str) -> str:
        """
        Extends a version string by adding '.1' to the end.

        Args:
            version (str): The current version string.

        Returns:
            str: The extended version string.
        """

        return version + '.1'

    @classmethod
    def get_next_version(cls, session: Session, model_name: str, project_ids: list[int], parent_model: Model = None) -> str:
        """
        Determines the next version for a model based on its parent model, sibling versions and the current project they are in.

        Args:
            session (Session): SQLAlchemy session for database access.
            model_name (str): The name of the model.
            project_ids (list[int]): List of project IDs the model is associated with.
            parent_model (Model, optional): The parent model of the current model. Can be None.

        Returns:
            str: The next version string for the model.
        """

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
