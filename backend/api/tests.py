from django.test import TestCase

# Create your tests here.


from rest_framework.test import APITestCase
from unittest.mock import patch


   


class ChatAPITests(APITestCase):
    url = "/api/chat/"

    def test_question_is_required(self):
        response = self.client.post(
            self.url,
            {"question": ""},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_filters_must_be_json_object(self):
        response = self.client.post(
            self.url,
            {
                "question": "What does createRoot do?",
                "filters": ["react"],
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data["error"],
            "Filters must be a JSON object.",
        )

    def test_unsupported_filter_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "question": "What does createRoot do?",
                "filters": {"unknown_field": "value"},
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid_filters", response.data)



    @patch("api.views.search_chunks_by_function", return_value=[])
    @patch("api.views.search_similar_chunks", return_value=[])
    @patch("api.views.create_query_embedding", return_value=[0.1] * 384)


    

    def test_valid_metadata_filters_are_passed_to_retrieval(
        self,
        mock_embedding,
        mock_semantic_search,
        mock_function_search,
    ):
        filters = {
            "framework": "react",
            "documentation_source": "react.dev",
        }

        response = self.client.post(
            self.url,
            {
                "question": "What does createRoot do in React?",
                "filters": filters,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        mock_semantic_search.assert_called_once_with(
            mock_embedding.return_value,
            metadata_filters=filters,
        )

        for call in mock_function_search.call_args_list:
            self.assertEqual(
                call.kwargs["metadata_filters"],
                filters,
            )

