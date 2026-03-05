from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='payment_method',
            field=models.CharField(
                blank=True,
                choices=[('cash', 'Efectivo'), ('pse', 'PSE'), ('card', 'Tarjeta')],
                default='cash',
                max_length=10,
                null=True
            ),
        ),
    ]
