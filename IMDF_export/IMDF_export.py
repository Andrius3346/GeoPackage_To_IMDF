import geopandas as gpd
import fiona
import os
import json
import zipfile
from datetime import datetime, timezone
import pandas as pd
import config

def get_junction_table_ids(gpkg_path, junction_table, id_field, reference_field, reference_value):
    """Get array of IDs from junction table for a given reference value"""
    try:
        # Read junction table
        junction_df = gpd.read_file(gpkg_path, layer=junction_table)
        
        # Convert reference_value to string for comparison
        reference_value = str(reference_value)
        
        # Convert reference field values to strings for comparison
        junction_df[reference_field] = junction_df[reference_field].astype(str)
        
        # Filter and get IDs
        matched_rows = junction_df[junction_df[reference_field] == reference_value]
        
        if matched_rows.empty:
            return None
        
        # Convert IDs to strings and get as list
        ids = matched_rows[id_field].astype(str).tolist()
        print(f"Found {len(ids)} IDs in {junction_table} for {reference_field}={reference_value}")
        return ids
        
    except Exception as e:
        print(f"Warning: Error processing junction table {junction_table}: {e}")
        return None

def process_junction_tables(row_dict, feature_type, gpkg_path):
    """Process junction tables and add _ids fields to properties"""
    
    feature_id = row_dict.get('id')
    print(f"Processing {feature_type} feature with ID: {feature_id}")

    junction_mappings = config.junction_mappings
    
    # Check if feature type has junction tables
    if feature_type not in junction_mappings:
        return

    # Process each _ids field for the feature type
    for field_name, mapping in junction_mappings[feature_type].items():
        ids = get_junction_table_ids(
            gpkg_path,
            mapping['table'],
            mapping['id'],
            mapping['ref'],
            feature_id
        )
        # Only add field if IDs were found
        if ids:
            row_dict[field_name] = ids
        else:
            row_dict[field_name] = None  # Set to null if no IDs found

def convert_gpkg_array_to_list(value):
    """Convert gpkg array string to Python list."""
    if not isinstance(value, str) or not value.startswith('{') or not value.endswith('}'):
        return value
    
    items = value[1:-1].split(',')
    return [item.strip().strip('"').strip("'") for item in items if item.strip()]

def is_empty_value(value):
    """Check if value is an empty array or dictionary"""
    return isinstance(value, (list, dict)) and len(value) == 0

def process_address_fields(row_dict, feature_type):
    """Force string type for address feature fields"""
    if feature_type == 'address':
        for key in ['unit', 'postal_code', 'postal_code_ext', 'postal_code_vanity']:
            row_dict[key] = str(row_dict.get(key)) if row_dict.get(key) is not None else None

def process_name_fields(row_dict):
    """Handle name fields"""
    for key in ['name', 'alt_name', 'short_name']:
        value = row_dict.get(key)
        if isinstance(value, str):
            try:
                parsed_value = json.loads(value)
                row_dict[key] = None if is_empty_value(parsed_value) else parsed_value
            except json.JSONDecodeError:
                continue

def process_other_fields(row_dict, key, value):
    """Handle gpkg array strings and JSON string fields"""
    pg_array = convert_gpkg_array_to_list(value)
    if isinstance(pg_array, list):
        return None if len(pg_array) == 0 else pg_array

    if isinstance(value, str):
        try:
            parsed_value = json.loads(value)
            return None if is_empty_value(parsed_value) else parsed_value
        except json.JSONDecodeError:
            return value

    if is_empty_value(value):
        return None

    return value

def process_display_point(row_dict):
    """Handle display_point"""
    if 'display_point' in row_dict and isinstance(row_dict['display_point'], str):
        try:
            lat_str, lon_str = row_dict['display_point'].split(',')
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
            return {
                "type": "Point",
                "coordinates": [lon, lat]
            }
        except Exception:
            print(f"Warning: Could not parse display_point '{row_dict['display_point']}'")
    return row_dict.get('display_point')

def export_layers_custom_format(gpkg_path, output_folder, layers_to_export):
    available_layers = fiona.listlayers(gpkg_path)
    exported_files = []

    for layer in layers_to_export:
        if layer not in available_layers:
            print(f"Layer '{layer}' not found. Available layers: {available_layers}")
            continue

        print(f"Reading layer: {layer}")
        gdf = gpd.read_file(gpkg_path, layer=layer)

        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, f"{layer}.geojson")

        if gdf.empty:
            print(f"Warning: Layer '{layer}' has no features. Skipping export.")
            continue

        print(f"Exporting layer as GeoJSON FeatureCollection: {output_path}")
        # Pass gpkg_path to export_spatial_layer
        export_spatial_layer(gdf, output_path, feature_type=layer, gpkg_path=gpkg_path)
        exported_files.append(output_path)

    return exported_files

def process_door_fields(properties):
    """Process door fields for opening layer"""
    type_val = properties.pop('type', None)
    automatic = properties.pop('automatic', False)
    material = properties.pop('material', None)

    if automatic or material or type_val:
        door_dict = {}
        if type_val:
            door_dict['type'] = type_val
        if automatic:
            door_dict['automatic'] = automatic
        if material:
            door_dict['material'] = material

        properties['door'] = door_dict
    else:
        properties['door'] = None

def process_validity_fields(properties):
    """Process validity fields for occupant layer"""
    start = properties.pop('start', None)
    end = properties.pop('end', None)
    modified = properties.pop('modified', None)

    start = start.isoformat() if pd.notnull(start) and hasattr(start, 'isoformat') else None
    end = end.isoformat() if pd.notnull(end) and hasattr(end, 'isoformat') else None
    modified = modified.isoformat() if pd.notnull(modified) and hasattr(modified, 'isoformat') else None

    if any(x is not None for x in [start, end, modified]):
        validity_dict = {}
        if start:
            validity_dict['start'] = start
        if end:
            validity_dict['end'] = end
        if modified:
            validity_dict['modified'] = modified

        properties['validity'] = validity_dict
    else:
        properties['validity'] = None

def format_relationship_properties(properties):
    """Format relationship properties"""
    formatted = {
        'category': properties.get('category'),
        'direction': properties.get('direction'),
        'origin': None,
        'intermediary': None,
        'destination': None,
        'hours': properties.get('hours')
    }

    # Handle origin
    origin_type = properties.pop('origin_type', None)
    origin_id = properties.pop('origin_unit_id', None) or properties.pop('origin_opening_id', None)
    if origin_type and origin_id:
        formatted['origin'] = {
            'id': origin_id,
            'feature_type': origin_type
        }

    # Handle intermediary
    intermediary_ids = None
    intermediary_type = None

    if properties.get('unit_ids'):
        intermediary_ids = properties.pop('unit_ids')
        intermediary_type = 'unit'
    elif properties.get('opening_ids'):
        intermediary_ids = properties.pop('opening_ids')
        intermediary_type = 'opening'

    if intermediary_ids:
        # Ensure intermediary_ids is a list
        if not isinstance(intermediary_ids, list):
            intermediary_ids = [intermediary_ids]

        formatted['intermediary'] = [{
            'id': id_value,
            'feature_type': intermediary_type
        } for id_value in intermediary_ids]

    # Handle destination
    destination_type = properties.pop('destination_type', None)
    destination_id = properties.pop('destination_unit_id', None) or properties.pop('destination_opening_id', None)
    if destination_type and destination_id:
        formatted['destination'] = {
            'id': destination_id,
            'feature_type': destination_type
        }
    
    # Remove original fields
    properties.clear()
    properties.update(formatted)

    return properties

def process_feature_properties(row_dict, feature_type):
    """Process all fields of a feature"""
    process_address_fields(row_dict, feature_type)
    process_name_fields(row_dict)

    for key, value in row_dict.items():
        if key in ['unit', 'postal_code', 'postal_code_ext', 'postal_code_vanity', 'name', 'alt_name', 'short_name']:
            continue

        processed_value = process_other_fields(row_dict, key, value)
        row_dict[key] = processed_value

    display_point = process_display_point(row_dict)
    if display_point:
        row_dict['display_point'] = display_point

    if feature_type == 'opening':
        process_door_fields(row_dict)
    elif feature_type == 'occupant':
        process_validity_fields(row_dict)
    elif feature_type == 'relationship':
        row_dict = format_relationship_properties(row_dict)

def export_spatial_layer(gdf, output_path, feature_type, gpkg_path):
    features = []
    
    for _, row in gdf.iterrows():
        row_dict = row.to_dict()
        
        # Process junction tables to add _ids fields
        process_junction_tables(row_dict, feature_type, gpkg_path)
        
        feature_id = row_dict.pop('id', None)
        geometry = row_dict.pop('geometry', None)

        if feature_id is None:
            continue

        # Process all fields
        process_feature_properties(row_dict, feature_type)

        feature = {
            "id": feature_id,
            "type": "Feature",
            "feature_type": feature_type,
            "geometry": geometry.__geo_interface__ if geometry else None,
            "properties": row_dict
        }
        features.append(feature)

    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(feature_collection, f, ensure_ascii=False, indent=2)

def create_manifest_json(output_folder):
    """Creates a manifest.json file with metadata about the export."""
    manifest = {
        "version": "1.0.0",
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "generated_by": "Vilnius University",
        "language": config.language
    }

    manifest_path = os.path.join(output_folder, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

    print(f"Created manifest at {manifest_path}")
    return manifest_path

def create_zip_archive(output_folder, files_to_zip, zip_name="exported_imdf.zip"):
    """Creates a ZIP archive of the exported files."""
    zip_path = os.path.join(output_folder, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files_to_zip:
            arcname = os.path.basename(file_path)
            zipf.write(file_path, arcname)
    print(f"Created ZIP archive: {zip_path}")

if __name__ == "__main__":
    
    gpkg_file = config.gpkg_path
    output_dir = config.output_dir

    excluded_layers = config.excluded_layers
    all_layers = fiona.listlayers(gpkg_file)
    layers = [layer for layer in all_layers if layer not in excluded_layers]

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Export files and create zip
    exported_files = export_layers_custom_format(gpkg_file, output_dir, layers)
    manifest_path = create_manifest_json(output_dir)
    exported_files.append(manifest_path)
    create_zip_archive(output_dir, exported_files)

    print("IMDF zip file created successfully!")