import secrets
from datetime import timedelta
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


def generate_and_send_verification_code(user):
    code = f"{secrets.randbelow(900000) + 100000:06d}"
    user.verification_code = code
    user.verification_code_expires_at = timezone.now() + timedelta(minutes=15)
    user.save(update_fields=["verification_code", "verification_code_expires_at"])

    subject = "DineFlow — Verify Your Email"
    message = (
        f"Hello {user.username},\n\n"
        f"Your DineFlow verification code is: {code}\n\n"
        f"This code will expire in 15 minutes.\n\n"
        f"Thank you,\nDineFlow Team"
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    return code


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "password_confirm",
            "phone_number",
            "role",
            "is_email_verified",
        )
        read_only_fields = ("id", "is_email_verified")

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Password fields do not match."}
            )
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        role = validated_data.get("role", User.Role.CUSTOMER)
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            phone_number=validated_data.get("phone_number", ""),
            role=role,
            is_email_verified=False,
        )
        generate_and_send_verification_code(user)
        return user


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    code = serializers.CharField(max_length=6, min_length=6, required=True)

    def validate(self, attrs):
        email = attrs.get("email")
        code = attrs.get("code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "No account found with this email."})

        if user.is_email_verified:
            raise serializers.ValidationError({"detail": "Email is already verified."})

        if user.verification_code != code:
            raise serializers.ValidationError({"code": "Invalid verification code."})

        if user.verification_code_expires_at and timezone.now() > user.verification_code_expires_at:
            raise serializers.ValidationError({"code": "Verification code has expired. Please request a new one."})

        attrs["user"] = user
        return attrs


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No account found with this email.")

        if user.is_email_verified:
            raise serializers.ValidationError("Email is already verified.")

        return value


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        if not self.user.is_email_verified and not self.user.is_superuser:
            raise serializers.ValidationError(
                {
                    "detail": "Please verify your email before logging in.",
                    "needs_verification": True,
                    "email": self.user.email,
                }
            )

        data["user"] = {
            "id": self.user.id,
            "username": self.user.username,
            "email": self.user.email,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "phone_number": self.user.phone_number,
            "role": self.user.role,
            "is_email_verified": self.user.is_email_verified,
        }
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = ("id", "role", "is_email_verified", "date_joined")


class AdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "password",
            "first_name",
            "last_name",
            "phone_number",
            "role",
            "is_active",
            "is_email_verified",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, validators=[validate_password]
    )
    new_password_confirm = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password": "New passwords do not match."}
            )
        return attrs