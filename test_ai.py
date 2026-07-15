import os
import sys
import unittest
import numpy as np

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class TestAISystem(unittest.TestCase):
    def setUp(self):
        # Disable logging / redirect stdout for cleaner outputs if needed
        pass

    def test_imports(self):
        """
        Verify that all core application components can be imported successfully.
        """
        try:
            from backend.ai.model import FaceCNN
            from backend.ai.detector import FaceDetector
            from backend.ai.dataset import FaceDatasetLoader
            from backend.db_models import User, Student, Attendance
            from backend.reports_generator import generate_csv
            from backend.backup_manager import list_db_backups
            
            print("[-] All modules imported successfully.")
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Module import failed: {e}")

    def test_model_forward_pass(self):
        """
        Verify the FaceCNN PyTorch model architecture compiles and handles a forward pass.
        """
        try:
            import torch
            from backend.ai.model import FaceCNN
            
            num_classes = 5
            model = FaceCNN(num_classes=num_classes)
            model.eval()
            
            # Create a mock batch of 2 images: 100x100 RGB
            dummy_input = torch.randn(2, 3, 100, 100)
            
            with torch.no_grad():
                output = model(dummy_input)
                probs = model.predict_probability(dummy_input)
                
            self.assertEqual(output.shape, (2, num_classes))
            self.assertEqual(probs.shape, (2, num_classes))
            
            # Check probabilities sum to 1
            for i in range(2):
                self.assertAlmostEqual(probs[i].sum().item(), 1.0, places=4)
                
            print("[-] FaceCNN model architecture and forward pass verified.")
        except ImportError:
            print("[SKIP] PyTorch not installed yet, skipping forward pass test.")
        except Exception as e:
            self.fail(f"Model forward pass test failed: {e}")

    def test_detector_setup(self):
        """
        Verify the OpenCV Haar Cascade face detector loads properly.
        """
        try:
            from backend.ai.detector import FaceDetector
            detector = FaceDetector()
            self.assertIsNotNone(detector.face_cascade)
            print("[-] Face detector (OpenCV Haar Cascade) loaded successfully.")
        except Exception as e:
            self.fail(f"Face detector setup failed: {e}")

if __name__ == '__main__':
    unittest.main()
