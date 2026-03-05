from django.core.management.base import BaseCommand
from django.utils import timezone
from memberships.models import Member


class Command(BaseCommand):
    help = 'Actualiza el estado de todos los miembros basándose en la fecha de vencimiento de su membresía'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Muestra información detallada de las actualizaciones',
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        
        # Obtener todos los miembros
        members = Member.objects.all()
        
        updated_count = 0
        activated_count = 0
        deactivated_count = 0
        
        for member in members:
            old_status = member.status
            member.update_status()
            
            # Solo guardar si el estado cambió
            if old_status != member.status:
                member.save()
                updated_count += 1
                
                if member.status:
                    activated_count += 1
                    if verbose:
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'✓ {member.full_name} activado (vence: {member.membership_expires_at})'
                            )
                        )
                else:
                    deactivated_count += 1
                    if verbose:
                        self.stdout.write(
                            self.style.WARNING(
                                f'✗ {member.full_name} desactivado (venció: {member.membership_expires_at})'
                            )
                        )
        
        # Resumen
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Actualización completada ===\n'
                f'Total de miembros: {members.count()}\n'
                f'Estados actualizados: {updated_count}\n'
                f'Activados: {activated_count}\n'
                f'Desactivados: {deactivated_count}\n'
            )
        )
