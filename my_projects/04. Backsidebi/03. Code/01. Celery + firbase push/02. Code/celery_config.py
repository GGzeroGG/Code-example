from celery.schedules import crontab

CELERY_BROKER_URL = env.str('CELERY_BROKER_URL',
                            default='redis://localhost:6379/6')
CELERY_IMPORTS = (
    'services.tasks.notifications',
    'services.tasks.cleanup',
)
CELERY_BEAT_SCHEDULE = {
    'cleanup_notifications': {
        'task': 'services.tasks.cleanup.cleanup_notifications',
        'schedule': crontab(minute=0, hour=1),
    },
}
