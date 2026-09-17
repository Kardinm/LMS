from django.db import migrations, models


def normalize_tags(apps, schema_editor):
    Tag = apps.get_model('courses', 'CourseTag')
    Course = apps.get_model('courses', 'Course')
    seen = {}
    for tag in Tag.objects.order_by('pk'):
        name = ' '.join(tag.name.split())
        key = name.casefold()
        if key in seen:
            for course in Course.objects.filter(tags=tag):
                course.tags.add(seen[key])
            tag.delete()
        else:
            tag.name = name
            tag.normalized_name = key
            tag.save()
            seen[key] = tag.pk


class Migration(migrations.Migration):
    dependencies = [('courses', '0007_coursetag_icon_coursetag_normalized_name_and_more')]
    operations = [
        migrations.RunPython(normalize_tags, migrations.RunPython.noop),
        migrations.AlterField(model_name='coursetag', name='normalized_name',
                              field=models.CharField(max_length=100, unique=True, editable=False)),
    ]