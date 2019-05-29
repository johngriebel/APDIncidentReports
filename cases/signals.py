import logging

from django.db.models.signals import pre_delete
from cases.models import IncidentFile

logger = logging.getLogger('cases')


def delete_incident_file_from_disk(sender, **kwargs):
    """When an IncidentFile object is deleted from the database, we must ensure that it is
       deleted from disk as well."""
    if sender == IncidentFile:
        instance = kwargs.get('instance')
        logger.info(f"About to delete theIncidentFile {instance} from disk")
        instance.file.delete()


pre_delete.connect(delete_incident_file_from_disk)
