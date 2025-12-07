from encrypted_fields.fields import EncryptedFieldMixin
from phonenumber_field.modelfields import PhoneNumberField # type: ignore


class EncryptedPhoneNumberField(EncryptedFieldMixin, PhoneNumberField):
    pass
