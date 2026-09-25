"""
RevenueAI 360 - API Integration Test Suite
Validates the FastAPI REST endpoints using TestClient.
"""

import os
os.environ["LLM_PROVIDER"] = "deterministic_demo"

import pytest
from fastapi.testclient import TestClient
from apps.api.main import app
from domain.database import init_db
from services.demo_seeder import seed_demo_data
import asyncio


client = TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def init_api_test():
    init_db()
    asyncio.run(seed_demo_data())


def test_get_dashboard_metrics():
    res = client.get("/api/v1/dashboard/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "new_leads" in data
    assert "active_opportunities" in data
    assert "open_complaints" in data


def test_list_customers_and_customer360():
    res = client.get("/api/v1/customers")
    assert res.status_code == 200
    customers = res.json()
    assert len(customers) > 0
    nexa = next((c for c in customers if "Nexa" in c["name"]), None)
    assert nexa is not None

    # Get Customer 360
    res360 = client.get(f"/api/v1/customers/{nexa['id']}/360")
    assert res360.status_code == 200
    c360_data = res360.json()
    assert "account" in c360_data
    assert "contacts" in c360_data
    assert "recent_interactions" in c360_data
    assert "next_best_action" in c360_data


def test_inbound_event_and_workflow_trace():
    payload = {
        "channel": "email",
        "external_identity": "marcus.vance@nexalogistics.com",
        "subject": "Automated Copilot Demo Request",
        "content": "Exploring AI automation for freight broker tracking operations.",
    }
    res = client.post("/api/v1/events/inbound", json=payload)
    assert res.status_code == 200
    resp_data = res.json()
    assert resp_data["status"] == "ACCEPTED"
    wf_id = resp_data["workflow_id"]

    # Check Workflow Trace
    trace_res = client.get(f"/api/v1/workflows/{wf_id}/trace")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["workflow_id"] == wf_id
    assert len(trace_data["agent_runs"]) > 0


def test_approval_lifecycle():
    # Fetch pending actions
    res = client.get("/api/v1/actions/pending")
    assert res.status_code == 200
    actions = res.json()
    assert len(actions) > 0
    first_action = actions[0]

    # Approve action
    appr_payload = {
        "decision": "APPROVED",
        "reviewer": "Director of Sales",
        "comments": "Approved for dispatch.",
    }
    appr_res = client.post(f"/api/v1/actions/{first_action['id']}/approve", json=appr_payload)
    assert appr_res.status_code == 200
    assert appr_res.json()["status"] == "APPROVED_AND_EXECUTED"


def test_create_customer_ai_demo_endpoint():
    res = client.get("/api/v1/customers")
    nexa = next((c for c in res.json() if "Nexa" in c["name"]), None)

    demo_req = {
        "customer_problem": "Manual tracking updates causing dispatcher fatigue",
        "discovery_notes": "Needs WhatsApp alerts and ERP webhook integration",
    }
    demo_res = client.post(f"/api/v1/customers/{nexa['id']}/create-ai-demo", json=demo_req)
    assert demo_res.status_code == 200
    demo_data = demo_res.json()
    assert "recommended_ai_pattern" in demo_data
    assert len(demo_data["proposed_agents"]) == 3
    assert "prototype_to_production_roadmap" in demo_data
