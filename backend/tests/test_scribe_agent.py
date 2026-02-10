import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

# Mock modules before importing app modules
sys.modules['google.generativeai'] = MagicMock()
sys.modules['app.services.audit_service'] = MagicMock()

from app.agents.scribe_agent import ScribeAgent

class TestScribeAgent(unittest.IsolatedAsyncioTestCase):
    async def test_run_docx(self):
        # Mock settings
        with patch('app.agents.base_agent.settings') as mock_settings:
            mock_settings.GOOGLE_API_KEY = "fake_key"

            # Mock artifact_service
            with patch('app.agents.scribe_agent.artifact_service') as mock_artifact_service:
                mock_artifact_service.save_artifact.return_value = "path/to/artifact.docx"

                # Instantiate Agent
                config = {
                    "name": "SCRIBE",
                    "model": "fake-model",
                    "temperature": 0.1
                }

                # Mock audit service capture (called in __init__)
                with patch('app.services.audit_service.audit_service.capture_agent_state') as mock_capture:
                     mock_capture.return_value = "state_id"

                     agent = ScribeAgent(config, "task_123")

                     # Mock call_llm
                     agent.call_llm = AsyncMock(return_value="# Heading\n\n- Bullet point")

                     # Run
                     context = {
                         "scribe": {
                             "selected_documents": ["feature_doc"],
                             "output_format": "docx",
                             "requirement_text": "reqs",
                         }
                     }

                     result = await agent.run(context)

                     # Verify
                     self.assertEqual(result["status"], "success")
                     self.assertIn("feature_doc", result["artifacts"])

                     # Verify save_artifact called with bytes (docx)
                     args = mock_artifact_service.save_artifact.call_args
                     self.assertEqual(args[0][0], "task_123") # task_id
                     self.assertEqual(args[0][1], "feature_doc") # artifact_type
                     self.assertIsInstance(args[0][2], bytes) # content should be bytes
                     self.assertTrue(args[1]['filename'].endswith(".docx"))

if __name__ == '__main__':
    unittest.main()
