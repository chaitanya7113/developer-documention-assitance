from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APITestCase

from api.views import merge_results


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

    def test_whitespace_question_is_rejected(self):
        response = self.client.post(
            self.url,
            {"question": "   "},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data["error"], "Question is required.")

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

    @patch("api.views.search_combined_chunks", return_value=[])
    @patch("api.views.create_query_embedding", return_value=[0.1] * 384)
    def test_valid_metadata_filters_are_passed_to_combined_retrieval(
        self,
        mock_embedding,
        mock_combined_search,
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
        mock_combined_search.assert_called_once_with(
            query_vector=mock_embedding.return_value,
            function_names=["createRoot"],
            include_code=False,
            limit=20,
            metadata_filters=filters,
        )

    @patch("api.views.generate_answer")
    @patch("api.views.rerank_results")
    @patch("api.views.search_combined_chunks")
    @patch("api.views.create_query_embedding", return_value=[0.1] * 384)
    def test_results_below_threshold_are_rejected(
        self,
        mock_embedding,
        mock_combined_search,
        mock_rerank,
        mock_generate,
    ):
        point = SimpleNamespace(
            payload={
                "chunk_id": "react-001",
                "file": "react.md",
                "content": "Documentation content",
            }
        )
        mock_combined_search.return_value = [point]
        mock_rerank.return_value = [
            {
                "score": 0.99,
                "payload": point.payload,
            }
        ]

        response = self.client.post(
            self.url,
            {"question": "What does createRoot do?"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["answer"],
            "I couldn't find the answer in the provided documentation.",
        )
        self.assertEqual(response.data["citations"], [])
        mock_generate.assert_not_called()

    @patch("api.views.generate_answer", return_value="React creates a root.")
    @patch("api.views.build_context", return_value="Relevant documentation")
    @patch("api.views.rerank_results")
    @patch("api.views.search_combined_chunks")
    @patch("api.views.create_query_embedding", return_value=[0.1] * 384)
    def test_results_at_threshold_are_accepted(
        self,
        mock_embedding,
        mock_combined_search,
        mock_rerank,
        mock_build_context,
        mock_generate,
    ):
        point = SimpleNamespace(
            payload={
                "chunk_id": "react-001",
                "file": "react.md",
                "content": "Documentation content",
            }
        )
        mock_combined_search.return_value = [point]
        mock_rerank.return_value = [
            {
                "score": 1.0,
                "payload": point.payload,
            }
        ]

        response = self.client.post(
            self.url,
            {"question": "What does createRoot do?"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["answer"], "React creates a root.")
        mock_build_context.assert_called_once()
        mock_generate.assert_called_once_with(
            "What does createRoot do?",
            "Relevant documentation",
        )


class MergeResultsTests(TestCase):
    def test_duplicate_chunks_are_removed(self):
        chunk_1 = SimpleNamespace(
            payload={
                "chunk_id": "react-001",
                "content": "React documentation",
            }
        )
        chunk_2 = SimpleNamespace(
            payload={
                "chunk_id": "react-001",
                "content": "Duplicate chunk",
            }
        )
        chunk_3 = SimpleNamespace(
            payload={
                "chunk_id": "react-002",
                "content": "Another chunk",
            }
        )

        results = merge_results(
            [chunk_1, chunk_2],
            [chunk_3],
        )

        self.assertEqual(len(results), 2)
        self.assertEqual(
            [item.payload["chunk_id"] for item in results],
            ["react-001", "react-002"],
        )

    def test_chunks_without_ids_use_file_and_content(self):
        chunk_1 = SimpleNamespace(
            payload={
                "file": "react.md",
                "content": "How to create a root",
            }
        )
        duplicate = SimpleNamespace(
            payload={
                "file": "react.md",
                "content": "How to create a root",
            }
        )

        results = merge_results([chunk_1, duplicate])

        self.assertEqual(len(results), 1)
