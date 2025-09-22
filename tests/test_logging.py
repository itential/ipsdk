# Copyright (c) 2025 Itential, Inc
# GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import logging
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from ipsdk import logging as ipsdk_logging
from ipsdk import metadata


class TestLoggingConstants:
    """Test logging constants and levels."""

    def test_logging_constants_exist(self):
        """Test that all logging constants are properly defined."""
        assert hasattr(ipsdk_logging, "NOTSET")
        assert hasattr(ipsdk_logging, "DEBUG")
        assert hasattr(ipsdk_logging, "INFO")
        assert hasattr(ipsdk_logging, "WARNING")
        assert hasattr(ipsdk_logging, "ERROR")
        assert hasattr(ipsdk_logging, "CRITICAL")
        assert hasattr(ipsdk_logging, "FATAL")

    def test_logging_constants_values(self):
        """Test that logging constants have correct values."""
        assert ipsdk_logging.NOTSET == logging.NOTSET
        assert ipsdk_logging.DEBUG == logging.DEBUG
        assert ipsdk_logging.INFO == logging.INFO
        assert ipsdk_logging.WARNING == logging.WARNING
        assert ipsdk_logging.ERROR == logging.ERROR
        assert ipsdk_logging.CRITICAL == logging.CRITICAL
        assert ipsdk_logging.FATAL == 90

    def test_fatal_level_registered(self):
        """Test that FATAL level is properly registered with logging module."""
        assert logging.getLevelName(90) == "FATAL"


class TestLogFunction:
    """Test the main log function."""

    def test_log_function_calls_logger(self):
        """Test that log function properly calls the logger."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.log(logging.INFO, "test message")

            mock_get_logger.assert_called_once_with(metadata.name)
            mock_logger.log.assert_called_once_with(logging.INFO, "test message")

    def test_log_function_different_levels(self):
        """Test log function with different logging levels."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            levels_and_messages = [
                (logging.DEBUG, "debug message"),
                (logging.INFO, "info message"),
                (logging.WARNING, "warning message"),
                (logging.ERROR, "error message"),
                (logging.CRITICAL, "critical message"),
                (ipsdk_logging.FATAL, "fatal message"),
            ]

            for level, message in levels_and_messages:
                ipsdk_logging.log(level, message)
                mock_logger.log.assert_called_with(level, message)


class TestConvenienceFunctions:
    """Test the convenience logging functions (debug, info, warning, etc.)."""

    def test_debug_function(self):
        """Test debug convenience function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.debug("debug message")
            mock_logger.log.assert_called_once_with(logging.DEBUG, "debug message")

    def test_info_function(self):
        """Test info convenience function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.info("info message")
            mock_logger.log.assert_called_once_with(logging.INFO, "info message")

    def test_warning_function(self):
        """Test warning convenience function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.warning("warning message")
            mock_logger.log.assert_called_once_with(logging.WARNING, "warning message")

    def test_error_function(self):
        """Test error convenience function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.error("error message")
            mock_logger.log.assert_called_once_with(logging.ERROR, "error message")

    def test_critical_function(self):
        """Test critical convenience function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.critical("critical message")
            mock_logger.log.assert_called_once_with(
                logging.CRITICAL, "critical message"
            )


class TestExceptionFunction:
    """Test the exception logging function."""

    def test_exception_function_with_exception(self):
        """Test exception function logs exception as error."""
        with patch("ipsdk.logging.log") as mock_log:
            test_exception = ValueError("test error")
            ipsdk_logging.exception(test_exception)
            mock_log.assert_called_once_with(logging.ERROR, "test error")

    def test_exception_function_with_different_exceptions(self):
        """Test exception function with different exception types."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            exceptions_to_test = [
                ValueError("value error"),
                TypeError("type error"),
                RuntimeError("runtime error"),
                KeyError("key error"),
            ]

            for exc in exceptions_to_test:
                ipsdk_logging.exception(exc)
                mock_logger.log.assert_called_with(logging.ERROR, str(exc))


class TestFatalFunction:
    """Test the fatal logging function."""

    def test_fatal_function_logs_and_exits(self):
        """Test that fatal function logs message and exits."""
        with patch("ipsdk.logging.log") as mock_log, \
             patch("builtins.print") as mock_print, \
             patch("sys.exit") as mock_exit:

            ipsdk_logging.fatal("fatal error")

            mock_log.assert_called_once_with(ipsdk_logging.FATAL, "fatal error")
            mock_print.assert_called_once_with("ERROR: fatal error")
            mock_exit.assert_called_once_with(1)

    def test_fatal_function_different_messages(self):
        """Test fatal function with different messages."""
        messages = ["critical failure", "system error", "cannot continue"]

        for message in messages:
            with patch("ipsdk.logging.log") as mock_log, \
                 patch("builtins.print") as mock_print, \
                 patch("sys.exit") as mock_exit:

                ipsdk_logging.fatal(message)

                mock_log.assert_called_once_with(ipsdk_logging.FATAL, message)
                mock_print.assert_called_once_with(f"ERROR: {message}")
                mock_exit.assert_called_once_with(1)


class TestGetLogger:
    """Test the get_logger function."""

    def test_get_logger_returns_correct_logger(self):
        """Test get_logger returns the correct logger instance."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            result = ipsdk_logging.get_logger()

            mock_get_logger.assert_called_once_with(metadata.name)
            assert result == mock_logger

    def test_get_logger_actual_logger(self):
        """Test get_logger returns actual Logger instance."""
        logger = ipsdk_logging.get_logger()
        assert isinstance(logger, logging.Logger)
        assert logger.name == metadata.name


class TestSetLevel:
    """Test the set_level function."""

    def test_set_level_basic(self):
        """Test set_level with basic parameters."""
        with patch("ipsdk.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.set_level(logging.INFO)

            mock_logger.setLevel.assert_called_once_with(logging.INFO)
            mock_logger.propagate = False
            assert mock_logger.log.call_count == 2  # Two log calls made

    def test_set_level_with_propagate(self):
        """Test set_level with propagate parameter."""
        with patch("ipsdk.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.set_level(logging.DEBUG, propagate=True)

            mock_logger.setLevel.assert_called_once_with(logging.DEBUG)
            mock_logger.propagate = False

    def test_set_level_different_levels(self):
        """Test set_level with different logging levels."""
        levels = [
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
            logging.CRITICAL,
        ]

        for level in levels:
            with patch("ipsdk.logging.get_logger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                ipsdk_logging.set_level(level)

                mock_logger.setLevel.assert_called_once_with(level)


class TestFileHandlers:
    """Test file handler related functions."""

    def test_add_file_handler_basic(self):
        """Test add_file_handler with basic parameters."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_logger.level = logging.INFO
                mock_get_logger.return_value = mock_logger

                with patch("ipsdk.logging.logging.FileHandler") as mock_file_handler:
                    mock_handler = Mock()
                    mock_file_handler.return_value = mock_handler

                    ipsdk_logging.add_file_handler(str(log_file))

                    mock_file_handler.assert_called_once_with(str(log_file))
                    mock_handler.setLevel.assert_called_once_with(logging.INFO)
                    mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_add_file_handler_with_custom_level(self):
        """Test add_file_handler with custom level."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_get_logger.return_value = mock_logger

                with patch("ipsdk.logging.logging.FileHandler") as mock_file_handler:
                    mock_handler = Mock()
                    mock_file_handler.return_value = mock_handler

                    ipsdk_logging.add_file_handler(str(log_file), level=logging.DEBUG)

                    mock_handler.setLevel.assert_called_once_with(logging.DEBUG)

    def test_add_file_handler_with_custom_format(self):
        """Test add_file_handler with custom format string."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"
            custom_format = "%(levelname)s - %(message)s"

            with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_logger.level = logging.INFO
                mock_get_logger.return_value = mock_logger

                with patch("ipsdk.logging.logging.FileHandler") as mock_file_handler:
                    mock_handler = Mock()
                    mock_file_handler.return_value = mock_handler

                    with patch(
                        "ipsdk.logging.logging.Formatter"
                    ) as mock_formatter_class:
                        mock_formatter = Mock()
                        mock_formatter_class.return_value = mock_formatter

                        ipsdk_logging.add_file_handler(
                            str(log_file), format_string=custom_format
                        )

                        mock_formatter_class.assert_called_once_with(custom_format)
                        mock_handler.setFormatter.assert_called_once_with(mock_formatter)

    def test_add_file_handler_creates_parent_directories(self):
        """Test add_file_handler creates parent directories."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "subdir" / "nested" / "test.log"

            with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
                mock_logger = Mock()
                mock_logger.level = logging.INFO
                mock_get_logger.return_value = mock_logger

                with patch("ipsdk.logging.logging.FileHandler") as mock_file_handler:
                    mock_handler = Mock()
                    mock_file_handler.return_value = mock_handler

                    ipsdk_logging.add_file_handler(str(log_file))

                    # Check that parent directories were created
                    assert log_file.parent.exists()

    def test_remove_file_handlers_no_handlers(self):
        """Test remove_file_handlers when no file handlers exist."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.remove_file_handlers()

            # Should not crash and should not call log since no handlers removed
            mock_logger.log.assert_not_called()

    def test_remove_file_handlers_with_handlers(self):
        """Test remove_file_handlers with existing file handlers."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_file_handler1 = Mock(spec=logging.FileHandler)
            mock_file_handler2 = Mock(spec=logging.FileHandler)
            mock_stream_handler = Mock(spec=logging.StreamHandler)

            mock_logger.handlers = [
                mock_file_handler1,
                mock_stream_handler,
                mock_file_handler2,
            ]
            mock_get_logger.return_value = mock_logger

            ipsdk_logging.remove_file_handlers()

            # Should remove only file handlers
            mock_logger.removeHandler.assert_any_call(mock_file_handler1)
            mock_logger.removeHandler.assert_any_call(mock_file_handler2)
            assert mock_logger.removeHandler.call_count == 2

            # Should close file handlers
            mock_file_handler1.close.assert_called_once()
            mock_file_handler2.close.assert_called_once()

            # Should log removal
            mock_logger.log.assert_called_once_with(
                logging.INFO, "Removed %d file handler(s)", 2
            )

    def test_configure_file_logging(self):
        """Test configure_file_logging function."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            with patch("ipsdk.logging.set_level") as mock_set_level, \
                 patch("ipsdk.logging.add_file_handler") as mock_add_file_handler:

                ipsdk_logging.configure_file_logging(
                    str(log_file), level=logging.DEBUG, propagate=True
                )

                mock_set_level.assert_called_once_with(logging.DEBUG, propagate=True)
                mock_add_file_handler.assert_called_once_with(
                    str(log_file), logging.DEBUG, None
                )


class TestConsoleHandlers:
    """Test console handler functions."""

    def test_set_console_output_stderr(self):
        """Test set_console_output with stderr."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                ipsdk_logging.set_console_output("stderr")

                mock_stream_handler.assert_called_once_with(sys.stderr)
                mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_set_console_output_stdout(self):
        """Test set_console_output with stdout."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.handlers = []
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                ipsdk_logging.set_console_output("stdout")

                mock_stream_handler.assert_called_once_with(sys.stdout)

    def test_set_console_output_invalid_stream(self):
        """Test set_console_output with invalid stream raises ValueError."""
        with pytest.raises(ValueError, match="stream must be 'stdout' or 'stderr'"):
            ipsdk_logging.set_console_output("invalid")

    def test_set_console_output_removes_existing_handlers(self):
        """Test set_console_output removes existing console handlers."""
        # This test needs to use real handlers to pass isinstance checks
        real_logger = logging.getLogger("test_logger")
        real_console_handler1 = logging.StreamHandler(sys.stderr)
        real_console_handler2 = logging.StreamHandler(sys.stdout)
        mock_file_handler = Mock(spec=logging.FileHandler)

        # Add handlers to real logger
        real_logger.addHandler(real_console_handler1)
        real_logger.addHandler(mock_file_handler)
        real_logger.addHandler(real_console_handler2)

        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_get_logger.return_value = real_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_new_handler = Mock()
                mock_stream_handler.return_value = mock_new_handler

                initial_handler_count = len(real_logger.handlers)
                ipsdk_logging.set_console_output("stderr")

                # Should have removed 2 console handlers and added 1 new handler
                # So total handlers should be initial_count - 2 + 1
                final_handler_count = len(real_logger.handlers)
                assert final_handler_count == initial_handler_count - 2 + 1

    def test_add_stdout_handler(self):
        """Test add_stdout_handler function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.level = logging.INFO
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                ipsdk_logging.add_stdout_handler()

                mock_stream_handler.assert_called_once_with(sys.stdout)
                mock_handler.setLevel.assert_called_once_with(logging.INFO)
                mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_add_stdout_handler_with_custom_level(self):
        """Test add_stdout_handler with custom level."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                ipsdk_logging.add_stdout_handler(level=logging.DEBUG)

                mock_handler.setLevel.assert_called_once_with(logging.DEBUG)

    def test_add_stderr_handler(self):
        """Test add_stderr_handler function."""
        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.level = logging.INFO
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                ipsdk_logging.add_stderr_handler()

                mock_stream_handler.assert_called_once_with(sys.stderr)
                mock_handler.setLevel.assert_called_once_with(logging.INFO)
                mock_logger.addHandler.assert_called_once_with(mock_handler)

    def test_add_stderr_handler_with_custom_format(self):
        """Test add_stderr_handler with custom format string."""
        custom_format = "%(levelname)s: %(message)s"

        with patch("ipsdk.logging.logging.getLogger") as mock_get_logger:
            mock_logger = Mock()
            mock_logger.level = logging.INFO
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                with patch("ipsdk.logging.logging.Formatter") as mock_formatter_class:
                    mock_formatter = Mock()
                    mock_formatter_class.return_value = mock_formatter

                    ipsdk_logging.add_stderr_handler(format_string=custom_format)

                    mock_formatter_class.assert_called_once_with(custom_format)
                    mock_handler.setFormatter.assert_called_once_with(mock_formatter)


class TestInitialize:
    """Test the initialize function."""

    def test_initialize_function(self):
        """Test initialize function sets up logging correctly."""
        with patch("ipsdk.logging.get_logger") as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            with patch("ipsdk.logging.logging.StreamHandler") as mock_stream_handler:
                mock_handler = Mock()
                mock_stream_handler.return_value = mock_handler

                with patch("ipsdk.logging.logging.Formatter") as mock_formatter_class:
                    mock_formatter = Mock()
                    mock_formatter_class.return_value = mock_formatter

                    ipsdk_logging.initialize()

                    mock_stream_handler.assert_called_once_with(sys.stderr)
                    mock_formatter_class.assert_called_once_with(ipsdk_logging.logging_message_format)
                    mock_handler.setFormatter.assert_called_once_with(mock_formatter)
                    mock_logger.addHandler.assert_called_once_with(mock_handler)
                    mock_logger.setLevel.assert_called_once_with(100)
                    assert mock_logger.propagate is False


class TestIntegration:
    """Integration tests using actual logging functionality."""

    def test_actual_logging_output(self, caplog):
        """Test actual logging output using caplog fixture."""
        # Set up actual logging
        logger = ipsdk_logging.get_logger()
        logger.setLevel(logging.DEBUG)
        logger.propagate = True  # Enable propagation so caplog can capture messages

        with caplog.at_level(logging.DEBUG, logger=metadata.name):
            # Test different log levels
            ipsdk_logging.debug("debug message")
            ipsdk_logging.info("info message")
            ipsdk_logging.warning("warning message")
            ipsdk_logging.error("error message")
            ipsdk_logging.critical("critical message")

        # Check that messages were logged
        messages = [record.getMessage() for record in caplog.records]
        assert any("debug message" in msg for msg in messages)
        assert any("info message" in msg for msg in messages)
        assert any("warning message" in msg for msg in messages)
        assert any("error message" in msg for msg in messages)
        assert any("critical message" in msg for msg in messages)

    def test_actual_file_logging(self):
        """Test actual file logging functionality."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            # Configure file logging
            ipsdk_logging.configure_file_logging(str(log_file), level=logging.INFO)

            # Log some messages
            ipsdk_logging.info("test info message")
            ipsdk_logging.error("test error message")

            # Clean up handlers to flush logs
            ipsdk_logging.remove_file_handlers()

            # Check that log file was created and contains messages
            assert log_file.exists()
            log_content = log_file.read_text()
            assert "test info message" in log_content
            assert "test error message" in log_content


class TestFormatString:
    """Test the logging message format string."""

    def test_logging_message_format_exists(self):
        """Test that logging_message_format is properly defined."""
        assert hasattr(ipsdk_logging, "logging_message_format")
        assert isinstance(ipsdk_logging.logging_message_format, str)
        assert "%(asctime)s" in ipsdk_logging.logging_message_format
        assert "%(name)s" in ipsdk_logging.logging_message_format
        assert "%(levelname)s" in ipsdk_logging.logging_message_format
        assert "%(message)s" in ipsdk_logging.logging_message_format

