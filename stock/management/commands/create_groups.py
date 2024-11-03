from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from django.apps import apps

class Command(BaseCommand):
    help = "Create Users and Admins groups with specific permissions"

    def handle(self, *args, **options):
        user_permissions = [
            'view_home',
            'view_watchlist',
            'view_portfolio',
            'view_profile',
            'view_stocks',
            'add_watchlist',
            'remove_watchlist',
            'purchase_stock',
            'sell_stock',
            'view_stock_analysis',
            'update_graph',
            'make_payment',
            'view_success_page'
        ]

        users_group, _ = Group.objects.get_or_create(name='Users')
        
        admins_group, _ = Group.objects.get_or_create(name='Admins')

        all_permissions = Permission.objects.all()

        admin_permissions = all_permissions.exclude(codename__in=[
            'view_home',
            'view_watchlist',
            'view_portfolio',
            'view_profile'
        ])
        admins_group.permissions.set(admin_permissions)

        user_permission_objects = Permission.objects.filter(codename__in=user_permissions)
        users_group.permissions.set(user_permission_objects)

        self.stdout.write(
            self.style.SUCCESS('Successfully created Users and Admins groups with permissions')
        )
