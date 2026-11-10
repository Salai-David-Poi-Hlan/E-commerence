from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from orders.models import Order
from orders.services import change_order_status,InvalidTransition

class Command(BaseCommand):
    
    help='Cancel pending orders older than N minutes and restore their stock'

    def add_arguments(self,parser):
        parser.add_argument('--minutes',type=int,default=45)
        parser.add_argument('--dry-run',action='store_true')

    def handle(self, *args, **options):
        cutoff=timezone.now() - timedelta(minutes=options['minutes'])
        ids=list(
            Order.objects.filter(status='pending',created_at__lt=cutoff)
            .values_list('pk',flat=True)
        )
        if options['dry_run']:
            self.stdout.write(f'Would cancel {len(ids)} order(s): {ids}')


        cancelled=skipped=0
        for order_id in ids:
            try:
                change_order_status(order_id,'cancelled',expected_status='pending')
                cancelled+=1
            except InvalidTransition:
                skipped+=1
        self.stdout.write(self.style.SUCCESS(
            f'Cancelled {cancelled}, skipped {skipped}'
        ))
    
   
