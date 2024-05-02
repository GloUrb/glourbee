import unittest
import logging

from glourbee import assets_management

import ee
credentials = ee.ServiceAccountCredentials(
    'samuel@ee-glourb.iam.gserviceaccount.com', './earthengine-key.json')
ee.Initialize(credentials)
ee_project_name = 'ee-glourb'


class TestExtractionZones(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO)
    
    def test_create(self):
        self.logger.info('Creating asset')
        ds = assets_management.ExtractionZones(local_file='./tests/data/lhasa_testing.shp',
                                               ee_project_name=ee_project_name,
                                               asset_uuid='test_create')
        self.assertIsInstance(ds, assets_management.ExtractionZones)

        self.logger.info('Cleanup')
        ds.delete()

    def test_upload(self):
        self.logger.info('Creating asset')
        ds = assets_management.ExtractionZones(local_file='./tests/data/lhasa_testing.shp',
                                               ee_project_name=ee_project_name,
                                               asset_uuid='test_upload')

        self.logger.info('Deleting previous test residuals')
        ds.delete()
        ds.update_gee_state()

        self.logger.info('Uploading asset to GEE')
        ds.upload_to_gee(silent=True)
        self.assertTrue(len(ds.linked_tasks) > 0)

        self.logger.info('Waiting for tasks to complete')
        ds.wait_for_tasks(silent=True)

        self.assertEqual(len(ds.gee_assets), ds.len)
        self.assertEqual(ds.gee_state, 'complete')

        self.logger.info('Cleanup')
        ds.delete()

    def test_delete(self):
        self.logger.info('Creating asset')
        ds = assets_management.ExtractionZones(local_file='./tests/data/lhasa_testing.shp',
                                               ee_project_name=ee_project_name,
                                               asset_uuid='test_delete')
        
        self.logger.info('Deleting previous test residuals')
        ds.delete()
        ds.update_gee_state()

        self.logger.info('Uploading zones to GEE')
        ds.upload_to_gee(silent=True)
        ds.wait_for_tasks(silent=True)

        self.logger.info('Deleting asset')
        ds.delete()

        zones = ee.data.listAssets({'parent': f'projects/{ee_project_name}/assets/extraction_zones'})
        zone_names = [z['name'] for z in zones['assets']]
        self.assertFalse(ds.gee_dir in zone_names)


class TestMetrics(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO)
    
    def test_create(self):
        self.logger.info('Creating asset')
        zones = assets_management.ExtractionZones(local_file='./tests/data/lhasa_testing.shp',
                                                ee_project_name=ee_project_name,
                                                asset_uuid='test_metrics_create')
        
        self.logger.info('Deleting previous test residuals')
        zones.delete()
        zones.update_gee_state()

        ds = assets_management.MetricsDataset(ee_project_name=ee_project_name,
                                              asset_uuid='test_metrics_create_ds',
                                              parent_zones=zones)

        self.assertIsInstance(ds, assets_management.MetricsDataset)

        self.logger.info('Cleanup')
        ds.delete()
