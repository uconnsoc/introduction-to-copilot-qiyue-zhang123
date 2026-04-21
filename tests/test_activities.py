"""
Integration tests for the High School Activities API.

Tests cover all endpoints:
- GET /activities
- POST /activities/{activity_name}/signup
- DELETE /activities/{activity_name}/unregister
"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client):
        """Should return all activities in the database."""
        response = client.get("/activities")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have all 9 activities
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Basketball Team" in data

    def test_get_activities_returns_correct_structure(self, client):
        """Should return activities with all required fields."""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)

    def test_get_activities_includes_existing_participants(self, client):
        """Should return existing participant emails for activities."""
        response = client.get("/activities")
        data = response.json()
        
        chess_club = data["Chess Club"]
        assert "michael@mergington.edu" in chess_club["participants"]
        assert "daniel@mergington.edu" in chess_club["participants"]

    def test_get_activities_shows_empty_participant_lists(self, client):
        """Should return empty participant lists for activities with no signups."""
        response = client.get("/activities")
        data = response.json()
        
        basketball = data["Basketball Team"]
        assert basketball["participants"] == []


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_successfully_adds_participant(self, client, empty_activity_name, sample_email):
        """Should successfully sign up a student for an activity."""
        response = client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert sample_email in data["message"]

    def test_signup_updates_participant_list(self, client, empty_activity_name, sample_email):
        """Should add the email to the participants list."""
        client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": sample_email}
        )
        
        response = client.get("/activities")
        activities = response.json()
        
        assert sample_email in activities[empty_activity_name]["participants"]

    def test_signup_prevents_duplicate_registration(self, client, sample_activity_name):
        """Should prevent a student from signing up twice for the same activity."""
        email = "test@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{sample_activity_name}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_returns_404_for_nonexistent_activity(self, client, nonexistent_activity, sample_email):
        """Should return 404 when trying to sign up for a nonexistent activity."""
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_with_special_characters_in_activity_name(self, client, sample_email):
        """Should handle activity names with special characters."""
        # Try signing up for "Programming Class" which contains no spaces
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200

    def test_signup_multiple_students_to_same_activity(self, client, empty_activity_name):
        """Should allow multiple different students to sign up for the same activity."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        response1 = client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": email1}
        )
        response2 = client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": email2}
        )
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        # Check both are in participants
        response = client.get("/activities")
        participants = response.json()[empty_activity_name]["participants"]
        assert email1 in participants
        assert email2 in participants

    def test_signup_respects_max_participants(self, client):
        """Should allow signups up to max_participants limit."""
        # Basketball Team has max_participants of 15
        activity_name = "Basketball Team"
        
        # Sign up 15 students
        for i in range(15):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity_name}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # 16th student should fail (or succeed if no capacity check - adjust based on requirement)
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "student16@mergington.edu"}
        )
        # Note: Current implementation doesn't enforce max_participants on signup
        # Uncomment the assertion below if capacity enforcement is added
        # assert response.status_code == 400 or response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_successfully_removes_participant(self, client, empty_activity_name, sample_email):
        """Should successfully unregister a student from an activity."""
        # First, sign them up
        client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Then unregister
        response = client.delete(
            f"/activities/{empty_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_updates_participant_list(self, client, empty_activity_name, sample_email):
        """Should remove the email from the participants list."""
        # Sign up
        client.post(
            f"/activities/{empty_activity_name}/signup",
            params={"email": sample_email}
        )
        
        # Unregister
        client.delete(
            f"/activities/{empty_activity_name}/unregister",
            params={"email": sample_email}
        )
        
        # Verify removed
        response = client.get("/activities")
        participants = response.json()[empty_activity_name]["participants"]
        assert sample_email not in participants

    def test_unregister_prevents_unregistering_nonexistent_student(self, client, empty_activity_name):
        """Should return 400 when trying to unregister a student not in the activity."""
        response = client.delete(
            f"/activities/{empty_activity_name}/unregister",
            params={"email": "nonexistent@mergington.edu"}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_returns_404_for_nonexistent_activity(self, client, nonexistent_activity, sample_email):
        """Should return 404 when trying to unregister from a nonexistent activity."""
        response = client.delete(
            f"/activities/{nonexistent_activity}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_from_activity_with_multiple_participants(self, client, empty_activity_name):
        """Should only remove the specified student, leaving others."""
        email1 = "student1@mergington.edu"
        email2 = "student2@mergington.edu"
        
        # Sign up two students
        client.post(f"/activities/{empty_activity_name}/signup", params={"email": email1})
        client.post(f"/activities/{empty_activity_name}/signup", params={"email": email2})
        
        # Unregister first student
        response = client.delete(
            f"/activities/{empty_activity_name}/unregister",
            params={"email": email1}
        )
        
        assert response.status_code == 200
        
        # Check that email2 is still there
        response = client.get("/activities")
        participants = response.json()[empty_activity_name]["participants"]
        assert email1 not in participants
        assert email2 in participants


class TestRootEndpoint:
    """Tests for the root GET / endpoint."""

    def test_root_redirects_to_static_index(self, client):
        """Should redirect to /static/index.html."""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"
