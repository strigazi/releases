# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import textwrap

import fixtures
import mock
from oslotest import base
import yaml

from openstack_releases.cmds import validate


class TestValidateLaunchpad(base.BaseTestCase):

    def test_no_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {'launchpad': 'nonsense-name'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_launchpad_name(self):
        warnings = []
        errors = []
        validate.validate_launchpad(
            {'launchpad': 'oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateTeam(base.BaseTestCase):

    def test_no_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {},
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {'team': 'nonsense-name'},
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))

    def test_valid_name(self):
        warnings = []
        errors = []
        validate.validate_team(
            {'team': 'oslo'},
            {'oslo': None},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateReleaseNotes(base.BaseTestCase):

    def test_no_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_invalid_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {'release-notes': 'http://docs.openstack.org/no-such-page'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_link(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {'release-notes':
             'http://docs.openstack.org/releasenotes/oslo.config'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_invalid_link_multi(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {
                'release-notes': {
                    'openstack/releases': 'http://docs.openstack.org/no-such-page',
                }
            },
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_link_multi(self):
        warnings = []
        errors = []
        validate.validate_release_notes(
            {
                'release-notes': {
                    'openstack/releases': 'http://docs.openstack.org/releasenotes/oslo.config',
                }
            },
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateDeliverableType(base.BaseTestCase):

    def test_no_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_invalid_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {'type': 'not-valid'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_type(self):
        warnings = []
        errors = []
        validate.validate_type(
            {'type': 'library'},
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))


class TestGetModel(base.BaseTestCase):

    def test_no_model_series(self):
        self.assertEqual(
            'UNSPECIFIED',
            validate.get_model({}, 'ocata'),
        )

    def test_no_model_independent(self):
        self.assertEqual(
            'independent',
            validate.get_model({}, '_independent'),
        )

    def test_with_model_independent(self):
        self.assertEqual(
            'independent',
            validate.get_model({'release-model': 'set'}, '_independent'),
        )

    def test_with_model_series(self):
        self.assertEqual(
            'set',
            validate.get_model({'release-model': 'set'}, 'ocata'),
        )


class TestValidateModel(base.BaseTestCase):

    def test_no_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_no_model_independent(self):
        warnings = []
        errors = []
        validate.validate_model(
            {},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_model_independent_match(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'independent'},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_model_independent_nomatch(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'cycle-with-intermediary'},
            '_independent',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_with_independent_and_model(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'independent'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_with_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'cycle-with-intermediary'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_with_unknown_model_series(self):
        warnings = []
        errors = []
        validate.validate_model(
            {'release-model': 'not-a-model'},
            'ocata',
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateReleases(base.BaseTestCase):

    def setUp(self):
        super(TestValidateReleases, self).setUp()
        self.tmpdir = self.useFixture(fixtures.TempDir()).path

    @mock.patch('openstack_releases.project_config.require_release_jobs_for_repo')
    def test_check_release_jobs(self, check_jobs):
        deliverable_info = {
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))
        check_jobs.assert_called_once()

    def test_invalid_hash(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '0.1',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'this-is-not-a-hash'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_existing(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_no_such_hash(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.0.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'de2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(1, len(errors))

    def test_mismatch_existing(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # hash from the previous release
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_not_descendent(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.4.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]},
                {'version': '1.4.999',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      # a commit on stable/mitaka instead of stable/newton
                      'hash': 'e92b85ec64ac74598983a90bd2f3e1cf232ba9d5'},
                 ]},
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_new_not_at_end(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1.3.999',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'e87dc55a48387d2b8b8c46e02a342c27995dacb1'},
                 ]},
                {'version': '1.4.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'c6278ba1a8167447a5f52bdb92c2790abc5d0f87'},
                 ]},
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(1, len(errors))

    @mock.patch('openstack_releases.versionutils.validate_version')
    def test_invalid_version(self, validate_version):
        # Set up the nested validation function to produce an error,
        # even though there is nothing else wrong with the
        # inputs. That ensures we only get the 1 error back.
        validate_version.configure_mock(
            return_value=['an error goes here'],
        )
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '99.5.0',
                 'projects': [
                     {'repo': 'openstack/automaton',
                      'hash': 'be2885f544637e6ee6139df7dc7bf937925804dd'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_releases(
            deliverable_info,
            {'validate-projects-by-name': {}},
            'ocata',
            self.tmpdir,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(1, len(errors))


class TestValidateNewReleases(base.BaseTestCase):

    team_data_yaml = textwrap.dedent("""
    Release Management:
      ptl:
        name: Doug Hellmann
        irc: dhellmann
        email: doug@doughellmann.com
      irc-channel: openstack-release
      mission: >
        Coordinating the release of OpenStack deliverables, by defining the
        overall development cycle, release models, publication processes,
        versioning rules and tools, then enabling project teams to produce
        their own releases.
      url: https://wiki.openstack.org/wiki/Release_Management
      tags:
        - team:diverse-affiliation
      deliverables:
        release-schedule-generator:
          repos:
            - openstack/release-schedule-generator
        release-test:
          repos:
            - openstack/release-test
        release-tools:
          repos:
            - openstack-infra/release-tools
        releases:
          repos:
            - openstack/releases
        reno:
          repos:
            - openstack/reno
          docs:
            contributor: http://docs.openstack.org/developer/reno/
        specs-cookiecutter:
          repos:
            - openstack-dev/specs-cookiecutter
    """)

    team_data = yaml.load(team_data_yaml)

    def test_all_repos(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                     {'repo': 'openstack/release-test',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))

    def test_extra_repo(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                     {'repo': 'openstack/release-test',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                     {'repo': 'openstack-infra/release-tools',
                      'hash': '685da43147c3bedc24906d5a26839550f2e962b1'},
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))

    def test_missing_repo(self):
        deliverable_info = {
            'artifact-link-mode': 'none',
            'releases': [
                {'version': '1000.0.0',
                 'projects': [
                 ]}
            ],
        }
        warnings = []
        errors = []
        validate.validate_new_releases(
            deliverable_info,
            'release-test.yaml',
            self.team_data,
            warnings.append,
            errors.append,
        )
        self.assertEqual(1, len(warnings))
        self.assertEqual(0, len(errors))


class TestValidateBranchPrefixes(base.BaseTestCase):

    def test_invalid_prefix(self):
        deliverable_info = {
            'branches': [
                {'name': 'invalid/branch'},
            ],
        }
        warnings = []
        errors = []
        validate.validate_branch_prefixes(
            deliverable_info,
            warnings.append,
            errors.append,
        )
        self.assertEqual(0, len(warnings))
        self.assertEqual(1, len(errors))

    def test_valid_prefix(self):
        warnings = []
        errors = []
        for prefix in validate._VALID_BRANCH_PREFIXES:
            deliverable_info = {
                'branches': [
                    {'name': '%s/branch' % prefix},
                ],
            }
            validate.validate_branch_prefixes(
                deliverable_info,
                warnings.append,
                errors.append,
            )
        self.assertEqual(0, len(warnings))
        self.assertEqual(0, len(errors))
        self.assertEqual(0, len(errors))