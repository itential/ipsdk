# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
from unittest.mock import patch

from ipsdk import logger, metadata


class TestLoggingConfiguration:
    """Test basic logging configuration and setup."""

    def test_fatal_logging_level_exists(self):
        """Test that FATAL logging level is properly configured."""
        assert hasattr(logging, 'FATAL')
        assert logging.FATAL == 90
        assert logging.getLevelName(90) == 'FATAL'

    def test_default_logger_level(self):
        """Test that the default logger level is set to 100."""
        ipsdk_logger = logging.getLogger(metadata.name)
        assert ipsdk_logger.level == 100


class TestLogFunction:
    """Test the core log function."""

    def test_log_function_with_debug_level(self):
        """Test log function with DEBUG level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.log(logging.DEBUG, "Debug message")
            mock_log.assert_called_once_with(logging.DEBUG, "Debug message")

    def test_log_function_with_info_level(self):
        """Test log function with INFO level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.log(logging.INFO, "Info message")
            mock_log.assert_called_once_with(logging.INFO, "Info message")

    def test_log_function_with_error_level(self):
        """Test log function with ERROR level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.log(logging.ERROR, "Error message")
            mock_log.assert_called_once_with(logging.ERROR, "Error message")

    def test_log_function_with_fatal_level(self):
        """Test log function with FATAL level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.log(logging.FATAL, "Fatal message")
            mock_log.assert_called_once_with(logging.FATAL, "Fatal message")


class TestPartialLogFunctions:
    """Test the partial log functions (debug, info, warning, etc.)."""

    def test_debug_function(self):
        """Test debug function calls log with DEBUG level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.debug("Debug message")
            mock_log.assert_called_once_with(logging.DEBUG, "Debug message")

    def test_info_function(self):
        """Test info function calls log with INFO level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.info("Info message")
            mock_log.assert_called_once_with(logging.INFO, "Info message")

    def test_warning_function(self):
        """Test warning function calls log with WARNING level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.warning("Warning message")
            mock_log.assert_called_once_with(logging.WARNING, "Warning message")

    def test_error_function(self):
        """Test error function calls log with ERROR level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.error("Error message")
            mock_log.assert_called_once_with(logging.ERROR, "Error message")

    def test_critical_function(self):
        """Test critical function calls log with CRITICAL level."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.critical("Critical message")
            mock_log.assert_called_once_with(logging.CRITICAL, "Critical message")


class TestExceptionFunction:
    """Test the exception logging function."""

    def test_exception_function_with_exception(self):
        """Test exception function logs exception as error."""
        test_exception = ValueError("Test exception message")
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.exception(test_exception)
            mock_log.assert_called_once_with(logging.ERROR, "Test exception message")

    def test_exception_function_with_runtime_error(self):
        """Test exception function with RuntimeError."""
        test_exception = RuntimeError("Runtime error occurred")
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.exception(test_exception)
            mock_log.assert_called_once_with(logging.ERROR, "Runtime error occurred")

    def test_exception_function_with_custom_exception(self):
        """Test exception function with custom exception."""
        class CustomError(Exception):
            pass

        test_exception = CustomError("Custom error message")
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.exception(test_exception)
            mock_log.assert_called_once_with(logging.ERROR, "Custom error message")


class TestFatalFunction:
    """Test the fatal function."""

    def test_fatal_function_logs_and_prints_and_exits(self):
        """Test fatal function logs message, prints to stdout, and exits."""
        test_message = "Fatal error occurred"
        
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log, \
             patch('builtins.print') as mock_print, \
             patch.object(sys, 'exit') as mock_exit:
            
            logger.fatal(test_message)
            
            mock_log.assert_called_once_with(logging.FATAL, test_message)
            mock_print.assert_called_once_with(f"ERROR: {test_message}")
            mock_exit.assert_called_once_with(1)

    def test_fatal_function_with_different_message(self):
        """Test fatal function with different message."""
        test_message = "System shutdown required"
        
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log, \
             patch('builtins.print') as mock_print, \
             patch.object(sys, 'exit') as mock_exit:
            
            logger.fatal(test_message)
            
            mock_log.assert_called_once_with(logging.FATAL, test_message)
            mock_print.assert_called_once_with(f"ERROR: {test_message}")
            mock_exit.assert_called_once_with(1)


class TestSetLoggingLevel:
    """Test the set_logging_level function."""

    def test_set_logging_level_basic(self):
        """Test set_logging_level sets the logger level correctly."""
        with patch.object(logging.getLogger(metadata.name), 'setLevel') as mock_setLevel, \
             patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            
            logger.set_logging_level(logging.DEBUG)
            
            mock_setLevel.assert_called_once_with(logging.DEBUG)
            
            # Check info messages are logged
            mock_log.assert_any_call(logging.INFO, f"ipsdk version {metadata.version}")
            mock_log.assert_any_call(logging.INFO, f"Logging level set to {logging.DEBUG}")
            mock_log.assert_any_call(logging.INFO, "Logging propagation is False")

    def test_set_logging_level_with_propagate_false(self):
        """Test set_logging_level with propagate=False (default)."""
        with patch.object(logging.getLogger(metadata.name), 'setLevel') as mock_ipsdk_setLevel, \
             patch.object(logging.getLogger("httpx"), 'setLevel') as mock_httpx_setLevel, \
             patch.object(logging.getLogger("httpcore"), 'setLevel') as mock_httpcore_setLevel, \
             patch.object(logging.getLogger(metadata.name), 'log'):
            
            logger.set_logging_level(logging.INFO, propagate=False)
            
            mock_ipsdk_setLevel.assert_called_once_with(logging.INFO)
            mock_httpx_setLevel.assert_not_called()
            mock_httpcore_setLevel.assert_not_called()

    def test_set_logging_level_with_propagate_true(self):
        """Test set_logging_level with propagate=True."""
        with patch.object(logging.getLogger(metadata.name), 'setLevel') as mock_ipsdk_setLevel, \
             patch.object(logging.getLogger("httpx"), 'setLevel') as mock_httpx_setLevel, \
             patch.object(logging.getLogger("httpcore"), 'setLevel') as mock_httpcore_setLevel, \
             patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            
            logger.set_logging_level(logging.WARNING, propagate=True)
            
            mock_ipsdk_setLevel.assert_called_once_with(logging.WARNING)
            mock_httpx_setLevel.assert_called_once_with(logging.WARNING)
            mock_httpcore_setLevel.assert_called_once_with(logging.WARNING)
            
            # Check info messages include propagation set to True
            mock_log.assert_any_call(logging.INFO, f"ipsdk version {metadata.version}")
            mock_log.assert_any_call(logging.INFO, f"Logging level set to {logging.WARNING}")
            mock_log.assert_any_call(logging.INFO, "Logging propagation is True")

    def test_set_logging_level_different_levels(self):
        """Test set_logging_level with different logging levels."""
        test_levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
            logging.FATAL
        ]
        
        for level in test_levels:
            with patch.object(logging.getLogger(metadata.name), 'setLevel') as mock_setLevel, \
                 patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
                
                logger.set_logging_level(level)
                
                mock_setLevel.assert_called_once_with(level)
                
                # Check that the level is logged correctly
                mock_log.assert_any_call(logging.INFO, f"Logging level set to {level}")


class TestLoggingIntegration:
    """Integration tests for logging functionality."""

    def test_log_message_format(self):
        """Test that log message format is configured correctly."""
        # Since basicConfig has already been called, we just verify the expected format is documented
        expected_format = "%(asctime)s: %(levelname)s: %(message)s"
        
        # Import the format from logger module to ensure it's what we expect
        from ipsdk.logger import logging_message_format
        assert logging_message_format == expected_format

    def test_logger_hierarchy(self):
        """Test that the ipsdk logger is properly configured."""
        ipsdk_logger = logging.getLogger(metadata.name)
        assert ipsdk_logger is not None
        assert ipsdk_logger.name == metadata.name

    def test_partial_functions_are_functions(self):
        """Test that partial functions are callable."""
        partial_functions = [
            logger.debug,
            logger.info,
            logger.warning,
            logger.error,
            logger.critical
        ]
        
        for func in partial_functions:
            assert callable(func)
            # Test that they can be called without error (but don't actually log)
            with patch.object(logging.getLogger(metadata.name), 'log'):
                func("test message")


class TestErrorConditions:
    """Test error conditions and edge cases."""

    def test_log_with_empty_message(self):
        """Test logging with empty message."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.info("")
            mock_log.assert_called_once_with(logging.INFO, "")

    def test_log_with_none_message(self):
        """Test logging with None message (should convert to string)."""
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.info(None)
            mock_log.assert_called_once_with(logging.INFO, None)

    def test_exception_with_empty_exception_message(self):
        """Test exception function with exception that has empty message."""
        test_exception = ValueError("")
        with patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            logger.exception(test_exception)
            mock_log.assert_called_once_with(logging.ERROR, "")

    def test_set_logging_level_with_custom_level(self):
        """Test set_logging_level with custom numeric level."""
        custom_level = 25  # Between INFO (20) and WARNING (30)
        
        with patch.object(logging.getLogger(metadata.name), 'setLevel') as mock_setLevel, \
             patch.object(logging.getLogger(metadata.name), 'log') as mock_log:
            
            logger.set_logging_level(custom_level)
            
            mock_setLevel.assert_called_once_with(custom_level)
            
            mock_log.assert_any_call(logging.INFO, f"Logging level set to {custom_level}")