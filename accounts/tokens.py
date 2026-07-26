from django.contrib.auth.tokens import PasswordResetTokenGenerator


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        verified = user.email_verified_at.isoformat() if user.email_verified_at else ""
        return f"{user.pk}{user.password}{timestamp}{user.email}{verified}"


email_verification_token = EmailVerificationTokenGenerator()
