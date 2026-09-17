from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_grade'),
    ]

    operations = [
        migrations.CreateModel(
            name='CourseTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.AddField(
            model_name='course',
            name='completion_badge_name',
            field=models.CharField(blank=True, default='', max_length=80),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='course',
            name='completion_badge_icon',
            field=models.CharField(blank=True, default='🏆', max_length=8),
        ),
        migrations.AddField(
            model_name='course',
            name='completion_badge_color',
            field=models.CharField(blank=True, default='#6c63ff', max_length=7),
        ),
        migrations.AddField(
            model_name='course',
            name='tags',
            field=models.ManyToManyField(blank=True, related_name='courses', to='courses.coursetag'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='lesson_type',
            field=models.CharField(choices=[('self_study', 'Самовивчення'), ('video', 'Відеоурок'), ('mixed', 'Змішаний'), ('live', 'Онлайн-зустріч'), ('practice', 'Практика')], default='self_study', max_length=20),
        ),
    ]
