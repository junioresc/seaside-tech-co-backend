from model_utils.models import TimeStampedModel, UUIDModel


class BaseModel(UUIDModel, TimeStampedModel):
    """
    Shared base that provides UUID primary keys and the richer created/modified
    behavior from model_utils' TimeStampedModel.
    """

    class Meta:
        abstract = True
