import unittest
from agent_runtime.models import ModelProfile, ModelRouter
from agent_runtime.permissions import PermissionEngine
from agent_runtime.sessions import InMemoryCheckpointRepository
from agent_runtime.tools import ToolRegistry

class ArchitectureTest(unittest.TestCase):
    def test_core_modules_construct(self) -> None:
        self.assertIsNotNone(ToolRegistry())
        self.assertEqual(PermissionEngine().decide("read", "low"), "ALLOW")
        self.assertIsNotNone(InMemoryCheckpointRepository())
        router = ModelRouter([ModelProfile("local", True, True, "local", 1000, 0, True)])
        self.assertEqual(router.select(tools=True, json_mode=True, private_data=True, input_tokens=10).id, "local")

if __name__ == "__main__": unittest.main()
