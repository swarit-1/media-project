import pytest
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.squad import SquadTemplate, SquadInstance, SquadMember, SquadInstanceStatus, SquadMemberStatus
from tests.conftest import FREELANCER_ID, EDITOR_ID, NEWSROOM_ID


@pytest.fixture
async def sample_template(db_session: AsyncSession) -> SquadTemplate:
    """Create a sample squad template."""
    template = SquadTemplate(
        id=uuid4(),
        newsroom_id=NEWSROOM_ID,
        created_by=EDITOR_ID,
        name="Investigative Team",
        description="Standard investigative reporting team",
        required_beats=["investigations", "tech", "legal"],
        required_roles=["lead_reporter", "researcher", "data_analyst"],
        min_members=2,
        max_members=5,
        min_trust_score=0.7,
        preferred_tiers=["tier1", "tier2"],
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    return template


@pytest.fixture
async def sample_instance(
    db_session: AsyncSession, sample_template: SquadTemplate
) -> SquadInstance:
    """Create a sample squad instance."""
    instance = SquadInstance(
        id=uuid4(),
        template_id=sample_template.id,
        newsroom_id=NEWSROOM_ID,
        created_by=EDITOR_ID,
        name="Tech Investigation Q1",
        description="Q1 tech investigation squad",
        project_brief="Investigating big tech data practices",
        status=SquadInstanceStatus.FORMING,
    )
    db_session.add(instance)
    await db_session.commit()
    await db_session.refresh(instance)
    return instance


# --- Template Tests ---

@pytest.mark.asyncio
async def test_create_template(editor_client: AsyncClient):
    """Test creating a squad template."""
    response = await editor_client.post(
        "/api/v1/squads/templates",
        json={
            "name": "Breaking News Team",
            "description": "Quick response breaking news team",
            "required_beats": ["breaking_news", "politics"],
            "required_roles": ["anchor", "field_reporter"],
            "min_members": 2,
            "max_members": 4,
            "min_trust_score": 0.8,
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Breaking News Team"
    assert data["newsroom_id"] == str(NEWSROOM_ID)
    assert data["created_by"] == str(EDITOR_ID)
    assert data["required_beats"] == ["breaking_news", "politics"]
    assert data["min_members"] == 2


@pytest.mark.asyncio
async def test_list_templates(
    editor_client: AsyncClient, sample_template: SquadTemplate
):
    """Test listing squad templates."""
    response = await editor_client.get("/api/v1/squads/templates")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "pagination" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_get_template(
    editor_client: AsyncClient, sample_template: SquadTemplate
):
    """Test getting a specific template."""
    response = await editor_client.get(
        f"/api/v1/squads/templates/{sample_template.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_template.id)
    assert data["name"] == "Investigative Team"


@pytest.mark.asyncio
async def test_update_template(
    editor_client: AsyncClient, sample_template: SquadTemplate
):
    """Test updating a squad template."""
    response = await editor_client.patch(
        f"/api/v1/squads/templates/{sample_template.id}",
        json={"name": "Updated Team Name", "max_members": 8},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Team Name"
    assert data["max_members"] == 8


@pytest.mark.asyncio
async def test_delete_template(
    editor_client: AsyncClient, sample_template: SquadTemplate
):
    """Test deleting a squad template."""
    response = await editor_client.delete(
        f"/api/v1/squads/templates/{sample_template.id}"
    )
    assert response.status_code == 204


# --- Instance Tests ---

@pytest.mark.asyncio
async def test_create_instance(
    editor_client: AsyncClient, sample_template: SquadTemplate
):
    """Test creating a squad instance."""
    response = await editor_client.post(
        "/api/v1/squads/instances",
        json={
            "template_id": str(sample_template.id),
            "name": "Election Coverage Squad",
            "description": "Squad for 2026 election coverage",
            "project_brief": "Cover the midterm elections",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Election Coverage Squad"
    assert data["status"] == "forming"
    assert data["template_id"] == str(sample_template.id)


@pytest.mark.asyncio
async def test_list_instances(
    editor_client: AsyncClient, sample_instance: SquadInstance
):
    """Test listing squad instances."""
    response = await editor_client.get("/api/v1/squads/instances")

    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert len(data["results"]) >= 1


@pytest.mark.asyncio
async def test_get_instance(
    editor_client: AsyncClient, sample_instance: SquadInstance
):
    """Test getting a squad instance."""
    response = await editor_client.get(
        f"/api/v1/squads/instances/{sample_instance.id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == str(sample_instance.id)
    assert data["status"] == "forming"


# --- Member Tests ---

@pytest.mark.asyncio
async def test_invite_member(
    editor_client: AsyncClient, sample_instance: SquadInstance
):
    """Test inviting a freelancer to a squad."""
    response = await editor_client.post(
        f"/api/v1/squads/instances/{sample_instance.id}/members",
        json={
            "freelancer_id": str(FREELANCER_ID),
            "role": "lead_reporter",
            "beats": ["investigations", "tech"],
            "invitation_message": "We'd love you to lead this investigation!",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert data["freelancer_id"] == str(FREELANCER_ID)
    assert data["role"] == "lead_reporter"
    assert data["status"] == "invited"


@pytest.mark.asyncio
async def test_list_my_invitations(
    freelancer_client: AsyncClient,
    db_session: AsyncSession,
    sample_instance: SquadInstance,
):
    """Test listing invitations for a freelancer."""
    # Create an invitation
    member = SquadMember(
        id=uuid4(),
        squad_id=sample_instance.id,
        freelancer_id=FREELANCER_ID,
        role="researcher",
        invited_by=EDITOR_ID,
        status=SquadMemberStatus.INVITED,
    )
    db_session.add(member)
    await db_session.commit()

    response = await freelancer_client.get("/api/v1/squads/invitations/my")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["freelancer_id"] == str(FREELANCER_ID)


@pytest.mark.asyncio
async def test_accept_invitation(
    freelancer_client: AsyncClient,
    db_session: AsyncSession,
    sample_instance: SquadInstance,
):
    """Test accepting a squad invitation."""
    member = SquadMember(
        id=uuid4(),
        squad_id=sample_instance.id,
        freelancer_id=FREELANCER_ID,
        role="data_analyst",
        invited_by=EDITOR_ID,
        status=SquadMemberStatus.INVITED,
    )
    db_session.add(member)
    await db_session.commit()

    response = await freelancer_client.post(
        f"/api/v1/squads/members/{member.id}/respond",
        json={"action": "accept"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["responded_at"] is not None


@pytest.mark.asyncio
async def test_decline_invitation(
    freelancer_client: AsyncClient,
    db_session: AsyncSession,
    sample_instance: SquadInstance,
):
    """Test declining a squad invitation."""
    member = SquadMember(
        id=uuid4(),
        squad_id=sample_instance.id,
        freelancer_id=FREELANCER_ID,
        role="researcher",
        invited_by=EDITOR_ID,
        status=SquadMemberStatus.INVITED,
    )
    db_session.add(member)
    await db_session.commit()

    response = await freelancer_client.post(
        f"/api/v1/squads/members/{member.id}/respond",
        json={"action": "decline"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "declined"


@pytest.mark.asyncio
async def test_disband_squad(
    editor_client: AsyncClient, sample_instance: SquadInstance
):
    """Test disbanding a squad."""
    response = await editor_client.post(
        f"/api/v1/squads/instances/{sample_instance.id}/disband"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "disbanded"


@pytest.mark.asyncio
async def test_activate_squad_insufficient_members(
    editor_client: AsyncClient, sample_instance: SquadInstance
):
    """Test that activating a squad without enough members fails."""
    response = await editor_client.post(
        f"/api/v1/squads/instances/{sample_instance.id}/activate"
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"]["code"] == "INVALID_STATE"
