"""Standalone no-Django tests of source-grounded dynamic generation planning."""
import unittest
from ai_onboarding.sico_case_coverage import make_coverage_plan, plan_generation_queue


def requirement(index, description):
    return {
        'requirement_id': f'id-{index}',
        'reference': f'R-{index}',
        'description': description,
        'requirement_name': f'Control {index}',
    }


ROWS = [
    requirement(1, 'Define a cybersecurity strategy and assign roles and responsibilities.'),
    requirement(2, 'Require multi-factor authentication and privileged access reviews.'),
    requirement(3, 'Maintain a system asset inventory and classification.'),
    requirement(4, 'Maintain firewall rules and network segmentation for remote access.'),
    requirement(5, 'Protect sensitive personal information using encryption.'),
    requirement(6, 'Maintain business continuity backups and test disaster recovery.'),
    requirement(7, 'Log events, monitor systems and detect suspicious activity.'),
    requirement(8, 'Assess supplier risk and review third-party vendor contracts.'),
    requirement(9, 'Conduct incident response exercises and prepare forensic procedures.'),
    requirement(10, 'Perform penetration testing and patch vulnerabilities.'),
    requirement(11, 'Train personnel in cybersecurity awareness.'),
    requirement(12, 'Ensure secure application development and change management.'),
]


class TestAdaptiveGenerationQueue(unittest.TestCase):
    def plan(self, rows=ROWS, objective='Assess organization security using the chosen framework and propose a complete GRC case'):
        return make_coverage_plan(
            organization='Test organization', framework='Example CSF v3',
            objective=objective, source_digest='a'*64,
            framework_id='authorized-framework-one', authorized_requirements=rows)

    def test_all_requirements_unassessed(self):
        p = self.plan()
        self.assertEqual(len(p['requirement_work_items']), len(ROWS))
        self.assertTrue(all(x['proposed_result'] == 'not_assessed' for x in p['requirement_work_items']))
        self.assertTrue(all(x['evidence_verified'] is False for x in p['requirement_work_items']))
        self.assertEqual(p['coverage']['requirement_results_verified'], 0)

    def test_plans_multiple_drafts_from_diverse_source(self):
        p = self.plan()
        self.assertGreater(p['generation_summary']['activity_targets']['7'], 1)
        self.assertGreater(p['generation_summary']['activity_targets']['4'], 1)
        self.assertNotEqual(p['generation_summary']['activity_targets']['4'],
                            p['generation_summary']['activity_targets']['14'])

    def test_each_focus_came_from_authorized_rows(self):
        p = self.plan()
        ids = {r['reference']: r['requirement_id'] for r in ROWS}
        for slot in p['generation_queue']:
            self.assertEqual(slot['focus_requirement_id'], ids[slot['focus_requirement_reference']])

    def test_reference_slot_uniqueness(self):
        p = self.plan()
        keys = [(s['activity_number'], s['draft_index']) for s in p['generation_queue']]
        self.assertEqual(len(keys), len(set(keys)))

    def test_compatibility_with_quality_one_limits(self):
        p = self.plan()
        self.assertTrue(all(1 <= s['activity_number'] <= 16 and
                            1 <= s['draft_index'] <= 10000 for s in p['generation_queue']))

    def test_inventories_complete_before_downstream_categories(self):
        p = self.plan()
        steps=[s['activity_number'] for s in p['generation_queue']]
        self.assertEqual(steps,sorted(steps))
        self.assertEqual(set(steps),set(range(1,17)))

    def test_first_wave_links_compatible(self):
        p = self.plan()
        first = {n:next(s for s in p['generation_queue'] if s['activity_number']==n) for n in (4,5,6)}
        self.assertEqual(first[4]['focus_requirement_id'], first[5]['focus_requirement_id'])
        self.assertEqual(first[5]['focus_requirement_id'], first[6]['focus_requirement_id'])

    def test_does_not_mark_assets_verified(self):
        p = self.plan()
        self.assertFalse(p['generation_summary']['organizational_assets_verified'])
        self.assertFalse(p['generation_summary']['risk_matrix_selected'])

    def test_does_not_write_business_records(self):
        p = self.plan()
        self.assertFalse(p['business_records_written'])
        self.assertFalse(p['generation_summary']['business_records_written'])

    def test_no_fixed_same_count_for_every_activity(self):
        p = self.plan()
        sizes = list(p['generation_summary']['activity_targets'].values())
        self.assertGreater(len(set(sizes)), 1)

    def test_deterministic_across_repeated_calls(self):
        self.assertEqual(self.plan()['generation_queue'], self.plan()['generation_queue'])

    def test_no_hardcoded_framework_identity(self):
        self.assertEqual(self.plan()['scope']['framework'], 'Example CSF v3')

    def test_invalid_source_rejected(self):
        with self.assertRaises(ValueError):
            self.plan(rows=[ROWS[0], ROWS[0]])

    def test_fallback_for_specialized_unclassified_requirements(self):
        row = requirement(35, 'Establish protection for specialized equipment.')
        p = self.plan(rows=[row])
        self.assertGreater(len(p['generation_queue']), 0)
        self.assertEqual(p['generation_queue'][0]['focus_requirement_reference'], 'R-35')

    def test_does_not_exceed_transport_limit_and_reports_overflow(self):
        r = [requirement(i, text) for i, text in enumerate([
            'Define cyber governance strategy', 'Review multi-factor authentication',
            'Protect classified information', 'Protect firewall network',
            'Test disaster recovery backups', 'Manage patch vulnerabilities',
            'Review cloud configuration', 'Secure application development',
            'Inspect physical facility', 'Monitor alerts logs',
            'Manage supplier contracts', 'Educate staff through awareness training',
            'Implement cryptography encryption', 'Maintain asset inventory',
            'Review incident response',
        ], 1)]
        q = plan_generation_queue(authorized_requirements=r, objective='Generate a comprehensive security assessment', max_slots_per_activity=12)
        self.assertTrue(all(s['draft_index'] <= 12 for s in q['generation_queue']))
        self.assertGreater(sum(q['generation_summary']['source_topic_overflow_not_queued'].values()), 0)

    def test_rejects_unsupported_max(self):
        with self.assertRaises(ValueError):
            plan_generation_queue(authorized_requirements=ROWS, objective='GRC assessment', max_slots_per_activity=10001)

    def test_unassessed_queue_is_not_counted_as_qwen(self):
        p = self.plan()
        self.assertNotEqual(p['coverage']['requirements_considered_for_review'],
                            p['generation_summary']['planned_qwen_detail_drafts'])
        self.assertFalse(p['coverage']['full_framework_assessed'])


if __name__ == '__main__':
    unittest.main()
