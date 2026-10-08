"""API integration checks using the local trained models (no training or downloads).
Run from the repository root: HF_HUB_OFFLINE=1 venv/bin/python web-server/backend/test_api.py
"""
from fastapi.testclient import TestClient
from app import app
from pipeline import pipeline_instance

client = TestClient(app)


def test_backend_api():
    assert client.get('/api/health').status_code == 200
    assert len(client.get('/api/assets/taxonomy').json()) == 18
    dashboard = client.get('/')
    assert dashboard.status_code == 200 and '<app-root>' in dashboard.text
    assert client.post('/api/analyze', json={'text': ' '}).status_code == 400
    response = client.post('/api/analyze', json={
        'text': 'The attacker used PowerShell on the workstation. Then the attacker used RDP to access the server.',
        'report_name': 'integration-test'
    })
    assert response.status_code == 200, response.text
    graph = response.json()['attack_flow']
    assert graph['nodes'] and graph['edges']
    assert all(node['evidence'] and node['occurrence_count'] >= 1 for node in graph['nodes'])
    assert all(edge['evidence'] and edge['basis'] for edge in graph['edges'])
    assert all(edge['relation'] in ('REPORT_ORDER', 'CO_MENTIONED') for edge in graph['edges'])
    assert all(score >= .99 for _, score, _ in pipeline_instance.predict_techniques('PowerShell', .99))
    assert all(score >= .99 for _, score, _ in pipeline_instance.predict_assets('workstation', .99))
    print('API checks passed: dashboard, taxonomy, validation, real-model analysis, evidence, and thresholds.')


if __name__ == '__main__':
    test_backend_api()
