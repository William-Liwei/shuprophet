import json
import math
import unittest

from agent.public import public_agent_result
from agent.reasoner import TSReasoner


class ToolAgentTests(unittest.TestCase):
    def test_agent_runs_analysis_forecast_and_validation(self):
        data = [20 + 0.12 * i + 1.8 * math.sin(i / 4) for i in range(72)]

        result = TSReasoner().predict(data, steps=6)

        self.assertEqual(len(result["predictions"]), 6)
        self.assertEqual(len(result["prediction_interval"]["lower"]), 6)
        self.assertGreaterEqual(result["confidence"], 0.1)
        self.assertLessEqual(result["confidence"], 0.95)

        actions = [step["action"] for step in result["trajectory"]["steps"]]
        self.assertIn("trend_analysis", actions)
        self.assertIn("forecast_model_selection", actions)
        self.assertIn("prediction_range_check", actions)
        self.assertIn("trend_consistency_check", actions)
        self.assertIn("confidence_scoring", actions)

        public_result = public_agent_result(result)
        serialized = json.dumps(public_result, ensure_ascii=False).lower()
        self.assertEqual(public_result["engine"], "鼠先知引擎")
        self.assertEqual(public_result["candidates_evaluated"], len(result["models_used"]))
        for internal_name in ("arima", "ets", "theta", "linear"):
            self.assertNotIn(internal_name, serialized)
        for sensitive_key in ("selected_model", "models_used", "cv_errors"):
            self.assertNotIn(sensitive_key, serialized)

    def test_agent_rejects_invalid_tasks(self):
        with self.assertRaisesRegex(ValueError, "预测步数"):
            TSReasoner().predict(list(range(20)), steps=0)
        with self.assertRaisesRegex(ValueError, "常数"):
            TSReasoner().predict([1] * 20, steps=5)


if __name__ == "__main__":
    unittest.main()
