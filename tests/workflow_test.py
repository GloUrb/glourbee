import unittest
import logging

from glourbee import (
    assets_management,
    workflow
)

import ee
credentials = ee.ServiceAccountCredentials(
    'samuel@ee-glourb.iam.gserviceaccount.com', './earthengine-key.json')
ee.Initialize(credentials)
ee_project_name = 'ee-glourb'

class TestWorkflow(unittest.TestCase):
    logger = logging.getLogger(__name__)
    logging.basicConfig(format = '%(asctime)s %(module)s %(levelname)s: %(message)s',
                    datefmt = '%m/%d/%Y %I:%M:%S %p', level = logging.INFO)

    def setUp(self):
        self.logger.info('Setting up extraction zones')
        self.zones = assets_management.ExtractionZones(local_file='./tests/data/lhasa_testing.shp',
                                                ee_project_name='ee-glourb',
                                                asset_uuid='test_workflow')
        
        if self.zones.gee_state != 'complete':
            self.logger.info('Uploading extraction zones to GEE')
            # Delete previous test residuals
            self.zones.delete()
            self.zones.update_gee_state()
            
            self.zones.upload_to_gee(silent=True)
            self.zones.wait_for_tasks(silent=True)

            self.zones.update_gee_state()
        else:
            self.logger.info('Extraction zones already uploaded to GEE')

    
    def test_start_and_cancel_workflow(self):
        self.logger.info('Starting metrics calculation workflow for Landsat images')
        metrics_ds = workflow.startWorkflow(zones_dataset=self.zones,
                  satellite_type = 'Landsat',
                  start = '1990-01-01',
                  end = '1990-01-31',
                  mosaic_same_day=False)
        
        self.assertTrue(len(metrics_ds.linked_tasks) > 0)

        metrics_ds.cancel_linked_tasks(silent=False)
        # TODO: assert that all tasks are cancelled

        metrics_ds.delete(silent=False)

    def test_landsat_workflow(self):
        self.logger.info('Starting metrics calculation workflow for Landsat images')
        metrics_ds = workflow.startWorkflow(zones_dataset=self.zones,
                  satellite_type = 'Landsat',
                  start = '1990-01-01',
                  end = '1990-01-31',
                  mosaic_same_day=False)
        
        self.assertTrue(len(metrics_ds.linked_tasks) > 0)

        metrics_ds.wait_for_tasks(silent=False)
        self.assertTrue(metrics_ds.gee_state == 'complete')

        metrics_ds.delete(silent=False)