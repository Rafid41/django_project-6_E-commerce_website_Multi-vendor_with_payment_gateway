# NOTE: only run migration after complete this whole code, register in admin site, configure settings.py
# NOTE: settings.py e bole dte hbe j amra built in user model change koresi
# NOTE: migration run korte 1st: 'py manage.py makemigrations App_Login' run korte hbe, not 'py manage.py migrate'

from django.db import models

# to rewrite the built-in user model
# to create a custom user model and admin panel
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as ugettext_lazy     # django-4 e ugettext_lazy nai

# To automatically create pne to one objects
from django.db.models.signals import post_save
from django.dispatch import receiver




# Create your models here.
# BaseUserManager new user handle kore
class MyUserManager(BaseUserManager):

    # built-in class, unique email identifier, not username
    # email + password diye hbe
    def _create_user(self, email, password, **extra_fields):

        if not email:
            raise ValueError("The Email must be set!")
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using = self.db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True')
        return self._create_user(email, password, **extra_fields)
    


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique= True, null = False)
    account_type = models.CharField(
        max_length=10,
        choices= (('Normal','Normal'),('Seller','Seller')),
    )

    # admin panel er 'checkbox text' and checkbox text er 'description' change korbe
    is_staff = models.BooleanField(
        ugettext_lazy('staff status'), 
        default=False,
        help_text = ugettext_lazy('designates whether the user can log in to admin panel')
    )

    is_active = models.BooleanField(
        ugettext_lazy('active'),
        default= True,
        help_text= ugettext_lazy('Designates whether this user should be treated as active. Unselect this instead of deleting accounts'),
    )


    # email will be treated as username
    USERNAME_FIELD = 'email'
    objects = MyUserManager()


    # rewriting 3 built-in fn
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email
    


# extra fileds of User class
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    username = models.CharField(max_length=264, blank=True)
    full_name = models.CharField(max_length=264, blank=True)
    address_1 = models.TextField(max_length=300, blank=True)
    city = models.CharField(max_length=40, blank=True)
    zipcode = models.CharField(max_length=10, blank=True)
    country = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username + "'s Profile"
    

    # chk all field filled or not, user defined fn
    def is_fully_filled(self):
        fields_name_list = [f.name for f in self._meta.get_fields()]   # eita likhle oi classer shob filed check kore

        for field_name in fields_name_list:
            value = getattr(self, field_name)

            if value is None or value =='':
                return False
        return True
    

# views.py e call kore one-to-one relation built er alternative
@receiver(post_save, sender= User)  # means User model kono signal send kore j ami save hoyesi, then nicher fn call hbe
def create_profile(sender, instance, created, **kwargs):
  
    if created:
        Profile.objects.create(user=instance)  # jodi asholei model create hoye thake, thn oi model er ekti object create hbe


@receiver(post_save, sender= User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
    # means User model er kno change er jnno Profile model eo tar provab porbe (oneToOne relation er jnno)
    # 'profile' holo related name

