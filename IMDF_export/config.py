junction_mappings = {
        'level': {
            'building_ids': {'table': 'level_building', 'id': 'building_id', 'ref': 'level_id'}
        },
        'footprint': {
            'building_ids': {'table': 'footprint_building', 'id': 'building_id', 'ref': 'footprint_id'}
        },
        'geofence': {
            'building_ids': {'table': 'geofence_building', 'id': 'building_id', 'ref': 'geofence_id'},
            'level_ids': {'table': 'geofence_level', 'id': 'level_id', 'ref': 'geofence_id'},
            'parents': {'table': 'geofence_parent', 'id': 'parent_id', 'ref': 'child_id'}
        },
        'section': {
            'parents': {'table': 'section_parent', 'id': 'parent_id', 'ref': 'child_id'}
        },
        'amenity': {
            'unit_ids': {'table': 'amenity_unit', 'id': 'unit_id', 'ref': 'amenity_id'}
        },
        'relationship': {
            'opening_ids': {'table': 'relationship_opening', 'id': 'opening_id', 'ref': 'relationship_id'},
            'unit_ids': {'table': 'relationship_unit', 'id': 'unit_id', 'ref': 'relationship_id'}
        }
    }

excluded_layers = [
        'access_control_domain', 
        'accessibility_domain',
        'level_building',
        'geofence_level',
        'geofence_building',
        'footprint_building',
        'geofence_parent',
        'section_parent',
        'relationship_opening',
        'relationship_unit',
        'amenity_unit'
    ]

# Language code for the IMDF manifest JSON
language = "lt-LT"

# Path to the GeoPackage file
# Update this path to your GeoPackage file
gpkg_path = r""

# Output directory for the IMDF files
# Update this path to your desired output directory
output_dir = r""