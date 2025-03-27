"""
Tests for Android integration with Memory Debugger.
These tests verify that the Android integration works as expected.
"""
import os
import platform
import unittest
from unittest.mock import patch, MagicMock

# Try to import Android support
try:
    from android_process_connector import AndroidProcessConnector, is_running_on_android
    from process_bridge import ProcessType
    HAS_ANDROID_SUPPORT = True
except ImportError:
    HAS_ANDROID_SUPPORT = False

@unittest.skipIf(not HAS_ANDROID_SUPPORT, "Android support not available")
class TestAndroidIntegration(unittest.TestCase):
    """Test Android integration with Memory Debugger"""
    
    def setUp(self):
        """Set up test environment"""
        self.android_connector = AndroidProcessConnector()
    
    @patch('subprocess.run')
    def test_is_android_connected(self, mock_run):
        """Test detecting connected Android devices"""
        # Mock subprocess.run to return a successful result
        mock_process = MagicMock()
        mock_process.stdout = "List of devices attached\ndevice123\tdevice\n"
        mock_run.return_value = mock_process
        
        # Test the connection detection
        result = self.android_connector.is_android_connected()
        self.assertTrue(result)
        self.assertEqual(self.android_connector.device_id, "device123")
    
    @patch('android_process_connector.AndroidProcessConnector.is_android_connected')
    @patch('subprocess.run')
    def test_list_processes(self, mock_run, mock_is_connected):
        """Test listing processes on Android device"""
        # Mock connection and subprocess.run
        mock_is_connected.return_value = True
        self.android_connector.device_id = "device123"
        
        # Mock process list output
        sample_output = """USER     PID   PPID  VSIZE  RSS     WCHAN    PC        NAME
root      1     0     10376  1452   SyS_epoll_ 0000000000 init
system    123   1     986444 61808  SyS_epoll_ 0000000000 system_server
u0_a123   456   123   812344 41234  SyS_epoll_ 0000000000 com.android.chrome"""
        
        mock_process = MagicMock()
        mock_process.stdout = sample_output
        mock_run.return_value = mock_process
        
        # Test process listing
        processes = self.android_connector.list_processes()
        
        # Verify results
        self.assertEqual(len(processes), 3)
        self.assertEqual(processes[0]["pid"], "1")
        self.assertEqual(processes[0]["name"], "init")
        self.assertEqual(processes[1]["pid"], "123")
        self.assertEqual(processes[1]["name"], "system_server")
        self.assertEqual(processes[2]["pid"], "456")
        self.assertEqual(processes[2]["name"], "com.android.chrome")
    
    @patch('android_process_connector.AndroidProcessConnector.is_android_connected')
    @patch('subprocess.run')
    def test_is_device_rooted(self, mock_run, mock_is_connected):
        """Test detecting if Android device is rooted"""
        # Mock connection and subprocess.run
        mock_is_connected.return_value = True
        self.android_connector.device_id = "device123"
        
        # Test with rooted device
        mock_process = MagicMock()
        mock_process.stdout = "uid=0(root) gid=0(root) groups=0(root)"
        mock_run.return_value = mock_process
        
        self.assertTrue(self.android_connector.is_device_rooted())
        
        # Test with non-rooted device
        mock_process.stdout = "uid=10123(u0_a123) gid=10123(u0_a123) groups=10123(u0_a123)"
        self.assertFalse(self.android_connector.is_device_rooted())
    
    def test_is_running_on_android(self):
        """Test platform detection for Android"""
        # This should be False on test machines
        self.assertFalse(is_running_on_android())

if __name__ == '__main__':
    unittest.main()