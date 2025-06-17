from qgis.core import (
    QgsProject,
    QgsVectorLayer,
    QgsFields,
    QgsField,
    QgsVectorFileWriter,
    QgsWkbTypes,
    QgsEditorWidgetSetup,
    QgsDefaultValue,
    QgsFieldConstraints,
    QgsProviderRegistry,
    QgsFeature,
    QgsEditFormConfig,
    QgsAttributeEditorContainer,
    QgsAttributeEditorField,
    QgsOptionalExpression,
    QgsExpression,
    QgsRelation
)
from qgis.PyQt.QtWidgets import QFileDialog, QApplication
from qgis.PyQt.QtCore import QVariant
import pandas as pd
import uuid
import os
import gc

CONST_LANGUAGE = 'lt' # Change the language code to the desired language

gpkg_layers_config = {
    'accessibility_domain': {
        'geometry': 'None',
        'attributes': {
            'code': {'type': QVariant.String, 'notnull': True},
            'value': {'type': QVariant.String, 'notnull': True},
        },
    },
    'access_control_domain': {
        'geometry': 'None',
        'attributes': {
            'code': {'type': QVariant.String, 'notnull': True},
            'value': {'type': QVariant.String, 'notnull': True},
        },
    },
    'address': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'address': {'type': QVariant.String, 'notnull': True},
            'unit': {'type': QVariant.String, 'notnull': False},
            'locality': {'type': QVariant.String, 'notnull': True},
            'province': {'type': QVariant.String, 'notnull': False},
            'country': {'type': QVariant.String, 'notnull': True},
            'postal_code': {'type': QVariant.String, 'notnull': False},
            'postal_code_ext': {'type': QVariant.String, 'notnull': False},
            'postal_code_vanity': {'type': QVariant.String, 'notnull': False},
        },
    },
    'venue': {
        'geometry': 'Multipolygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'hours': {'type': QVariant.String, 'notnull': False},
            'phone': {'type': QVariant.String, 'notnull': False},
            'website': {'type': QVariant.String, 'notnull': False},
            'display_point': {'type': QVariant.String, 'notnull': True},
            'address_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'amenity': {
        'geometry': 'Point',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'accessibility': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'hours': {'type': QVariant.String, 'notnull': False},
            'phone': {'type': QVariant.String, 'notnull': False},
            'website': {'type': QVariant.String, 'notnull': False},
            'address_id': {'type': QVariant.String, 'notnull': False},
            'correlation_id': {'type': QVariant.String, 'notnull': False},
        },
    },
    'anchor': {
        'geometry': 'Point',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'address_id': {'type': QVariant.String, 'notnull': False},
            'unit_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'building': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'display_point': {'type': QVariant.String, 'notnull': False},
            'address_id': {'type': QVariant.String, 'notnull': False},
        },
    },
    'detail': {
        'geometry': 'MultiLineString',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'level_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'fixture': {
        'geometry': 'Polygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'anchor_id': {'type': QVariant.String, 'notnull': False},
            'level_id': {'type': QVariant.String, 'notnull': True},
            'display_point': {'type': QVariant.String, 'notnull': False},
        },
    },
    'footprint': {
        'geometry': 'Multipolygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
        },
    },
    'geofence': {
        'geometry': 'Polygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'correlation_id': {'type': QVariant.String, 'notnull': False},
            'display_point': {'type': QVariant.String, 'notnull': False},
        },
    },
    'kiosk': {
        'geometry': 'Polygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'anchor_id': {'type': QVariant.String, 'notnull': False},
            'level_id': {'type': QVariant.String, 'notnull': True},
            'display_point': {'type': QVariant.String, 'notnull': False},
        },
    },
    'level': {
        'geometry': 'Multipolygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'outdoor': {'type': QVariant.Bool, 'notnull': True},
            'ordinal': {'type': QVariant.Int, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'short_name': {'type': QVariant.StringList, 'notnull': True},
            'display_point': {'type': QVariant.String, 'notnull': False},
            'address_id': {'type': QVariant.String, 'notnull': False},
        },
    },
    'occupant': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'anchor_id': {'type': QVariant.String, 'notnull': True},
            'hours': {'type': QVariant.String, 'notnull': False},
            'phone': {'type': QVariant.String, 'notnull': False},
            'website': {'type': QVariant.String, 'notnull': False},
            'start': {'type': QVariant.DateTime, 'notnull': False},
            'end': {'type': QVariant.DateTime, 'notnull': False},
            'modified': {'type': QVariant.DateTime, 'notnull': False},
            'correlation_id': {'type': QVariant.String, 'notnull': False},
        },
    },
    'opening': {
        'geometry': 'String',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'accessibility': {'type': QVariant.String, 'notnull': False},
            'access_control': {'type': QVariant.String, 'notnull': False},
            'type': {'type': QVariant.String, 'notnull': False},
            'automatic': {'type': QVariant.Bool, 'notnull': False},
            'material': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'display_point': {'type': QVariant.String, 'notnull': False},
            'level_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'relationship': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'direction': {'type': QVariant.String, 'notnull': True},
            'origin_type': {'type': QVariant.String, 'notnull': False},
            'origin_unit_id': {'type': QVariant.String, 'notnull': False},
            'origin_opening_id': {'type': QVariant.String, 'notnull': False},
            'intermediary_type': {'type': QVariant.String, 'notnull': False},
            'destination_type': {'type': QVariant.String, 'notnull': False},
            'destination_unit_id': {'type': QVariant.String, 'notnull': False},
            'destination_opening_id': {'type': QVariant.String, 'notnull': False},
            'hours': {'type': QVariant.String, 'notnull': False},
        },
    },
    'section': {
        'geometry': 'Polygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'accessibility': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'display_point': {'type': QVariant.String, 'notnull': False},
            'level_id': {'type': QVariant.String, 'notnull': True},
            'address_id': {'type': QVariant.String, 'notnull': False},
            'correlation_id': {'type': QVariant.String, 'notnull': False},
        },
    },
    'unit': {
        'geometry': 'Polygon',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'category': {'type': QVariant.String, 'notnull': True},
            'restriction': {'type': QVariant.String, 'notnull': False},
            'accessibility': {'type': QVariant.String, 'notnull': False},
            'name': {'type': QVariant.StringList, 'notnull': True},
            'alt_name': {'type': QVariant.StringList, 'notnull': False},
            'level_id': {'type': QVariant.String, 'notnull': True},
            'display_point': {'type': QVariant.String, 'notnull': False},
        },
    },
    'geofence_level': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'geofence_id': {'type': QVariant.String, 'notnull': True},
            'level_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'level_building': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'level_id': {'type': QVariant.String, 'notnull': True},
            'building_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'geofence_building': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'geofence_id': {'type': QVariant.String, 'notnull': True},
            'building_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'footprint_building': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'footprint_id': {'type': QVariant.String, 'notnull': True},
            'building_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'relationship_opening': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'relationship_id': {'type': QVariant.String, 'notnull': True},
            'opening_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'relationship_unit': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'relationship_id': {'type': QVariant.String, 'notnull': True},
            'unit_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'geofence_parent': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'parent_id': {'type': QVariant.String, 'notnull': True},
            'child_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'section_parent': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'parent_id': {'type': QVariant.String, 'notnull': True},
            'child_id': {'type': QVariant.String, 'notnull': True},
        },
    },
    'amenity_unit': {
        'geometry': 'None',
        'attributes': {
            'id': {'type': QVariant.String, 'notnull': True},
            'amenity_id': {'type': QVariant.String, 'notnull': True},
            'unit_id': {'type': QVariant.String, 'notnull': True},
        },
    },
}


relationships_config = {
    'section_correlation': {
        'referenced_layer': 'section',
        'referencing_layer': 'section',
        'referenced_field': 'id',
        'referencing_field': 'correlation_id',
        'strength': QgsRelation.Association
    },
    'address_amenity': {
        'referenced_layer': 'address',
        'referencing_layer': 'amenity',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'amenity_correlation_id': {
        'referenced_layer': 'amenity',
        'referencing_layer': 'amenity',
        'referenced_field': 'id',
        'referencing_field': 'correlation_id',
        'strength': QgsRelation.Association
    },
    'address_anchor': {
        'referenced_layer': 'address',
        'referencing_layer': 'anchor',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'unit_anchor': {
        'referenced_layer': 'unit',
        'referencing_layer': 'anchor',
        'referenced_field': 'id',
        'referencing_field': 'unit_id',
        'strength': QgsRelation.Composition
    },
    'address_building': {
        'referenced_layer': 'address',
        'referencing_layer': 'building',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'level_detail': {
        'referenced_layer': 'level',
        'referencing_layer': 'detail',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'anchor_fixture': {
        'referenced_layer': 'anchor',
        'referencing_layer': 'fixture',
        'referenced_field': 'id',
        'referencing_field': 'anchor_id',
        'strength': QgsRelation.Association
    },
    'level_fixture': {
        'referenced_layer': 'level',
        'referencing_layer': 'fixture',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'geofence_correlation_id': {
        'referenced_layer': 'geofence',
        'referencing_layer': 'geofence',
        'referenced_field': 'id',
        'referencing_field': 'correlation_id',
        'strength': QgsRelation.Association
    },
    'anchor_kiosk': {
        'referenced_layer': 'anchor',
        'referencing_layer': 'kiosk',
        'referenced_field': 'id',
        'referencing_field': 'anchor_id',
        'strength': QgsRelation.Association
    },
    'level_kiosk': {
        'referenced_layer': 'level',
        'referencing_layer': 'kiosk',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'address_level': {
        'referenced_layer': 'address',
        'referencing_layer': 'level',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'anchor_occupant': {
        'referenced_layer': 'anchor',
        'referencing_layer': 'occupant',
        'referenced_field': 'id',
        'referencing_field': 'anchor_id',
        'strength': QgsRelation.Association
    },
    'occupant_correlation_id': {
        'referenced_layer': 'occupant',
        'referencing_layer': 'occupant',
        'referenced_field': 'id',
        'referencing_field': 'correlation_id',
        'strength': QgsRelation.Association
    },
    'level_opening': {
        'referenced_layer': 'level',
        'referencing_layer': 'opening',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'unit_relationship': {
        'referenced_layer': 'unit',
        'referencing_layer': 'relationship',
        'referenced_field': 'id',
        'referencing_field': 'origin_unit_id',
        'strength': QgsRelation.Composition
    },
    'opening_relationship': {
        'referenced_layer': 'opening',
        'referencing_layer': 'relationship',
        'referenced_field': 'id',
        'referencing_field': 'origin_opening_id',
        'strength': QgsRelation.Composition
    },
    'unit_destination': {
        'referenced_layer': 'unit',
        'referencing_layer': 'relationship',
        'referenced_field': 'id',
        'referencing_field': 'destination_unit_id',
        'strength': QgsRelation.Composition
    },
    'opening_destination': {
        'referenced_layer': 'opening',
        'referencing_layer': 'relationship',
        'referenced_field': 'id',
        'referencing_field': 'destination_opening_id',
        'strength': QgsRelation.Composition
    },
    'level_section': {
        'referenced_layer': 'level',
        'referencing_layer': 'section',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'address_section': {
        'referenced_layer': 'address',
        'referencing_layer': 'section',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'section_correlation_id': {
        'referenced_layer': 'section',
        'referencing_layer': 'section',
        'referenced_field': 'id',
        'referencing_field': 'correlation_id',
        'strength': QgsRelation.Association
    },
    'level_unit': {
        'referenced_layer': 'level',
        'referencing_layer': 'unit',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Composition
    },
    'address_venue': {
        'referenced_layer': 'address',
        'referencing_layer': 'venue',
        'referenced_field': 'id',
        'referencing_field': 'address_id',
        'strength': QgsRelation.Association
    },
    'level_geofence_level': {
        'referenced_layer': 'level',
        'referencing_layer': 'geofence_level',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Association
    },
    'geofence_level_ids': {
        'referenced_layer': 'geofence',
        'referencing_layer': 'geofence_level',
        'referenced_field': 'id',
        'referencing_field': 'geofence_id',
        'strength': QgsRelation.Association
    },
    'level_building_ids': {
        'referenced_layer': 'level',
        'referencing_layer': 'level_building',
        'referenced_field': 'id',
        'referencing_field': 'level_id',
        'strength': QgsRelation.Association
    },
    'building_level_building': {
        'referenced_layer': 'building',
        'referencing_layer': 'level_building',
        'referenced_field': 'id',
        'referencing_field': 'building_id',
        'strength': QgsRelation.Association
    },
    'geofence_building_ids': {
        'referenced_layer': 'geofence',
        'referencing_layer': 'geofence_building',
        'referenced_field': 'id',
        'referencing_field': 'geofence_id',
        'strength': QgsRelation.Association
    },
    'building_geofence_building': {
        'referenced_layer': 'building',
        'referencing_layer': 'geofence_building',
        'referenced_field': 'id',
        'referencing_field': 'building_id',
        'strength': QgsRelation.Association
    },
    'footprint_building_ids': {
        'referenced_layer': 'footprint',
        'referencing_layer': 'footprint_building',
        'referenced_field': 'id',
        'referencing_field': 'footprint_id',
        'strength': QgsRelation.Association
    },
    'building_footprint_building': {
        'referenced_layer': 'building',
        'referencing_layer': 'footprint_building',
        'referenced_field': 'id',
        'referencing_field': 'building_id',
        'strength': QgsRelation.Association
    },
    'intermediary_opening_ids': {
        'referenced_layer': 'relationship',
        'referencing_layer': 'relationship_opening',
        'referenced_field': 'id',
        'referencing_field': 'relationship_id',
        'strength': QgsRelation.Association
    },
    'opening_relationship_opening': {
        'referenced_layer': 'opening',
        'referencing_layer': 'relationship_opening',
        'referenced_field': 'id',
        'referencing_field': 'opening_id',
        'strength': QgsRelation.Association
    },
    'intermediary_unit_ids': {
        'referenced_layer': 'relationship',
        'referencing_layer': 'relationship_unit',
        'referenced_field': 'id',
        'referencing_field': 'relationship_id',
        'strength': QgsRelation.Association
    },
    'unit_relationship_unit': {
        'referenced_layer': 'unit',
        'referencing_layer': 'relationship_unit',
        'referenced_field': 'id',
        'referencing_field': 'unit_id',
        'strength': QgsRelation.Association
    },
    'geofence_parent_ids': {
        'referenced_layer': 'geofence',
        'referencing_layer': 'geofence_parent',
        'referenced_field': 'id',
        'referencing_field': 'child_id',
        'strength': QgsRelation.Association
    },
    'geofence_parent_child_ids': {
        'referenced_layer': 'geofence',
        'referencing_layer': 'geofence_parent',
        'referenced_field': 'id',
        'referencing_field': 'parent_id',
        'strength': QgsRelation.Association
    },
    'section_parent_ids': {
        'referenced_layer': 'section',
        'referencing_layer': 'section_parent',
        'referenced_field': 'id',
        'referencing_field': 'child_id',
        'strength': QgsRelation.Association
    },
    'section_parent_child_ids': {
        'referenced_layer': 'section',
        'referencing_layer': 'section_parent',
        'referenced_field': 'id',
        'referencing_field': 'parent_id',
        'strength': QgsRelation.Association
    },
    'amenity_unit_ids': {
        'referenced_layer': 'amenity',
        'referencing_layer': 'amenity_unit',
        'referenced_field': 'id',
        'referencing_field': 'amenity_id',
        'strength': QgsRelation.Association
    },
    'unit_amenity_unit': {
        'referenced_layer': 'unit',
        'referencing_layer': 'amenity_unit',
        'referenced_field': 'id',
        'referencing_field': 'unit_id',
        'strength': QgsRelation.Association
    },
}

domain_fields_config = {
    'accessibility': 'accessibility_domain',
    'access_control': 'access_control_domain'
}

domain_config = {
    'Key': 'code',
    'Value': 'code',
    'AllowMulti': True,
    'AllowNull': True,
    'FilterExpression': '',
    'OrderByValue': False,
    'Description': 'value',
    'UseCompleter': False,
    'NofColumns': 1
}

layer_groups_config = {
    'IMDF features': [
        'address', 'venue', 'building', 'detail', 'anchor', 'amenity', 
        'fixture', 'kiosk', 'unit', 'opening', 'section', 'geofence', 
        'level', 'footprint', 'relationship', 'occupant'
    ],
    'Junction tables': [
        'geofence_level', 'level_building', 'geofence_building',
        'footprint_building', 'relationship_opening', 'relationship_unit',
        'geofence_parent', 'section_parent', 'amenity_unit'
    ],
    'Domain tables': [
        'access_control_domain', 'accessibility_domain'
    ]
}

def add_enum_domain(conn, constraint_name, values, table_name, column_name):
    """Inserts an enum domain into the GeoPackage data column constraints table"""
    # Escape single quotes in values
    value_tuples = [
        f"""('{constraint_name}', 'enum', '{str(code).replace("'", "''")}', '{str(value).replace("'", "''")}')"""
        for code, value in values
    ]
    values_sql = ",\n".join(value_tuples)

    insert_sql = f"""
        INSERT OR IGNORE INTO gpkg_data_column_constraints (constraint_name, constraint_type, value, description)
        VALUES
        {values_sql};
    """
    conn.executeSql(insert_sql)

    conn.executeSql(f"""
        INSERT OR REPLACE INTO gpkg_data_columns (table_name, column_name, constraint_name)
        VALUES ('{table_name}', '{column_name}', '{constraint_name}');
    """)

def insert_domain_values(gpkg_path, excel_data, domain_sheets):
    """
    Insert domain values from Excel sheets into GeoPackage domain tables
    
    Args:
        gpkg_path (str): Path to the GeoPackage file
        excel_data (dict): Excel data containig domain values
        domain_sheets (list): List of tuples containing (sheet_name, table_name) pairs
    """
    for sheet_name, table_name in domain_sheets:
        if sheet_name not in excel_data:
            print(f"Warning: Sheet '{sheet_name}' not found in Excel file. Skipping.")
            continue
            
        df = excel_data[sheet_name]
        if not {"code", "value"}.issubset(df.columns):
            print(f"Warning: Sheet '{sheet_name}' must contain 'code' and 'value' columns. Skipping.")
            continue
            
        layer = QgsVectorLayer(f"{gpkg_path}|layername={table_name}", table_name, "ogr")
        
        if layer.isValid():
            layer.startEditing()
            for _, row in df.iterrows():
                feature = QgsFeature(layer.fields())
                feature.setAttribute("code", str(row["code"]))
                feature.setAttribute("value", str(row["value"]))
                layer.addFeature(feature)
            
            success = layer.commitChanges()
            if success:
                print(f"Added values to {table_name} table from {sheet_name} sheet")
            else:
                print(f"Failed to add values to {table_name} table")
        else:
            print(f"Warning: Could not load layer {table_name}")

def configure_value_relation_widgets(layer, layer_name):
    """
    Configures Value Relation widgets for fields with different configurations
    
    Args:
        layer (QgsVectorLayer): The layer to configure widgets for
        layer_name (str): Name of the layer for logging purposes
    """

    for field_name, domain_layer_name in domain_fields_config.items():
        field_idx = layer.fields().indexOf(field_name)
        if field_idx != -1:
            try:
                target_layer = QgsProject.instance().mapLayersByName(domain_layer_name)[0]
                config = domain_config.copy()
                config['Layer'] = target_layer.id()
                layer.setEditorWidgetSetup(field_idx, QgsEditorWidgetSetup('ValueRelation', config))
                print(f"'{field_name}' field configured with domain Value Relation widget for '{layer_name}'")
            except IndexError:
                print(f"Warning: Domain layer '{domain_layer_name}' not found for '{field_name}' field")

def setup_relationships(loaded_layers):
    """Sets up relationships between layers based on configuration"""
    
    for rel_id, rel_config in relationships_config.items():
        referenced_layer = loaded_layers.get(rel_config['referenced_layer'])
        referencing_layer = loaded_layers.get(rel_config['referencing_layer'])
        
        if referenced_layer and referencing_layer:
            relation = QgsRelation()
            relation.setId(str(uuid.uuid4()))
            relation.setName(rel_id)
            relation.setReferencedLayer(referenced_layer.id())
            relation.setReferencingLayer(referencing_layer.id())
            relation.addFieldPair(rel_config['referencing_field'], rel_config['referenced_field'])
            relation.setStrength(rel_config['strength'])
            
            if relation.isValid():
                QgsProject.instance().relationManager().addRelation(relation)
                if rel_config['referencing_field'] == 'address_id':
                    referenced_layer.setDisplayExpression("address || ' ' || unit")
                elif rel_config['referencing_field'] == 'anchor_id':
                    referenced_layer.setDisplayExpression(f"attribute(get_feature('unit', 'id', unit_id), 'name')[{CONST_LANGUAGE}]")
                else:
                    referenced_layer.setDisplayExpression(f"name[{CONST_LANGUAGE}]")
                    
                print(f"Relationship {rel_id} configured successfully")
            else:
                print(f"Failed to create relationship {rel_id}")

# Main script starts here
# Select GeoPackage save path
save_path, _ = QFileDialog.getSaveFileName(None, "Save GeoPackage As", "", "GeoPackage (*.gpkg)")
if not save_path:
    raise Exception("No file path selected!")
if not save_path.lower().endswith(".gpkg"):
    save_path += ".gpkg"
gpkg_path = save_path.replace("\\", "/")
print(f"GeoPackage will be saved as: {gpkg_path}")

# Select Excel file with domain values
excel_path, _ = QFileDialog.getOpenFileName(
    None,
    "Select Excel File with Domain Values",
    "",
    "Excel Files (*.xlsx *.xls)"
)
if not excel_path:
    raise Exception("No Excel file selected.")

for layer in list(QgsProject.instance().mapLayers().values()):
    if gpkg_path in layer.dataProvider().dataSourceUri().replace("\\", "/"):
        QgsProject.instance().removeMapLayer(layer)
        del layer
QApplication.processEvents()
gc.collect()

if os.path.exists(gpkg_path):
    try:
        os.remove(gpkg_path)
        print("Existing GeoPackage deleted.")
    except PermissionError as e:
        raise Exception(f"Failed to delete GeoPackage: {e}")

# Create a new GeoPackage
for i, (layer_name, config) in enumerate(gpkg_layers_config.items()):
    geometry_type = QgsWkbTypes.NoGeometry if config['geometry'] == 'None' else QgsWkbTypes.parseType(config['geometry'])
    geometry_str = QgsWkbTypes.displayString(geometry_type)
    layer = QgsVectorLayer(f"{geometry_str}?crs=EPSG:4326", layer_name, "memory")
    pr = layer.dataProvider()

    fields = QgsFields()
    for attr, dtype in config['attributes'].items():
        if isinstance(dtype, dict):
            fields.append(QgsField(attr, dtype['type']))
        else:
            fields.append(QgsField(attr, dtype))
    pr.addAttributes(fields)
    layer.updateFields()

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = "GPKG"
    options.layerName = layer_name
    options.actionOnExistingFile = QgsVectorFileWriter.CreateOrOverwriteFile if i == 0 else QgsVectorFileWriter.CreateOrOverwriteLayer

    res, err = QgsVectorFileWriter.writeAsVectorFormatV2(
        layer,
        gpkg_path,
        QgsProject.instance().transformContext(),
        options
    )

    if res == QgsVectorFileWriter.NoError:
        print(f"Layer '{layer_name}' written.")
    else:
        print(f"Failed to write layer '{layer_name}': {err}")

# Create necessary tables for domain constraints
conn = QgsProviderRegistry.instance().providerMetadata('ogr').createConnection(gpkg_path, {})

conn.executeSql("""
    CREATE TABLE IF NOT EXISTS gpkg_data_column_constraints (
        constraint_name TEXT NOT NULL,
        constraint_type TEXT NOT NULL,
        value TEXT,
        min NUMERIC,
        min_is_inclusive BOOLEAN,
        max NUMERIC,
        max_is_inclusive BOOLEAN,
        description TEXT,
        CONSTRAINT gdcc_ntv UNIQUE (constraint_name, constraint_type, value)
    );
""")

conn.executeSql("""
    CREATE TABLE IF NOT EXISTS gpkg_data_columns (
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        name TEXT UNIQUE,
        title TEXT,
        description TEXT,
        mime_type TEXT,
        constraint_name TEXT,
        CONSTRAINT pk_gdc PRIMARY KEY (table_name, column_name),
        CONSTRAINT fk_gdc_tn FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name)
    );
""")

# Load Excel data
excel_data = pd.read_excel(excel_path, sheet_name=None)

if "domain_layer_field" not in excel_data:
    raise Exception("The Excel file must contain a sheet named 'domain_layer_field'.")

domain_map_df = excel_data["domain_layer_field"]
required_cols = {"constraint_name", "layer", "attribute"}
if not required_cols.issubset(domain_map_df.columns):
    raise Exception(f"'domain_layer_field' must contain columns: {required_cols}")

domain_sheets = [
    ("accessibility_category", "accessibility_domain"),
    ("access_control_category", "access_control_domain")
]

# Insert domain values into the GeoPackage
insert_domain_values(gpkg_path, excel_data, domain_sheets)

for _, row in domain_map_df.iterrows():
    constraint = row["constraint_name"]
    table = row["layer"]
    column = row["attribute"]

    if constraint not in excel_data:
        print(f"Warning: No sheet named '{constraint}' found. Skipping.")
        continue

    domain_df = excel_data[constraint]
    if not {"code", "value"}.issubset(domain_df.columns):
        print(f"Warning: Sheet '{constraint}' must contain 'code' and 'value' columns.")
        continue

    code_value_pairs = list(zip(domain_df["code"], domain_df["value"]))
    add_enum_domain(conn, constraint, code_value_pairs, table, column)

print("Enum domains successfully applied.")

# Create layer groups in the project
root = QgsProject.instance().layerTreeRoot()
imdf_group = root.addGroup('IMDF features')
domain_group = root.addGroup('Domain tables')
junction_group = root.addGroup('Junction tables')

# Load layers from the GeoPackage and add them to the project
loaded_layers = {}
for group_name, layers in layer_groups_config.items():
    if group_name == 'IMDF features':
        target_group = imdf_group
    elif group_name == 'Domain tables':
        target_group = domain_group
        layers = sorted(layers)  
    else:
        target_group = junction_group
        
    for layer_name in layers:
        if layer_name in gpkg_layers_config:
            uri = f"{gpkg_path}|layername={layer_name}"
            layer = QgsVectorLayer(uri, layer_name, "ogr")
            if layer.isValid():
                loaded_layers[layer_name] = layer
                QgsProject.instance().addMapLayer(layer, False)
                target_group.addLayer(layer)
                print(f"Layer '{layer_name}' loaded")

setup_relationships(loaded_layers)

for layer_name, layer in loaded_layers.items():
    # Get layer configuration
    layer_config = gpkg_layers_config[layer_name]
    
    # Configure form and constraints
    form_config = layer.editFormConfig()
    form_config.setLayout(QgsEditFormConfig.EditorLayout.DragAndDrop)
    
    # Apply not null constraints and configure relation reference widgets
    for field_name, field_config in layer_config['attributes'].items():
        field_idx = layer.fields().indexOf(field_name)
        if field_idx != -1:
            # Set not null constraint if specified
            if isinstance(field_config, dict) and field_config.get('notnull', False):
                constraints = QgsFieldConstraints()
                constraints.setConstraint(QgsFieldConstraints.ConstraintNotNull)
                layer.setFieldConstraint(field_idx, QgsFieldConstraints.ConstraintNotNull, QgsFieldConstraints.ConstraintStrengthHard)
                print(f"Not null constraint added for field '{field_name}' in layer '{layer_name}'")

    layer.setEditFormConfig(form_config)

    # Configure field values
    id_idx = layer.fields().indexOf('id')
    display_point_idx = layer.fields().indexOf('display_point')
    phone_idx = layer.fields().indexOf('phone')
    origin_type_idx = layer.fields().indexOf('origin_type')
    origin_unit_id_idx = layer.fields().indexOf('origin_unit_id')
    origin_opening_id_idx = layer.fields().indexOf('origin_opening_id')
    intermediary_type_idx = layer.fields().indexOf('intermediary_type')
    destination_type_idx = layer.fields().indexOf('destination_type')
    destination_unit_id_idx = layer.fields().indexOf('destination_unit_id')
    destination_opening_id_idx = layer.fields().indexOf('destination_opening_id')

    if id_idx != -1:
        layer.setEditorWidgetSetup(id_idx, QgsEditorWidgetSetup('UuidGenerator', {}))
        expression = "uuid('WithoutBraces')"
        layer.setDefaultValueDefinition(id_idx, QgsDefaultValue(expression))
        print(f"'id' field configured for '{layer_name}'")

    if display_point_idx != -1:
        expression = "concat(round(y(point_on_surface($geometry)), 7), ', ', round(x(point_on_surface($geometry)), 7))"
        layer.setDefaultValueDefinition(display_point_idx, QgsDefaultValue(expression))
        print(f"'display_point' field configured for '{layer_name}'")

    if phone_idx != -1:
        expression = "regexp_match(phone, '^\\\\+[1-9][0-9]{1,14}$')"
        constraints = QgsFieldConstraints()
        constraints.setConstraint(QgsFieldConstraints.ConstraintExpression)
        layer.setFieldConstraint(phone_idx, QgsFieldConstraints.ConstraintExpression, QgsFieldConstraints.ConstraintStrengthSoft)
        layer.setConstraintExpression(phone_idx, expression, "Needs to be a valid E.164 phone number")
        print(f"'phone' field configured for '{layer_name}'")

    if origin_type_idx != -1:
        expression = "origin_type in ('unit', 'opening')"
        constraints = QgsFieldConstraints()
        constraints.setConstraint(QgsFieldConstraints.ConstraintExpression)
        layer.setFieldConstraint(origin_type_idx, QgsFieldConstraints.ConstraintExpression, QgsFieldConstraints.ConstraintStrengthSoft)
        layer.setConstraintExpression(origin_type_idx, expression, "Expects unit or opening as value")
        print(f"'origin_type' field configured for '{layer_name}'")
    
    if intermediary_type_idx != -1:
        expression = "intermediary_type in ('unit', 'opening')"
        constraints = QgsFieldConstraints()
        constraints.setConstraint(QgsFieldConstraints.ConstraintExpression)
        layer.setFieldConstraint(intermediary_type_idx, QgsFieldConstraints.ConstraintExpression, QgsFieldConstraints.ConstraintStrengthSoft)
        layer.setConstraintExpression(intermediary_type_idx, expression, "Expects unit or opening as value")
        print(f"'intermediary_type' field configured for '{layer_name}'")
    
    if destination_type_idx != -1:
        expression = "destination_type in ('unit', 'opening')"
        constraints = QgsFieldConstraints()
        constraints.setConstraint(QgsFieldConstraints.ConstraintExpression)
        layer.setFieldConstraint(destination_type_idx, QgsFieldConstraints.ConstraintExpression, QgsFieldConstraints.ConstraintStrengthSoft)
        layer.setConstraintExpression(destination_type_idx, expression, "Expects unit or opening as value")
        print(f"'destination_type' field configured for '{layer_name}'")

    # Configures the drag and drop designer for the relationship and opening layers
    if layer_name == 'relationship':

        form_config = layer.editFormConfig()
        form_config.setLayout(QgsEditFormConfig.EditorLayout.DragAndDrop)
        layer.setEditFormConfig(form_config)
        
        root = form_config.invisibleRootContainer()
        root.clear()
        
        fid_field = QgsAttributeEditorField("fid", 0, root)
        root.addChildElement(fid_field)
        id_field = QgsAttributeEditorField("id", id_idx, root)
        root.addChildElement(id_field)
        category_field = QgsAttributeEditorField("category", layer.fields().indexOf('category'), root)
        root.addChildElement(category_field)
        direction_field = QgsAttributeEditorField("direction", layer.fields().indexOf('direction'), root)
        root.addChildElement(direction_field)
        origin_type_field = QgsAttributeEditorField("origin_type", origin_type_idx, root)
        root.addChildElement(origin_type_field)

        origin_container = QgsAttributeEditorContainer("origin", root)
        origin_container.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("origin_type = 'unit'"), True)
        origin_container.setVisibilityExpression(visibility_expr)
        root.addChildElement(origin_container)
        origin_unit_id_field = QgsAttributeEditorField("origin_unit_id", origin_unit_id_idx, origin_container)
        origin_container.addChildElement(origin_unit_id_field)
        
        origin_container_1 = QgsAttributeEditorContainer("origin", root)
        origin_container_1.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("origin_type = 'opening'"), True)
        origin_container_1.setVisibilityExpression(visibility_expr)
        root.addChildElement(origin_container_1)
        origin_opening_id_field = QgsAttributeEditorField("origin_opening_id", origin_opening_id_idx, origin_container_1)
        origin_container_1.addChildElement(origin_opening_id_field)

        intermediary_type_field = QgsAttributeEditorField("intermediary_type", intermediary_type_idx, root)
        root.addChildElement(intermediary_type_field)

        intermediary_container = QgsAttributeEditorContainer("intermediary", root)
        intermediary_container.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("intermediary_type = 'unit'"), True)
        intermediary_container.setVisibilityExpression(visibility_expr)
        root.addChildElement(intermediary_container)
        
        intermediary_container_1 = QgsAttributeEditorContainer("intermediary", root)
        intermediary_container_1.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("intermediary_type = 'opening'"), True)
        intermediary_container_1.setVisibilityExpression(visibility_expr)
        root.addChildElement(intermediary_container_1)

        destination_type_field = QgsAttributeEditorField("destination_type", destination_type_idx, root)
        root.addChildElement(destination_type_field)

        destination_container = QgsAttributeEditorContainer("destination", root)
        destination_container.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("destination_type = 'unit'"), True)
        destination_container.setVisibilityExpression(visibility_expr)
        root.addChildElement(destination_container)
        destination_unit_id_field = QgsAttributeEditorField("destination_unit_id", destination_unit_id_idx, destination_container)
        destination_container.addChildElement(destination_unit_id_field)
        
        destination_container_1 = QgsAttributeEditorContainer("destination", root)
        destination_container_1.setIsGroupBox(True)
        visibility_expr = QgsOptionalExpression(QgsExpression("destination_type = 'opening'"), True)
        destination_container_1.setVisibilityExpression(visibility_expr)
        root.addChildElement(destination_container_1)
        destination_opening_id_field = QgsAttributeEditorField("destination_opening_id", destination_opening_id_idx, destination_container_1)
        destination_container_1.addChildElement(destination_opening_id_field)

        hours_field = QgsAttributeEditorField("hours", layer.fields().indexOf('hours'), root)
        root.addChildElement(hours_field)
    
        print(f"Drag and drop designer enabled for '{layer_name}' layer configured containers")
    
    if layer_name == 'opening':
        form_config = layer.editFormConfig()
        form_config.setLayout(QgsEditFormConfig.EditorLayout.DragAndDrop)
        layer.setEditFormConfig(form_config)
        
        root = form_config.invisibleRootContainer()
        root.clear()
        
        fid_field = QgsAttributeEditorField("fid", 0, root)
        root.addChildElement(fid_field)
        id_field = QgsAttributeEditorField("id", id_idx, root)
        root.addChildElement(id_field)
        category_field = QgsAttributeEditorField("category", layer.fields().indexOf('category'), root)
        root.addChildElement(category_field)
        accessibility_field = QgsAttributeEditorField("accessibility", layer.fields().indexOf('accessibility'), root)
        root.addChildElement(accessibility_field)
        access_control_field = QgsAttributeEditorField("access_control", layer.fields().indexOf('access_control'), root)
        root.addChildElement(access_control_field)

        door_container = QgsAttributeEditorContainer("door", root)
        door_container.setIsGroupBox(True)
        root.addChildElement(door_container)
        type_field = QgsAttributeEditorField("type", layer.fields().indexOf('type'), door_container)
        automatic_field = QgsAttributeEditorField("automatic", layer.fields().indexOf('automatic'), door_container)
        material_field = QgsAttributeEditorField("material", layer.fields().indexOf('material'), door_container)
        door_container.addChildElement(type_field)
        door_container.addChildElement(automatic_field)
        door_container.addChildElement(material_field)

        name_field = QgsAttributeEditorField("name", layer.fields().indexOf('name'), root)
        root.addChildElement(name_field)
        alt_name_field = QgsAttributeEditorField("alt_name", layer.fields().indexOf('alt_name'), root)
        root.addChildElement(alt_name_field)
        display_point_field = QgsAttributeEditorField("display_point", display_point_idx, root)
        root.addChildElement(display_point_field)
        level_id_field = QgsAttributeEditorField("level_id", layer.fields().indexOf('level_id'), root)
        root.addChildElement(level_id_field)

        print(f"Drag and drop designer enabled for '{layer_name}' layer configured containers")

    if layer_name == 'occupant':
        form_config = layer.editFormConfig()
        form_config.setLayout(QgsEditFormConfig.EditorLayout.DragAndDrop)
        layer.setEditFormConfig(form_config)

        root = form_config.invisibleRootContainer()
        root.clear()

        fid_field = QgsAttributeEditorField("fid", 0, root)
        root.addChildElement(fid_field)
        id_field = QgsAttributeEditorField("id", id_idx, root)
        root.addChildElement(id_field)
        name_field = QgsAttributeEditorField("name", layer.fields().indexOf('name'), root)
        root.addChildElement(name_field)
        category_field = QgsAttributeEditorField("category", layer.fields().indexOf('category'), root)
        root.addChildElement(category_field)
        anchor_id_field = QgsAttributeEditorField("anchor_id", layer.fields().indexOf('anchor_id'), root)
        root.addChildElement(anchor_id_field)
        hours_field = QgsAttributeEditorField("hours", layer.fields().indexOf('hours'), root)
        root.addChildElement(hours_field)
        phone_field = QgsAttributeEditorField("phone", layer.fields().indexOf('phone'), root)
        root.addChildElement(phone_field)
        website_field = QgsAttributeEditorField("website", layer.fields().indexOf('website'), root)
        root.addChildElement(website_field)

        validity_container = QgsAttributeEditorContainer("validity", root)
        validity_container.setIsGroupBox(True)
        root.addChildElement(validity_container)
        start_field = QgsAttributeEditorField("start", layer.fields().indexOf('start'), validity_container)
        end_field = QgsAttributeEditorField("end", layer.fields().indexOf('end'), validity_container)
        modified_field = QgsAttributeEditorField("modified", layer.fields().indexOf('modified'), validity_container)
        validity_container.addChildElement(start_field)
        validity_container.addChildElement(end_field)
        validity_container.addChildElement(modified_field)

        correlation_id_field = QgsAttributeEditorField("correlation_id", layer.fields().indexOf('correlation_id'), root)
        root.addChildElement(correlation_id_field)

        print(f"Drag and drop designer enabled for '{layer_name}' layer configured containers")

    configure_value_relation_widgets(layer, layer_name)

print("Layers loaded and configured!")

# Save the configured project to the GeoPackage
project_name = os.path.splitext(os.path.basename(gpkg_path))[0]
project = QgsProject.instance()
project.setTitle(project_name)

try:
    project_uri = f"geopackage://{gpkg_path}?projectName={project_name}"
    
    if project.write(project_uri):
        print(f"Project '{project_name}' saved to GeoPackage successfully")
    else:
        print(f"Failed to save project '{project_name}' to GeoPackage")
        backup_path = gpkg_path.replace('.gpkg', '.qgz')
        if project.write(backup_path):
            print(f"Project saved as backup file: {backup_path}")
except Exception as e:
    print(f"Error saving project: {str(e)}")