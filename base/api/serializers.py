# Classes takes in data/models we want to seralise and turn into JSON formatted data
from rest_framework.serializers import ModelSerializer, ImageField, ValidationError, CharField, SerializerMethodField
from django.contrib.auth import get_user_model
from base.models import Room, Message, Topic, Profile

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__' 

    # Field-level example
    def validate_name(self, value):
        if len(value.strip()) < 3:
            raise ValidationError("Name must be at least 3 characters.")
        return value

    # Object-level example (use if you need cross-field checks)
    def validate(self, attrs):
        # e.g. ensure description isn’t identical to name
        if 'name' in attrs and 'description' in attrs:
            if attrs['name'].strip().lower() == attrs['description'].strip().lower():
                raise ValidationError("Description must differ from name.")
        return attrs
    

User = get_user_model()


class UserSerializer(ModelSerializer):
    password = CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()
        Profile.objects.get_or_create(user=user)
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            if not password.strip():
                raise ValidationError({"password": "Password cannot be blank."})
            instance.set_password(password)

        instance.save()
        return instance
class MessageSerializer(ModelSerializer):
    username = CharField(source='user.username', read_only=True)
    room_name = CharField(source='room.name', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'username', 'room_name', 'body', 'updated', 'created']
        read_only_fields = ['id', 'username', 'room_name', 'updated', 'created']

class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'

class ProfileSerializer(ModelSerializer):
    profile_img = ImageField(required=False, allow_null=True)
    profile_img_url = SerializerMethodField()

    class Meta:
        model = Profile
        # include the URL field in `fields`
        fields = ["id", "user_id", "profile_img", "profile_img_url"]
        read_only_fields = ["id", "user_id"]

    def get_profile_img_url(self, obj):
        request = self.context.get("request")
        if obj.profile_img:
            url = obj.profile_img.url
            return request.build_absolute_uri(url) if request else url
        return None