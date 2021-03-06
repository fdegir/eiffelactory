"""
Module containing classes and methods for creating and handling Eiffel events.
Eiffel events should be created using the corresponding create_<event>() method.
All Eiffel model classes inherit from dict for easy json serialization.

Parameter and class descriptions are often taken verbatim or shortened from
the official Eiffel documentation found here:
https://github.com/eiffel-community/eiffel
"""
import uuid

from eiffelactory import utils

# Eiffel event types
EIFFEL_ARTIFACT_PUBLISHED_EVENT = "EiffelArtifactPublishedEvent"
EIFFEL_ARTIFACT_CREATED_EVENT = "EiffelArtifactCreatedEvent"

# Eiffel schema version
VERSION_3_0_0 = "3.0.0"

# Used to populate meta.source.name, identifies event sender
EIFFELACTORY = 'EIFFELACTORY'


class Event(dict):
    """
    Represents an Eiffel event.

    :param data: the event data
    :param links: the event links
    :param meta: the event meta
    """

    def __init__(self, data, links, meta):
        super().__init__(self, data=data, links=links, meta=meta)


class Meta(dict):
    """
    Represents an Eiffel event's meta object.
    Parameters with None as default value are non-required fields.

    :param event_type: type of event according to Eiffel specification
    :param version: Eiffel schema version
    :param tags: tags or keywords associated with the events
    :param source: a description of the source of the event
    """

    def __init__(self,
                 event_type,
                 version,
                 event_id=None,
                 time=None,
                 tags=None,
                 source=None):

        if event_id is None:
            event_id = str(uuid.uuid4())

        if time is None:
            time = utils.current_time_millis()

        super().__init__(self,
                         id=event_id,
                         type=event_type,
                         version=version,
                         time=time,
                         tags=tags,
                         source=source)


class Source(dict):
    """
    Represents an Eiffel event's meta.source object.
    Provides a description of the source of the event for traceability purposes.
    Parameters with None as default value are non-required fields.

    :param domain_id: identifies the domain that produced an event
    :param host: hostname of the event sender
    :param name: name of the event sender
    :param serializer: identity of the serializer used to construct the event
    :param uri: URI of, related to or describing the event sender
    """

    def __init__(self,
                 domain_id=None,
                 host=None,
                 name=EIFFELACTORY,
                 serializer=None,
                 uri=None):

        super().__init__(self,
                         domainId=domain_id,
                         host=host,
                         name=name,
                         serializer=serializer,
                         uri=uri)


class Link(dict):
    """
    Represents an Eiffel link object.

    :param link_type: type of link according to Eiffel specification
    :param target: the uuid of the parent event
    """

    ARTIFACT = "ARTIFACT"

    def __init__(self, link_type, target):
        super().__init__(self, type=link_type, target=target)


class ArtifactPublishedData(dict):
    """
    Represents an EiffelArtifactPublishedEvent's data object.

    :param locations: a list of locations at which the artifact may be retrieved
    """

    def __init__(self, locations):
        super().__init__(self, locations=locations)


class Location(dict):
    """
    Represents a location at which an artifact may be retrieved.

    :param uri: URI at which the artifact can be retrieved
    :param location_type: location type according to the Eiffel specification
    """

    ARTIFACTORY = "ARTIFACTORY"

    def __init__(self, uri, location_type=ARTIFACTORY):
        super().__init__(self, type=location_type, uri=uri)


def create_artifact_published_event(artc_event_id, locations):
    """
    Creates an EiffelArtifactPublishedEvent.

    :param artc_event_id: the target id of the required ARTIFACT link
    :param locations: a list of artifact locations
    :return: an Event object structured as an ArtP event
    """
    data = ArtifactPublishedData(locations)
    links = [Link(Link.ARTIFACT, artc_event_id)]
    meta = Meta(EIFFEL_ARTIFACT_PUBLISHED_EVENT, VERSION_3_0_0, source=Source())

    event = Event(data, links, meta)

    return event


def is_eiffel_event_type(event, event_type):
    """
    Checks if an event is of a given type.

    :param event: the Eiffel event as a dict
    :param event_type: the Eiffel event type
    :return: True if meta.type equals event_type
    """
    return event['meta']['type'] == event_type


def is_artifact_created_event(event):
    """
    Checks if an event is an EiffelArtifactCreatedEvent.

    :param event: the Eiffel event as a dict
    :return: True if meta.type equals EiffelArtifactCreatedEvent
    """
    return is_eiffel_event_type(event, EIFFEL_ARTIFACT_CREATED_EVENT)


def is_sent_from_sources(event, sources):
    """
    Checks if an event is sent from a list of source names.
    Source names are configured in eiffelactory.config.

    :param event: the Eiffel event
    :param sources: a list of source names
    :return: True if event's meta.source.name is in the list of source names
    """
    if 'source' not in event['meta'] \
            or event['meta']['source'] is None:
        return False

    if 'name' not in event['meta']['source'] \
            or event['meta']['source']['name'] is None:
        return False

    return event['meta']['source']['name'] in sources
