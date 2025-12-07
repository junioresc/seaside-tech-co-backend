from phonenumber_field.modelfields import PhoneNumberField
from encrypted_fields.fields import EncryptedFieldMixin


class EncryptedPhoneNumberField(EncryptedFieldMixin, PhoneNumberField):
    pass