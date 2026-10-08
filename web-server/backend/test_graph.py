"""Run with: python -m unittest discover -s web-server/backend -p test_graph.py."""
import unittest
from attack_flow import AttackFlowEngine
from schemas import AttackFlowGraph


def sentence(index, techniques=(), assets=()):
    return {"sentence_id": index, "text": f"Evidence {index}",
            "techniques": [{"id": t, "name": t, "confidence": .8, "prediction_source": "classifier"} for t in techniques],
            "assets": [{"id": a, "name": a, "confidence": .95, "prediction_source": "keyword"} for a in assets]}


class GraphEvidenceTests(unittest.TestCase):
    def build(self, rows):
        return AttackFlowGraph(**AttackFlowEngine().build_attack_flow_from_chrono_data(rows, {}, {}))

    def test_repeated_entities_preserve_evidence_through_response_schema(self):
        graph = self.build([sentence(0, ['T1'], ['A1']), sentence(1, ['T1'], ['A1'])])
        self.assertEqual(len(graph.nodes), 2)
        for node in graph.nodes:
            self.assertEqual(node.occurrence_count, 2)
            self.assertEqual([e.sentence_id for e in node.evidence], [0, 1])
        self.assertEqual(graph.nodes[1].prediction_sources, ['keyword'])
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.edges[0].relation, 'CO_MENTIONED')
        self.assertEqual(len(graph.edges[0].evidence), 2)

    def test_asset_only_sentence_does_not_invent_targeting(self):
        graph = self.build([sentence(0, ['T1']), sentence(1, assets=['A1']), sentence(2, ['T2'])])
        self.assertEqual(len(graph.edges), 1)
        edge = graph.edges[0]
        self.assertEqual((edge.source, edge.target, edge.relation), ('tech_T1', 'tech_T2', 'REPORT_ORDER'))
        self.assertEqual([e.sentence_id for e in edge.evidence], [0, 2])
        self.assertIn('not verified', edge.basis)

    def test_cycles_and_disconnected_assets_have_stable_nonoverlapping_layout(self):
        rows = [sentence(0, ['T1'], ['A1', 'A2']), sentence(1, ['T2']), sentence(2, ['T1']), sentence(3, assets=['A3'])]
        graph = self.build(rows)
        self.assertFalse(graph.metrics.is_dag)
        self.assertEqual(graph.model_dump(), self.build(rows).model_dump())
        for i, a in enumerate(graph.nodes):
            for b in graph.nodes[i + 1:]:
                overlap = a.x < b.x + b.width and a.x + a.width > b.x and a.y < b.y + b.height and a.y + a.height > b.y
                self.assertFalse(overlap, (a.id, b.id))

    def test_same_sentence_techniques_are_not_assumed_sequential(self):
        graph = self.build([sentence(0, ['T1', 'T2'], ['A1'])])
        self.assertTrue(all(edge.relation == 'CO_MENTIONED' for edge in graph.edges))

    def test_empty_report(self):
        graph = self.build([])
        self.assertEqual(graph.nodes, [])
        self.assertEqual(graph.edges, [])
        self.assertEqual(graph.metrics.longest_attack_chain, 0)


if __name__ == '__main__':
    unittest.main()
