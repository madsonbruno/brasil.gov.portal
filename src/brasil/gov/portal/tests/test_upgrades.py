# -*- coding: utf-8 -*-
from brasil.gov.portal.testing import INTEGRATION_TESTING

import unittest


class UpgradeBaseTestCase(unittest.TestCase):

    layer = INTEGRATION_TESTING
    profile_id = u'brasil.gov.portal:default'

    def setUp(self):
        self.portal = self.layer['portal']
        self.setup = self.portal['portal_setup']
        self.setup.setLastVersionForProfile(self.profile_id, self.from_)

    def _get_upgrade_step_by_title(self, title):
        """Return the upgrade step that matches the title specified."""
        self.setup.setLastVersionForProfile(self.profile_id, self.from_)
        upgrades = self.setup.listUpgrades(self.profile_id)
        steps = [s for s in upgrades[0] if s['title'] == title]
        return steps[0] if steps else None

    def _do_upgrade(self, step):
        """Execute an upgrade step."""
        request = self.layer['request']
        request.form['profile_id'] = self.profile_id
        request.form['upgrades'] = [step['id']]
        self.setup.manage_doUpgrades(request=request)


class To1001TestCase(UpgradeBaseTestCase):

    from_ = '10803'
    to_ = '1001'

    def test_profile_version(self):
        version = self.setup.getLastVersionForProfile(self.profile_id)[0]
        self.assertEqual(version, self.from_)

    @unittest.expectedFailure
    def test_registered_steps(self):
        steps = len(self.setup.listUpgrades(self.profile_id)[0])
        self.assertEqual(steps, 0)

    def test_remove_styles(self):
        # address also an issue with Setup permission
        title = u'Move styles to brasil.gov.temas package'
        step = self._get_upgrade_step_by_title(title)
        self.assertIsNotNone(step)

        # simulate state on previous version
        from brasil.gov.portal.upgrades.v1001 import STYLES
        css_tool = api.portal.get_tool('portal_css')
        for css in STYLES:
            css_tool.registerResource(id=css)
            self.assertIn(css, css_tool.getResourceIds())

        # run the upgrade step to validate the update
        self._do_upgrade_step(step)
        for css in STYLES:
            self.assertNotIn(css, css_tool.getResourceIds())
