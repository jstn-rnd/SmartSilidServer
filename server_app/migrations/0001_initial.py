<<<<<<< HEAD
# Generated by Django 5.1 on 2024-08-10 20:27
=======
# Generated by Django 5.0.7 on 2024-08-14 17:14
>>>>>>> 80df7ac60918b66063a9d995e13b7ac1de16e511

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Blacklist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Computer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('computer_name', models.CharField(default=' ', max_length=255)),
                ('mac_address', models.CharField(default=' ', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='ComputerLogs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('computerName', models.CharField(max_length=255)),
                ('dateTime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='MacAddress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='StudentMAC',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('computer_name', models.CharField(max_length=255)),
                ('mac_address', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Test',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('RFID', models.CharField(max_length=30, unique=True)),
                ('approved', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Whitelist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('middle_initial', models.CharField(default=' ', max_length=255)),
                ('type', models.CharField(default=' ', max_length=255)),
                ('section', models.CharField(default=' ', max_length=255)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
<<<<<<< HEAD
=======
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('rfids', models.ManyToManyField(blank=True, to='server_app.test')),
            ],
        ),
        migrations.CreateModel(
>>>>>>> 80df7ac60918b66063a9d995e13b7ac1de16e511
            name='UserLog',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('dateTime', models.DateTimeField()),
<<<<<<< HEAD
=======
                ('computer', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='UserLogs', to='server_app.computer')),
>>>>>>> 80df7ac60918b66063a9d995e13b7ac1de16e511
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='UserLogs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
