from django.db import migrations, models


def copy_status_to_boolean(apps, schema_editor):
    member_model = apps.get_model('memberships', 'Member')
    for member in member_model.objects.all().iterator():
        status_value = getattr(member, 'status', None)
        # Preserve existing semantic values from char status.
        member.status_bool = status_value == 'active'
        member.save(update_fields=['status_bool'])


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0002_member_payment_method'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='status_bool',
            field=models.BooleanField(default=True),
        ),
        migrations.RunPython(copy_status_to_boolean, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='member',
            name='status',
        ),
        migrations.RenameField(
            model_name='member',
            old_name='status_bool',
            new_name='status',
        ),
    ]
