import sys
import unittest
from types import SimpleNamespace
from unittest import mock

sys.modules.setdefault("opendataloader_pdf", SimpleNamespace(convert=mock.Mock()))

import convert


class ConvertCliTests(unittest.TestCase):
    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_single_input_path_uses_string_argument(self, mock_convert, mock_backend):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(["file1.pdf"])

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            hybrid_fallback=True,
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_multiple_input_paths_use_list_argument(self, mock_convert, mock_backend):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(["file1.pdf", "files/"])

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path=["file1.pdf", "files/"],
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            hybrid_fallback=True,
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_optional_flags_override_defaults(self, mock_convert, mock_backend):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(
            ["file1.pdf", "--output-dir", "out", "--format", "json,markdown"]
        )

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="out",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            hybrid_fallback=True,
            format="json,markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_explicit_enrich_formula_keeps_default_behavior(
        self, mock_convert, mock_backend
    ):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(["file1.pdf", "--enrich-formula"])

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            hybrid_fallback=True,
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_no_enrich_formula_disables_formula_enrichment(
        self, mock_convert, mock_backend
    ):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(["file1.pdf", "--no-enrich-formula"])

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            hybrid_fallback=True,
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=False,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_hybrid_timeout_and_fallback_are_passed_through(
        self, mock_convert, mock_backend
    ):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(
            [
                "file1.pdf",
                "--hybrid-timeout",
                "60000",
                "--hybrid-fallback",
            ]
        )

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="60000",
            hybrid_fallback=True,
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.managed_backend")
    @mock.patch("convert.opendataloader_pdf.convert")
    def test_no_hybrid_fallback_disables_java_fallback(
        self, mock_convert, mock_backend
    ):
        mock_backend.return_value.__enter__.return_value = "http://127.0.0.1:9999"

        exit_code = convert.main(["file1.pdf", "--no-hybrid-fallback"])

        self.assertEqual(exit_code, 0)
        mock_convert.assert_called_once_with(
            input_path="file1.pdf",
            output_dir="./",
            hybrid="docling-fast",
            hybrid_mode="full",
            hybrid_url="http://127.0.0.1:9999",
            hybrid_timeout="180000",
            format="markdown",
        )
        mock_backend.assert_called_once_with(
            enrich_formula=True,
            startup_timeout=120.0,
        )

    @mock.patch("convert.urlopen")
    @mock.patch("convert.subprocess.Popen")
    @mock.patch("convert._backend_command", return_value=["backend", "--port", "5555"])
    @mock.patch("convert._find_free_port", return_value=5555)
    @mock.patch("convert.time.monotonic", side_effect=[0.0, 1.0])
    def test_managed_backend_starts_and_stops_process(
        self,
        _mock_monotonic,
        mock_find_free_port,
        mock_backend_command,
        mock_popen,
        mock_urlopen,
    ):
        process = mock.Mock()
        process.poll.side_effect = [None, None]
        process.returncode = None
        process.wait.return_value = None
        mock_popen.return_value = process

        response = mock.MagicMock()
        response.status = 200
        health_context = mock.MagicMock()
        health_context.__enter__.return_value = response
        mock_urlopen.return_value = health_context

        with convert.managed_backend(enrich_formula=True, startup_timeout=5.0) as url:
            self.assertEqual(url, "http://127.0.0.1:5555")

        mock_find_free_port.assert_called_once_with()
        mock_backend_command.assert_called_once_with(5555, True)
        mock_popen.assert_called_once_with(["backend", "--port", "5555"])
        mock_urlopen.assert_called_once_with("http://127.0.0.1:5555/health", timeout=1)
        process.terminate.assert_called_once_with()
        process.wait.assert_called_once_with(timeout=10)


if __name__ == "__main__":
    unittest.main()
