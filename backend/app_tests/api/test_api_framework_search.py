import pytest
from rest_framework import status

from core.models import Framework
from iam.models import Folder


@pytest.mark.django_db
class TestFrameworkSearch:
    """Framework search only matches terms at the start of a word"""

    def test_search_does_not_match_inside_words(self, authenticated_client):
        root = Folder.get_root_folder()
        Framework.objects.create(
            name="NIST SP 800-53",
            description="Security controls",
            provider="NIST",
            folder=root,
        )
        Framework.objects.create(
            name="NIST-CSF 2.0",
            description="Cybersecurity framework",
            folder=root,
        )
        Framework.objects.create(
            name="PSSI-MCAS",
            description="Politique pour les ministères chargés des affaires sociales",
            folder=root,
        )
        Framework.objects.create(
            name="Recommandations relatives à l'administration sécurisée",
            description="Guide",
            folder=root,
        )

        response = authenticated_client.get("/api/frameworks/", {"search": "nist"})

        assert response.status_code == status.HTTP_200_OK
        names = sorted(item["name"] for item in response.json()["results"])
        assert names == ["NIST SP 800-53", "NIST-CSF 2.0"]

    def test_search_matches_provider_and_multiple_terms(self, authenticated_client):
        root = Folder.get_root_folder()
        Framework.objects.create(
            name="Essential Eight",
            description="Mitigation strategies",
            provider="ACSC",
            folder=root,
        )
        Framework.objects.create(
            name="Other",
            description="Mitigation strategies",
            provider="Other",
            folder=root,
        )

        response = authenticated_client.get(
            "/api/frameworks/", {"search": "acsc mitigation"}
        )

        assert response.status_code == status.HTTP_200_OK
        names = [item["name"] for item in response.json()["results"]]
        assert names == ["Essential Eight"]
