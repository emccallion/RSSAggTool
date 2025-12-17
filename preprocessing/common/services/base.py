"""
Base service classes for business logic.
"""
from django.core.exceptions import ValidationError


class BaseCRUDService:
    """
    Base service class providing CRUD operations.

    Subclasses should set the 'model' attribute.
    """
    model = None

    @classmethod
    def get_model(cls):
        """Get the model class."""
        if cls.model is None:
            raise NotImplementedError("Subclass must set 'model' attribute")
        return cls.model

    @classmethod
    def get_all(cls, **filters):
        """Get all instances, optionally filtered."""
        model = cls.get_model()
        return model.objects.filter(**filters)

    @classmethod
    def get_by_id(cls, id):
        """Get a single instance by ID."""
        model = cls.get_model()
        return model.objects.get(pk=id)

    @classmethod
    def get_or_none(cls, **filters):
        """Get a single instance or None."""
        model = cls.get_model()
        try:
            return model.objects.get(**filters)
        except model.DoesNotExist:
            return None

    @classmethod
    def create(cls, **data):
        """Create a new instance."""
        model = cls.get_model()

        # Validate data
        cls.validate_create(data)

        # Pre-create hook
        data = cls.before_create(data)

        # Create instance
        instance = model.objects.create(**data)

        # Post-create hook
        cls.after_create(instance)

        return instance

    @classmethod
    def update(cls, instance, **data):
        """Update an existing instance."""
        # Validate data
        cls.validate_update(instance, data)

        # Pre-update hook
        data = cls.before_update(instance, data)

        # Update fields
        for key, value in data.items():
            setattr(instance, key, value)

        instance.save()

        # Post-update hook
        cls.after_update(instance)

        return instance

    @classmethod
    def delete(cls, instance):
        """Delete an instance."""
        # Pre-delete hook
        cls.before_delete(instance)

        instance.delete()

        # Post-delete hook
        cls.after_delete(instance)

    # Validation hooks (override in subclasses)
    @classmethod
    def validate_create(cls, data):
        """Validate data before creating. Raise ValidationError if invalid."""
        pass

    @classmethod
    def validate_update(cls, instance, data):
        """Validate data before updating. Raise ValidationError if invalid."""
        pass

    # Lifecycle hooks (override in subclasses)
    @classmethod
    def before_create(cls, data):
        """Hook called before creating an instance. Return modified data."""
        return data

    @classmethod
    def after_create(cls, instance):
        """Hook called after creating an instance."""
        pass

    @classmethod
    def before_update(cls, instance, data):
        """Hook called before updating an instance. Return modified data."""
        return data

    @classmethod
    def after_update(cls, instance):
        """Hook called after updating an instance."""
        pass

    @classmethod
    def before_delete(cls, instance):
        """Hook called before deleting an instance."""
        pass

    @classmethod
    def after_delete(cls, instance):
        """Hook called after deleting an instance."""
        pass
