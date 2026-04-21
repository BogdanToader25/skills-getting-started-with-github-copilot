"""
FastAPI tests for activities management endpoints.
Tests use AAA (Arrange-Act-Assert) pattern and cover success cases, 
error handling, and edge cases.
"""

import pytest
from src.app import activities


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client_with_reset):
        # Arrange
        expected_activity_count = 9

        # Act
        response = client_with_reset.get("/activities")

        # Assert
        assert response.status_code == 200
        activities_data = response.json()
        assert len(activities_data) == expected_activity_count
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data

    def test_get_activities_returns_correct_structure(self, client_with_reset):
        # Arrange
        # Activity

        # Act
        response = client_with_reset.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        chess_club = activities_data["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_includes_existing_participants(self, client_with_reset):
        # Arrange
        expected_chess_participants = ["michael@mergington.edu", "daniel@mergington.edu"]

        # Act
        response = client_with_reset.get("/activities")
        activities_data = response.json()

        # Assert
        assert response.status_code == 200
        assert activities_data["Chess Club"]["participants"] == expected_chess_participants


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful_with_valid_activity_and_email(self, client_with_reset):
        # Arrange
        activity_name = "Chess Club"
        email = "new_student@mergington.edu"

        # Act
        response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in activities["Chess Club"]["participants"]

    def test_signup_duplicate_email_returns_400(self, client_with_reset):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already signed up

        # Act
        response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_invalid_activity_returns_404(self, client_with_reset):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"

        # Act
        response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_updates_participant_count(self, client_with_reset):
        # Arrange
        activity_name = "Tennis Club"
        email = "new_player@mergington.edu"
        initial_count = len(activities["Tennis Club"]["participants"])

        # Act
        response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(activities["Tennis Club"]["participants"]) == initial_count + 1

    def test_signup_multiple_different_emails_succeeds(self, client_with_reset):
        # Arrange
        activity_name = "Art Studio"
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"

        # Act
        response1 = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email1}
        )
        response2 = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 in activities["Art Studio"]["participants"]
        assert email2 in activities["Art Studio"]["participants"]


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful_removes_participant(self, client_with_reset):
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        assert email in activities[activity_name]["participants"]

        # Act
        response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        assert email not in activities[activity_name]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, client_with_reset):
        # Arrange
        activity_name = "Chess Club"
        email = "not_signed_up@mergington.edu"

        # Act
        response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_invalid_activity_returns_404(self, client_with_reset):
        # Arrange
        activity_name = "Nonexistent Activity"
        email = "michael@mergington.edu"

        # Act
        response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_updates_participant_count(self, client_with_reset):
        # Arrange
        activity_name = "Programming Class"
        email = "emma@mergington.edu"
        initial_count = len(activities[activity_name]["participants"])

        # Act
        response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert len(activities[activity_name]["participants"]) == initial_count - 1

    def test_unregister_then_signup_again_succeeds(self, client_with_reset):
        # Arrange
        activity_name = "Art Studio"
        email = "isabella@mergington.edu"

        # Act - Unregister
        unregister_response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Act - Signup again
        signup_response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert
        assert unregister_response.status_code == 200
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

    def test_unregister_multiple_participants_independently(self, client_with_reset):
        # Arrange
        activity_name = "Debate Team"
        email1 = "noah@mergington.edu"
        email2 = "ava@mergington.edu"

        # Act
        response1 = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email1}
        )
        response2 = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email2}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email1 not in activities[activity_name]["participants"]
        assert email2 not in activities[activity_name]["participants"]


class TestIntegrationScenarios:
    """Integration tests combining multiple endpoints"""

    def test_full_lifecycle_signup_and_unregister(self, client_with_reset):
        # Arrange
        activity_name = "Science Club"
        email = "test_student@mergington.edu"

        # Act - Signup
        signup_response = client_with_reset.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )

        # Assert signup
        assert signup_response.status_code == 200
        assert email in activities[activity_name]["participants"]

        # Act - Unregister
        unregister_response = client_with_reset.delete(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )

        # Assert unregister
        assert unregister_response.status_code == 200
        assert email not in activities[activity_name]["participants"]

    def test_multiple_activities_enrollment(self, client_with_reset):
        # Arrange
        email = "multi_activity_student@mergington.edu"
        activities_to_enroll = ["Chess Club", "Programming Class", "Tennis Club"]

        # Act - Enroll in multiple activities
        responses = []
        for activity_name in activities_to_enroll:
            response = client_with_reset.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            responses.append(response)

        # Assert
        for response in responses:
            assert response.status_code == 200
        for activity_name in activities_to_enroll:
            assert email in activities[activity_name]["participants"]
